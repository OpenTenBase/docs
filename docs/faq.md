# 常见问题

1.	强同步等待ack超过sqlasyntimeout（默认30s）后的错误提示

```sql
ERROR 1613 (XA106): The transaction is in doubt. Please check whether the transaction has been committed.
```

2.	大事务产生的binlog超过binlog_write_threshold（默认1610612736）后错误提示：

```sql
ERROR 4040 (HY000): binlog write threshold(xxx) exceeded, the transaction has xxx (bytes) binlogs, it is aborted.
```