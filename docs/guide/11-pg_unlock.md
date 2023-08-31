# V2.3.0升级特性pg_unlock使用说明

## 1. 安装 pg_unlock 工具：
连接任意主CN：

```
CREATE EXTENSION pg_unlock;
```

## 2. 构造分布式死锁用例

session1—cn1:

```
postgres=# begin; select * from a; 
```

session2—cn2:

```
postgres=# begin; select * from b; 
```
 

session1—cn1:

```
postgres=# drop table b;
```

session2—cn2:

```
postgres=# drop table a;
```

## 3. 查找事务间依赖关系(不检测死锁)

session3—cn1:

```
postgres=# select * from pg_unlock_check_dependency();
 dependencyid |      dependency       |    nodename     |              query              
--------------+-----------------------+-----------------+---------------------------------
            0 | 0:1998:5 --> 1:1995:1 | cn001 --> cn002 | drop table b; --> drop table a;
            1 | 1:1995:1 --> 0:1998:5 | cn002 --> cn001 | drop table a; --> drop table b;
(2 rows)

```

上述用例中的事务间等待关系。其中 dependencyid 表示记录数， dependency 中展示了事务间等待关系，其中每个事务使用其 global transactionid 来表示。"0:1998:5 --> 1:1995:1"表示记录0的事务"1998:5"等待记录1的事务"1995:1"。



## 4. 查找集群中的死锁(不解开死锁)

```
postgres=# select * from pg_unlock_check_deadlock();
 deadlockid |                   deadlocks                   | nodename |     query     
------------+-----------------------------------------------+----------+---------------
          0 | 0:1998:5       (100.105.50.198 :30004       )+| cn001   +| drop table b;+
            | 1:1995:1       (100.105.50.198 :30005       ) | cn002    | drop table a;
(1 row)

```
上述用例中存在的所有死锁。其中 deadlockid 表示死锁的记录数，deadlocks 中展示了每个死锁中包含的所有事务(这些事务之间由“+”号连接)，并且还打印出了每个事务的发起节点的 ip 和 port。


## 5. 检测死锁并解开死锁

```
postgres=# select * from pg_unlock_execute();
 executetime | txnindex |                  rollbacktxnifo                  | nodename | cancel_query  
-------------+----------+--------------------------------------------------+----------+---------------
           0 |        0 | 0:1998:5       (100.105.50.198 :30004          ) | cn001    | drop table b;
(1 row)

```
上述用了解开死锁所结束的事务。其中 executetime 表示执行结束事务的次数，因为若集群中在第一次结束事务解开死锁之后，可能形成新的死锁或者第一次检测过程中死锁数目大于 50，只解开了部分死锁;txnindex 表示结束事务的记录数;rollbacktxninfo 表示结束事务的信息，同样这个信息里包括事务的 global transactionid， ip 和 port。

## 6. 分析过程

1）在上述用例中，在 CN1 中发起了事务“1998:5”，在 CN2 中发起了事务“1995:1”。   
2）首先，在两个 session 中执行“select”语句，事务“1998:5”获取了表 a 的 ACCESS
SHARE 锁，事务“1995:1”获取了表 b 的 ACCESS SHARE 锁。  
3）然后，两个 session 中分别执行“drop table”语句，事务“1998:5”申请表 b 的
ACCESS EXCLUSIVE 锁，这与“1995:1”持有的表 b 的 ACCESS SHARE 锁冲突，因此 “1998:5 --> 1995:1”。同理，也有“1995:1 --> 1998:5”。  
4) 至此两个事务间死锁形成。由上述可知，检测到死锁之后，程序结束了事务 “1998:5”。