# V2.3.0 Upgrade Features: pg_unlock Usage Instructions

## 1. Install the pg_unlock Tool:
Connect to any primary CN:

```
CREATE EXTENSION pg_unlock;
```

## 2. Construct a Distributed Deadlock Scenario

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

## 3. Identify Transaction Dependencies (Without Deadlock Detection)

session3—cn1:

```
postgres=# select * from pg_unlock_check_dependency();
dependencyid |      dependency       |    nodename     |              query              
--------------+-----------------------+-----------------+---------------------------------
            0 | 0:1998:5 --> 1:1995:1 | cn001 --> cn002 | drop table b; --> drop table a;
            1 | 1:1995:1 --> 0:1998:5 | cn002 --> cn001 | drop table a; --> drop table b;
(2 rows)
```
The above scenario shows transactional dependencies between transactions, where `dependencyid` indicates the record number and `dependency` displays the waiting relationship between transactions using their global transaction IDs. "0:1998:5 --> 1:1995:1" signifies that transaction "1998:5" is waiting for transaction "1995:1".

## 4. Detect Deadlocks in the Cluster (Without Resolving Them)

```
postgres=# select * from pg_unlock_check_deadlock();
deadlockid |                   deadlocks                   | nodename |     query     
------------+-----------------------------------------------+----------+---------------
          0 | 0:1998:5       (100.105.50.198 :30004       )+| cn001   +| drop table b;+
            | 1:1995:1       (100.105.50.198 :30005       ) | cn002    | drop table a;
(1 row)
```
This example shows all existing deadlocks in the cluster. The `deadlockid` represents the deadlock record count, while `deadlocks` presents all transactions involved in each deadlock, connected by "+" signs. It also prints out the IP and port of the node where each transaction originated.

## 5. Detect and Resolve Deadlocks

```
postgres=# select * from pg_unlock_execute();
executetime | txnindex |                  rollbacktxnifo                  | nodename | cancel_query  
-------------+----------+--------------------------------------------------+----------+---------------
           0 |        0 | 0:1998:5       (100.105.50.198 :30004          ) | cn001    | drop table b;
(1 row)
```
This illustrates the transaction rolled back to resolve the deadlock. The `executetime` indicates the number of times a transaction was ended to resolve deadlocks; if there are new deadlocks formed or more than 50 deadlocks detected initially, only some may be resolved in the first execution. The `txnindex` denotes the index of the transaction being terminated; the `rollbacktxninfo` provides information about the terminated transaction, including its global transaction ID, IP address, and port.

## 6. Analysis Process

1) In this example, transaction "1998:5" is initiated on CN1, and transaction "1995:1" is started on CN2.
   
2) Initially, both sessions execute "select" statements, causing transaction "1998:5" to acquire an ACCESS SHARE lock on table a, and transaction "1995:1" acquires an ACCESS SHARE lock on table b.

3) Subsequently, when both sessions attempt to execute "drop table" commands, transaction "1998:5" requests an ACCESS EXCLUSIVE lock on table b, which conflicts with the ACCESS SHARE lock held by transaction "1995:1". Thus, a "1998:5 --> 1995:1" dependency is created. Similarly, there's a reciprocal dependency "1995:1 --> 1998:5".

4) At this point, a deadlock situation arises between the two transactions. Upon detection of the deadlock, the tool terminates transaction "1998:5". In summary, the pg_unlock tool offers a means to identify and resolve deadlock situations in distributed database environments, ensuring smooth operation of database transactions.
