# 分片表索引优化实践

<!-- Copyright (c) 2026 taisun820-dotcom. SPDX-License-Identifier: MIT -->

本案例比较客户等值查询、客户与日期范围查询、状态汇总三种访问需求，说明如何结合 CN 耗时与 DN 局部执行计划选择索引。

验证版本为 OpenTenBase V5.21（PostgreSQL 10.0 分支），数据规模为 50 万行。

## 案例问题与主要发现

在订单表中，按客户编号查询少量订单，以及按状态汇总大部分订单，是两类不同的访问需求。本案例在按订单编号分片的表上比较客户单列索引、客户日期复合索引和状态索引，结合 CN 请求耗时与 DN 局部计划判断优化效果。

客户查询的中位数由 49.624 ms 降至 1.057 ms；客户与日期查询由 54.565 ms 降至 1.132 ms。命中 80% 数据的状态汇总在已有状态索引时仍选择顺序扫描。

| 索引方案 | 客户查询 ms | 客户日期查询 ms | 状态汇总 ms |
| --- | --- | --- | --- |
| 无二级索引 | 49.624 | 54.565 | 91.163 |
| 客户单列索引 | 1.057 | 1.090 | 90.629 |
| 客户日期复合索引 | 0.997 | 1.132 | 87.883 |
| 复合与状态索引 | 0.906 | 0.976 | 88.673 |

每阶段每条查询预热 2 次、正式测量 9 次，表中采用正式样本的中位数。计时来自实际 SELECT 的 psql 输出，EXPLAIN ANALYZE 单独采集。

## 环境与数据分布

| 项目 | 本次实验配置 |
| --- | --- |
| 数据库 | OpenTenBase V5.21，基于 PostgreSQL 10.0 |
| 集群 | 1 个主 CN、2 个主 DN，另配主备实例 |
| 分片键 | id；客户条件需要访问两个 DN |
| 分片行数 | dn0001 为 250080 行，dn0002 为 249920 行 |
| 成本与内存 | seq_page_cost 1；random_page_cost 4；work_mem 4 MB |

本案例数据按固定公式生成。customer_id 共有 10000 个取值，paid 状态占 80%，订单金额与日期可以独立重新计算。

## 建表造数与查询

复现时连接 CN，在新的 Schema 中建立实验表。下面使用 otb_index_case 作为 Schema 名称，并通过 search_path 简化后续 SQL。

```sql
CREATE SCHEMA otb_index_case;
SET search_path = otb_index_case;
CREATE TABLE orders (
  id bigint PRIMARY KEY,
  customer_id integer NOT NULL,
  order_date date NOT NULL,
  status varchar(10) NOT NULL,
  amount numeric(12,2) NOT NULL,
  memo text NOT NULL
) DISTRIBUTE BY SHARD (id);
INSERT INTO orders
SELECT g, (g % 10000 + 1)::integer,
  DATE '2025-01-01' + ((g * 37 + g / 10000) % 365)::integer,
  CASE WHEN g % 10 < 8 THEN 'paid' ELSE 'pending' END,
  (g % 100000)::numeric / 100,
  repeat(md5(g::text), 3)
FROM generate_series(1, 500000) AS g;
ANALYZE orders;
```

Q1 返回客户 4243 的 50 笔订单。Q2 增加 2025 年 6 月的日期范围，返回 5 行。Q3 返回 paid 订单的数量与金额，总计 400000 笔、199994000.00。

```sql
-- Q1
SELECT id, customer_id, order_date, amount
FROM orders WHERE customer_id = 4243;
-- Q2
SELECT id, customer_id, order_date, amount
FROM orders
WHERE customer_id = 4243
  AND order_date >= DATE '2025-06-01'
  AND order_date < DATE '2025-07-01';
-- Q3
SELECT count(*), sum(amount)
FROM orders WHERE status = 'paid';
```

查询结果可由造数公式独立验证：Q1 的 id 从 4242 开始，每次增加 10000；Q2 在这些 id 中按同一日期公式筛选。Q3 对 g % 10 < 8 的行累加数量与金额。

## 索引方案与测量步骤

先记录仅有主键索引的基线。随后依次建立客户单列索引、替换为客户日期复合索引，最后增加状态索引。每个阶段完成 ANALYZE 后，预热并测量三条查询，再进入下一阶段。

```sql
-- B: customer index
CREATE INDEX idx_customer ON orders(customer_id);
ANALYZE orders;

-- C: replace customer index with composite index
DROP INDEX idx_customer;
CREATE INDEX idx_customer_date
  ON orders(customer_id, order_date);
ANALYZE orders;

-- D: retain composite index and add status index
CREATE INDEX idx_status ON orders(status);
ANALYZE orders;
```

正式实验每阶段执行 9 轮，每轮包含 Q1、Q2、Q3，轮内顺序使用种子 20261016 打乱。全部正式样本共 108 个。计时期间保持同一 CN 连接，汇总中位数并保留最小值与最大值。

psql 使用下列开关记录查询耗时。每条查询的前两次执行用于预热，后续九次作为正式样本。

```psql
\timing on
SELECT id, customer_id, order_date, amount
FROM otb_index_case.orders WHERE customer_id = 4243;
```

## 执行计划采集

在 CN 上保存业务入口的计划。当前版本的 CN JSON 计划未完整展开 DN 扫描细节，因此还需直接连接两个 DN，采集相同 SQL 的局部解释计划。

```sql
EXPLAIN (ANALYZE, VERBOSE, BUFFERS, FORMAT JSON)
SELECT id, customer_id, order_date, amount
FROM otb_index_case.orders
WHERE customer_id = 4243;
```

当前 V5 版本拒绝在 EXECUTE DIRECT 中执行 EXPLAIN，局部计划通过 psql 直连 DN 获取。节点名称、地址和端口可由 pgxc_node 查询。直连后的 SQL 使用 Schema 全限定名称。

```psql
SELECT node_name, node_type, node_host, node_port
FROM pgxc_node ORDER BY node_name;
\connect postgres opentenbase DN_HOST DN_PORT
```

EXPLAIN ANALYZE 的时间单独保存。DN 局部耗时用于解释局部执行，CN 的正式 SELECT 耗时用于比较用户请求延迟。两者分别统计。

完成 DN 局部计划采集后，重新连接 CN 再进入下一索引阶段。切换连接后使用 Schema 全限定名称，或重新执行 `SET search_path = otb_index_case;`。

## 等值过滤与日期范围的访问路径

无二级索引时，两个 DN 通过顺序扫描查找客户订单；加入客户索引后，Q1 使用 Bitmap Heap Scan 与 Bitmap Index Scan。Q1 的基线样本范围为 47.085 至 58.338 ms，单列索引后为 0.905 至 1.259 ms。

对于 Q2，单列索引先找出该客户的候选行，再用日期 Filter 筛选。复合索引将客户等值条件与日期范围同时放入 Index Cond。各 DN 独立采集的计划字段如下。

| 节点与方案 | 访问路径 | 返回行数 | 命中缓冲块 |
| --- | --- | --- | --- |
| DN1 单列索引 | Bitmap Heap Scan | 3 | 31 |
| DN1 复合索引 | Index Scan | 3 | 6 |
| DN2 单列索引 | Bitmap Heap Scan | 2 | 25 |
| DN2 复合索引 | Index Scan | 2 | 5 |

DN1 单列索引计划的关键字段

```text
Node Type: Bitmap Heap Scan
Recheck Cond: customer_id = 4243
Filter: order_date >= '2025-06-01' AND order_date < '2025-07-01'
Rows Removed by Filter: 25
Actual Rows: 3
Shared Hit Blocks: 31
```

DN1 复合索引计划的关键字段

```text
Node Type: Index Scan
Index Name: idx_customer_date
Index Cond: customer_id = 4243
  AND order_date >= '2025-06-01' AND order_date < '2025-07-01'
Actual Rows: 3
Shared Hit Blocks: 6
```

复合索引减少了日期范围查询的局部访问工作。customer_id 放在前面可先定位客户，再在该客户的数据中限定日期范围，同时也支持 Q1 的前缀条件。

Q2 的单列与复合索引中位数分别为 1.090 ms 和 1.132 ms，样本范围分别为 0.897 至 1.317 ms 与 0.875 至 1.369 ms。两组范围重叠，端到端延迟在本次测量中接近；局部缓冲块数则有明确减少。

## 高命中率查询与索引取舍

Q3 需要读取 paid 订单的 amount，命中 40 万行，占全表 80%。最后阶段两个 DN 上均已建立 idx_status，优化器仍选择并行顺序扫描。

| 方案 | Q3 中位数 ms | 正式样本范围 ms | 扫描方式 |
| --- | --- | --- | --- |
| 无二级索引 | 91.163 | 86.448 至 105.321 | Seq Scan |
| 复合索引 | 87.883 | 86.401 至 91.917 | Seq Scan |
| 复合与状态索引 | 88.673 | 86.734 至 92.971 | Seq Scan |

状态索引在两个 DN 上合计占用 11313152 字节，约 10.79 MiB。它没有被这条汇总查询采用，测量区间也没有显示明确的延迟收益。对大量行进行索引访问并读取 amount 的成本，需要与顺序扫描成本一起评估。

## 索引选择建议

按客户查少量订单时，先评估 customer_id 单列索引；业务经常同时限制日期范围时，再评估 customer_id 与 order_date 的复合索引。是否保留索引，应结合实际计划和重复计时，而不是只依据 WHERE 中是否出现该字段。

大比例状态汇总宜先检查扫描和聚合路径。新增状态索引会增加存储占用，其对其他查询和写入的影响需要分别测量。本案例未测量写入吞吐、并发争用或冷缓存性能。

## 结果验证与测量条件

所有预热和正式查询均与 Python 按造数公式独立计算的结果逐行核对，Q1、Q2 行集合及 Q3 汇总值在各阶段保持一致。两个 DN 的分片计数之和为 500000，CN 总行数同为 500000。

测量运行于同一物理机上的双虚拟机环境，采用串行热缓存负载，阶段按 DDL 顺序执行。轮内随机顺序与统一预热用于减小部分顺序影响，毫秒内的方案差异需结合样本区间解读。

## 参考资料

- [问题定位及性能优化](../09-problem-performance.md)
- [基本使用](../03-basic-use.md)
