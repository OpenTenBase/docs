# V2.3.0 Upgrade Features pg_clean Usage Instructions

## 1. Installing the pg_clean Tool:
Connect to any primary CN:

```
CREATE EXTENSION pg_clean;
```

## 2. Creating a Two-Phase Commit Transaction Residue Example:
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
In this use case, we create a two-phase transaction with gid 'create\_a', and then turn on xc\_maintenance\_mode so that the transaction only executes rollback in dn002.

## 3. Finding Two-Phase Commit Transaction Residues in the Cluster:
session2—cn2 

```
select * from pg_clean_check_txn();
```
![pg_clean_check_txn](images/v.2.3.0_pg_clean_check_txn.png)

The above figure prints out the residual two-phase transactions in the cluster. Among them, gid represents the global identifier of the transaction, global\_transaction\_status represents the global status of the transaction, and transaction\_status\_on\_allnodes represents the status of the transaction in all nodes.

## 4. Viewing Names of 2PC Residual Files
Query the names of all residual 2PC files under the data directory `pg_2pc` on node cn1

Session1—cn1 

```
postgres=# select * from pgxc_get_record_list();
 pgxc_get_record_list 
----------------------
 create_a
(1 row)
```

## 5. Cleaning Up Residual Two-Phase Commit Transactions in the Cluster:
session2—cn2

```
select * from pg_clean_execute();
```
![pg_clean_execute](images/v2.3.0_pg_clean_execute.png)

The above image prints all residual two-phase transactions, and the operations performed on them. Where operation represents the operation performed on each node of the transaction, and operation\_status represents whether the operation was successfully executed. Since the global transaction status of the transaction is ABORT, we go to each node with the prepare status to perform a rollback operation on the transaction.

## 6. Checking if Resolved Two-Phase Commit Transactions Still Have File Records

Session1—cn1 

```
    postgres=# select * from pgxc_get_record_list();
     pgxc_get_record_list 
    ----------------------

    (1 row)

```

Since pg\_clean\_execute was successfully executed in the previous step, the file records of the rolled back transaction 'create_a' on all nodes have been deleted. Here we view all 2pc file records in cn1, which is displayed as empty and the result is correct.