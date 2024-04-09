# Upgrade Features in V2.3.0: Instructions for Using pg_clean

## 1. Install the pg_clean tool:
Connect to any primary CN (Coordinate Node):

```
CREATE EXTENSION pg_clean;
```

## 2. Construct a test case for residual two-phase transactions:
Session 1 - CN1

```
begin; 
create table a (id int); 
prepare transaction 'create_a';
set xc_maintenance_mode = on;
execute direct on (dn002) 'rollback prepared ''create_a''';
set xc_maintenance_mode = off;
\q
```

In this test case, we created a two-phase transaction with a GID (Global Identifier) of 'create_a', then turned on xc_maintenance_mode, causing the transaction to only execute a rollback on dn002.

## 3. Find residual two-phase transactions in the cluster:
Session 2 - CN2

```
select * from pg_clean_check_txn();
```

![pg_clean_check_txn](images/v.2.3.0_pg_clean_check_txn.png)

The above image shows residual two-phase transactions in the cluster. The GID represents the global identifier of the transaction, global_transaction_status indicates the global status of the transaction, and transaction_status_on_allnodes shows the status of the transaction on all nodes.

## 4. Check 2PC residual filenames

Query all residual 2PC filenames in the pg_2pc directory of the data folder on node cn1.

Session 1 - CN1

```
postgres=# select * from pgxc_get_record_list();
 pgxc_get_record_list 
----------------------
create_a
(1 row)
```

## 5. Clean up residual two-phase transactions in the cluster:
Session 2 - CN2

```
select * from pg_clean_execute();
```

![pg_clean_execute](images/v2.3.0_pg_clean_execute.png)

The above image prints out all residual two-phase transactions and the operations executed on them. The operation column indicates the action performed on the transaction on each node, and operation_status indicates whether the operation was successful. Since the global transaction status of this transaction is ABORT, we go to each node with a status of prepare and execute a rollback operation on the transaction.

## 6. Check for residual file records of the cleaned two-phase transactions:
Session 1 - CN1

```
postgres=# select * from pgxc_get_record_list();
pgxc_get_record_list 
----------------------
```

Since the pg_clean_execute in the previous step was successful, the file records of the rolled-back transaction 'create_a' have been deleted from all nodes. Here we check on cn1 for all 2PC file records, which shows as empty, and the result is correct.
