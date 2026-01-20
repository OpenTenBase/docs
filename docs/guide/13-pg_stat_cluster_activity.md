# **OpenTenbase 集群状态监控扩展模块pg_stat_cluster_activity详解**

## **安装 OpenTenbase 集群状态监控扩展模块**

连接到 OpenTenbase 数据库的节点：

```sql
CREATE EXTENSION pg_stat_cluster_activity;
```

此命令会安装 `pg_stat_cluster_activity` 扩展，该扩展提供集群级别的监控功能，能够详细展示集群中各节点的查询和事务状态。

## 背景介绍

OpenTenbase作为一个分布式数据库，执行查询时需要多个协调节点（CN）和数据节点（DN）交互，复杂查询可能涉及多层调用。这种架构下，CN和DN之间存在生产者和消费者的依赖关系，可能导致死锁、程序挂起、节点报错等问题。在缺乏有效的定位工具时，这些问题难以快速解决。本文介绍的全局视图工具，是解决这些问题的有力工具，适用于以下场景：

- 定位问题查询所在的CN节点
- 通过错误ID定位对应的DN节点
- 定位出现进程挂起的问题节点

## 总体介绍

OpenTenbase 在运行过程中，多个节点的参与使得问题定位复杂。全局视图通过内部消息，将所有节点的运行信息统一展示，用户可以通过不同的过滤条件来精确定位问题。全局视图 `pg_stat_cluster_activity` 提供了每个服务器进程的详细描述，包括关联的用户会话和查询信息，极大地方便了SQL任务的问题分析和排查。

## 全局视图表介绍

`pg_stat_cluster_activity` 视图包含多个重要字段，每个字段都是分析问题不可或缺的信息源：

- `sessionid`: 全局会话标识，用于识别不同会话。
- `queryid`: 查询标识，相同的查询在不同的CN和DN上会有相同的queryid。
- `nodename`: 执行查询的节点名称。
- `datname`: 数据库名。
- `pid`: 进程ID，用于进程级的问题分析。
- `query`: 正在执行的查询文本。
- `state`: 查询的状态，如活跃、挂起等。
- `wait_event_type`: 等待事件类型，用于分析进程等待的资源类型。
- `wait_event`: 具体的等待事件，描述进程正在等待的具体资源。

## 注意事项

在使用全局视图时，需要注意以下几点：

1. 全局视图修改了内存表列和系统视图，因此必须在每个节点的 `postgresql.conf` 中进行配置修改后重启集群，扩展才能生效。
2. 只有超级用户（superuser）或进程的拥有者才能查询 `pg_stat_activity` 视图。

## 使用场景

### 查看连接信息

通过以下SQL查询可以确认当前的连接用户和对应的连接机器：

```sql
SELECT datname, usename, client_addr, client_port
FROM pg_stat_cluster_activity
WHERE client_addr IS NOT NULL;
```

### 查看SQL运行信息

获取当前用户执行的SQL信息：

```sql
SELECT queryid, nodename, datname, pid, query
FROM pg_stat_cluster_activity
WHERE query <> ''
ORDER BY queryid, nodename;
```

### 查看耗时较长的查询

查找当前运行中耗时较长的SQL语句：

```sql
SELECT current_timestamp - query_start AS runtime, queryid, nodename, datname, state, query
FROM pg_stat_cluster_activity
WHERE state != 'idle' AND query <> ''
ORDER BY runtime DESC;
```

### Query执行过程中挂起的问题定位

定位执行过程中挂起的Query的问题节点：

```sql
SELECT queryid, nodename, datid AS datid, datname AS datname, pid, wait_event_type, wait_event, wait_event_info, local_fid, state, query
FROM pg_stat_cluster_activity
WHERE

 queryid = (
    SELECT queryid
    FROM pg_stat_cluster_activity
    WHERE pid= ?  -- 替换 `?` 为挂起Query的PID
);
```

例如输出可能包括：

- CN节点等待数据的事件类型，如果 `wait_event_type` 为 FN，表明在等待网络数据。
- DN节点的 `local_fid` 是40，且没有等待事件，可能指示该DN节点为问题源。
- 另一DN节点的等待事件为 `ClientRead`，表明它在正常等待新的命令，因此是正常节点。

通过上述工具和方法，用户可以有效地利用OpenTenbase全局视图来监控和诊断分布式数据库中的各种问题。