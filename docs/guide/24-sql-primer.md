# SQL 入门手册：从建表到查询的三条语句

本文面向第一次接触 OpenTenBase 的读者，从仓库已有文档中选取 3 条最基础的 SQL 示例，按“建表 → 写入 → 查询”的顺序解释每一行在做什么、为什么这样写，并给出新手最常见的困惑点。

> **关于本文的验证方式**
>
> 本文示例均摘自 OpenTenBase 文档库，出处逐条标注。所有输出均为按文档说明推导的**预期结果**，本文作者未在集群上实际执行这些 SQL；如需真实验证，请参考[快速入门](01-quickstart.md)搭建实例。

## 1、阅读顺序

| 顺序 | 语句类型 | 先解决什么问题 | 对应示例 |
| --- | --- | --- | --- |
| 第一步 | `CREATE TABLE` | 数据放在哪、怎么分布 | 示例一 |
| 第二步 | `INSERT` | 怎么把数据写进去 | 示例二 |
| 第三步 | `SELECT` | 怎么把数据查出来、走哪些节点 | 示例三 |

先建表再写入最后查询，是因为 OpenTenBase 是分布式数据库，表建好时就已经决定了数据分布方式，后续读写性能都受它影响。

## 2、示例一：建一张复制表

**来源**：[`docs/guide/03-basic-use.md`](https://github.com/OpenTenBase/docs/blob/main/docs/guide/03-basic-use.md) 的“1.3、创建复制表”一节，在线页面：[基本使用](https://docs.opentenbase.org/guide/03-basic-use/)。

```sql
create table public.t1_rep
(
    f1 int not null,
    f2 varchar(20),
    primary key(f1)
)
distribute by replication
to group default_group;
```

逐行解释：

| 代码 | 作用 |
| --- | --- |
| `create table public.t1_rep` | 在 `public` 模式下建表，表名 `t1_rep` |
| `f1 int not null` | 第一列，整型，不允许为空 |
| `f2 varchar(20)` | 第二列，最长 20 个字符的可变长字符串 |
| `primary key(f1)` | 主键是 `f1`，同时会创建主键索引 |
| `distribute by replication` | 复制表：每个 DN 节点都保存一份全量数据 |
| `to group default_group` | 放进默认存储组，即所有 DN 节点 |

**预期结果**：`CREATE TABLE`。

**为什么用复制表**：文档同一节给出的适用场景是“经常要跨库 JOIN 的小数据量表”；同时明确了两条约束——所有节点都有全量数据，因此不适合大数据表；复制表的更新性能较低。

## 3、示例二：一次插入两行

**来源**：同一文档的“2.1、INSERT”一节。

```sql
CREATE TABLE public.t1_insert_mul
(
    f1 int not null,
    f2 varchar(20),
    primary key(f1)
) distribute by shard(f1) to group default_group;

INSERT INTO t1_insert_mul VALUES (1,'opentenbase'),(2,'pg');
```

逐行解释：

| 代码 | 作用 |
| --- | --- |
| `distribute by shard(f1)` | 分片表，按 `f1` 的值计算哈希，决定这一行落到哪个 DN |
| `to group default_group` | 使用默认存储组（包含多个 DN 节点） |
| `INSERT INTO t1_insert_mul VALUES (...),(...)` | 一条语句插入两行，逗号分隔多个值组 |
| `(1,'opentenbase')`、`(2,'pg')` | 两行数据，列顺序与建表时一致 |

**预期结果**：`INSERT 0 2`（文档原文输出，属预期结果）。

**新手容易忽略的点**：因为是按 `f1` 分片，`f1 = 1` 和 `f1 = 2` 的两行很可能落在不同节点上，这是正常现象，不是“数据只写进去了一半”。

## 4、示例三：带分布键的查询

**来源**：同一文档的“2.4、SELECT”一节。

```sql
explain select * from t1_select where f1=1;
```

逐行解释：

| 代码 | 作用 |
| --- | --- |
| `explain` | 只显示执行计划，不真正返回数据行 |
| `select *` | 查询所有列 |
| `from t1_select` | 查询前面建好的分片表 |
| `where f1=1` | 条件命中分布键 `f1`，可以定位到单个 DN |

**预期结果**：执行计划中出现 `Node/s: dn001`，并在该节点上走 `Index Scan`（文档原文输出，属预期结果）。

**关键结论**：文档在同一节明确“基于分布键查询性能最优、扩展性好”；反过来，不命中分布键的条件会被发往所有节点，再在 CN 汇总。

## 5、把最难懂的一句讲清楚

原文档对建表语法的说明只有两句话：

> `distribute by shard(x) 用于指定分布键，数据分布于那个节点就是根据这个字段值来计算分片。`
>
> `to group xxx 用于指定存储组（每个存储组可以有多个节点）。`

新手读完仍然容易混淆三件事：分布键、存储组、主键。改进后的对照说明如下。

| 概念 | 一句话解释 | 在本例中 |
| --- | --- | --- |
| 分布键 | 决定某一行去哪个 DN 的字段 | `shard(f1)` 中的 `f1` |
| 存储组 | 一批 DN 的集合，表只在这些节点上分布 | `default_group` |
| 主键 | 保证这一行唯一，与数据分布是两件事 | `primary key(f1)` |

> **别把类比当技术事实**
>
> 可以把它想象成“按学号尾号分班（分布键）+ 只在这几栋教学楼里分（存储组）”，但类比只帮助建立直觉；实际分片规则是哈希计算，具体行为以文档和源码为准。

**改进前后对比**：

| 维度 | 原说明 | 改进后 |
| --- | --- | --- |
| 概念数量 | 一句话里塞了分布键、节点、存储组 | 拆成 3 行表格，一概念一行 |
| 主键是否参与分布 | 未提及 | 明确“主键与分布是两件事” |
| 可自查性 | 读完无法确认 | 每行都对应示例中的具体字段 |

## 6、小练习

1. 把示例一的复制表改成按 `f1` 分片的表，`distribute by` 那行应该怎么写？
   自查要点：应改为 `distribute by shard(f1)`，其余不变。
2. 执行示例二的插入后，`select count(*) from t1_insert_mul;` 的预期结果是多少？
   自查要点：插入 2 行，预期为 2。
3. 如果执行 `update t1_insert_mul set f1 = 3 where f1 = 1;` 会发生什么？
   自查要点：`f1` 是分布键，文档“2.2、UPDATE”明确分布键不能更新，会报 `Distributed column or partition column “f1” can't be updated in current version`。

## 7、逐项核对

| 解释条目 | 依据 | 核对结果 |
| --- | --- | --- |
| 复制表每节点全量、不适合大表、更新性能低 | 03-basic-use.md“1.3、创建复制表”说明段 | 一致 |
| `distribute by shard(f1)` 按字段值计算分片 | 03-basic-use.md“1.1、创建 shard 普通表”说明段 | 一致 |
| 复制表建表预期输出 `CREATE TABLE` | 03-basic-use.md“1.3”代码块 | 一致 |
| 多行插入预期输出 `INSERT 0 2` | 03-basic-use.md“2.1、INSERT”代码块 | 一致 |
| 分布键查询走单个 DN | 03-basic-use.md“2.4、SELECT”的 EXPLAIN 输出 | 一致 |
| 分布键不可更新 | 03-basic-use.md“2.2、UPDATE”报错示例 | 一致 |

> **试读反馈（待补）**
>
> 按任务要求需请另一组同学试读并记录一条反馈。当前记录模板如下，提交 PR 前需补齐：
>
> - 试读者：
> - 读完后用自己的话复述“分布键”：
> - 卡住的位置：
> - 建议：

## 8、参考

- [基本使用（文档源文件）](https://github.com/OpenTenBase/docs/blob/main/docs/guide/03-basic-use.md)
- [基本使用（在线页面）](https://docs.opentenbase.org/guide/03-basic-use/)
- [快速入门](01-quickstart.md)
- [应用接入](02-access.md)
