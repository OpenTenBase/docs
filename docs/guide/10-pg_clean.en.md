# V2.3.0 Upgrade Features: pg_clean Usage Instructions

## 1. Install the pg_clean Tool:
Connect to any primary CN:

```
CREATE EXTENSION pg_clean;
```

## 2. Construct a Two-Phase Transaction Residual Scenario:
session1—cn1

```
begin;
create table a (id int);
prepare transaction 'create_a';
set xc_maintenance_mode = on;
execute direct on (dn002) 'rollback prepared ''create_a''';
set xc_maintenance_mode = off;
\q
```

In this scenario we create a two-phase transaction whose gid is 'create\_a', and then turn on xc\_maintenance\_mode so that the transaction is rolled back only on dn002.

## 3. Find Residual Two-Phase Transactions in the Cluster:
session2—cn2

```
select * from pg_clean_check_txn();
```
![pg_clean_check_txn](images/v.2.3.0_pg_clean_check_txn.png)

The figure above prints out the residual two-phase transactions in the cluster. `gid` is the global identifier of the transaction, global\_transaction\_status is the global status of the transaction, and transaction\_status\_on\_allnodes is the status of the transaction on all nodes.

## 4. View the Names of the 2PC Residual Files

Query the names of all 2PC residual files under the `pg_2pc` data directory on node cn1

session1—cn1

```
postgres=# select * from pgxc_get_record_list();
 pgxc_get_record_list 
----------------------
 create_a
(1 row)
```

## 5. Clean Up Residual Two-Phase Transactions in the Cluster:
session2—cn2

```
select * from pg_clean_execute();
```
![pg_clean_execute](images/v2.3.0_pg_clean_execute.png)

The figure above prints out all residual two-phase transactions, as well as the operations performed on them. `operation` is the operation performed on the transaction on each node, and operation\_status indicates whether that operation was executed successfully. Because the global transaction status of this transaction is ABORT, we go to every node whose status is prepare and perform a rollback on the transaction there.

## 6. Check Whether the Cleaned Two-Phase Transactions Still Have Residual File Records:
session1—cn1

```
postgres=# select * from pgxc_get_record_list();
 pgxc_get_record_list 
----------------------
 
(1 row)
```

Because pg\_clean\_execute was executed successfully in the previous step, the file records of the already rolled back transaction 'create_a' have been deleted on all nodes. Here we check all 2pc file records on cn1, and they are displayed as empty — the result is correct.
