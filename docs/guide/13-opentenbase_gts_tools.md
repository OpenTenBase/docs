# opentenbase_gts_tools使用说明

## 1. 安装 OpenTenBase GTS Tools 扩展
首先，确保你有足够的权限来安装扩展。在PostgreSQL数据库的任意节点（CN）上执行以下命令来安装opentenbase_gts_tools扩展：

```
CREATE EXTENSION opentenbase_gts_tools;
```

## 2. 获取特定事务的提交时间戳
使用txid_gts函数来查询特定事务ID的提交时间戳。这个函数对于追踪事务提交时间或进行事务分析非常有用。如果事务已提交，函数将返回一个bigint类型的值，表示事务的提交时间戳。

```
SELECT txid_gts(your_transaction_id);
```

## 3. 获取堆页面上的元组信息（不包括数据）
当你需要获取堆页面上的元组信息，但不关心元组的实际数据内容时，可以使用heap_page_items_without_data函数。这个函数返回元组的位置、大小、关联的事务ID等信息, 此函数特别适用于分析页面结构或元组存储布局。

```
SELECT * FROM heap_page_items_without_data((SELECT pg_read_page('your_table'::regclass, 0)));
```

## 4. 获取并分析堆页面信息
使用heap_page_items_with_gts函数来获取和分析堆页面的详细信息。这个函数返回页面上每个项目的详细信息，包括项目的位置、大小、关联的事务ID和时间戳等。

```
SELECT * FROM heap_page_items_with_gts((SELECT pg_read_page('your_table'::regclass, 0)));
```

## 5. 日志输出分析
为了更详细地了解页面信息，可以使用heap_page_items_with_gts_log函数，它会输出额外的日志信息，有助于调试和深入分析。

```
SELECT * FROM heap_page_items_with_gts_log((SELECT pg_read_page('your_table'::regclass, 0)));
```

## 6. 获取仅ID的页面信息
如果只需要获取页面上元组的ID信息，可以使用heap_page_ids函数。这个函数返回了一个集合，其中只包含页面上每个元组的ID信息。

```
SELECT * FROM heap_page_ids((SELECT pg_read_page('your_table'::regclass, 0)));
```

通过这些功能，opentenbase_gts_tools扩展为数据库管理员和开发者提供了强大的分析和调试工具，帮助他们更好地理解和管理PostgreSQL数据库的内部结构和状态。