# OpenTenbase 连接池统计监控扩展使用指南

## 背景介绍

OpenTenbase数据库在处理大量并发连接时，有效的连接池管理是确保性能和资源利用最优化的关键。在分布式环境下，理解各节点上连接池的状态对于诊断问题、优化资源分配及提高查询响应时间至关重要。本扩展提供了全面的连接池统计信息，帮助数据库管理员监控和分析连接池的健康状况。

## 总体介绍

此扩展包括以下主要功能：

1. **获取连接池命令统计** (`opentenbase_get_pooler_cmd_statistics`)：提供连接池命令处理的统计数据，包括请求次数、平均处理时间、最长和最短处理时间等。
2. **重置连接池命令统计** (`opentenbase_reset_pooler_cmd_statistics`)：重置连接池统计信息，便于进行新的性能基准测试。
3. **获取连接池连接统计** (`opentenbase_get_pooler_conn_statistics`)：展示每个数据库和用户在各节点上的连接详细信息，包括总连接数、空闲连接数等。

## 扩展的主要功能和视图字段

### `opentenbase_get_pooler_cmd_statistics`

此函数展示连接池处理各种命令的统计信息，字段包括：

- **command_type**：命令类型，如CONNECT、DISCONNECT等。
- **request_times**：该命令的请求次数。
- **avg_costtime**：平均处理时间（微秒）。
- **max_costtime**：最长处理时间（微秒）。
- **min_costtime**：最短处理时间（微秒）。

### `opentenbase_get_pooler_conn_statistics`

此函数提供各数据库和用户在各节点上的连接统计，字段包括：

- **database**：数据库名。
- **user_name**：用户名。
- **node_name**：节点名称。
- **oid**：节点的OID。
- **is_coord**：节点是否为协调节点。
- **conn_cnt**：总连接数。
- **free_cnt**：空闲连接数。
- **warming_cnt**：预热中的连接数。
- **query_cnt**：当前正在处理查询的连接数。
- **exceed_keepalive_cnt**：超过保活时间的连接数。
- **exceed_deadtime_cnt**：超过死亡时间的连接数（为兼容保留，未使用）。
- **exceed_maxlifetime_cnt**：超过最大生命周期的连接数。

## 安装和使用方法

### 安装扩展

在任意主控节点（CN）上执行以下命令安装此扩展：

```sql
CREATE EXTENSION opentenbase_pooler_stat;
```

### 使用示例

#### 获取连接池命令统计

```sql
SELECT * FROM opentenbase_get_pooler_cmd_statistics();
```

#### 重置连接池命令统计

```sql
SELECT opentenbase_reset_pooler_cmd_statistics();
```

#### 获取连接池连接统计

```sql
SELECT * FROM opentenbase_get_pooler_conn_statistics();
```

这些查询将返回连接池的详细统计信息，帮助数据库管理员识别潜在的瓶颈，优化连接池配置。

## 注意事项

1. 使用这些监控功能需要超级用户权限，因为它们可能访问敏感的系统操作数据。
2. 扩展安装后可能需要配置相应的PostgreSQL参数并重启数据库以确保新的配置生效。
3. 监控数据可以帮助进行故障

诊断和性能优化，但获取数据时可能会对系统性能产生轻微影响，请在非高峰时间进行相关监控活动。

通过以上工具和方法，OpenTenbase管理员可以有效地监控和优化数据库连接池的性能，确保数据库系统的高效稳定运行。