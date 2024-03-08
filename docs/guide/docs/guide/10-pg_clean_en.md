
# V2.3.0 Upgrade Features pg_clean Instructions for use
## 1. Install the pg_clean utility:
Connect to any main CN:
```
CREATE EXTENSION pg_clean;
```
## 2. Construct two-phase transaction residual use cases:
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
In this use case we create a two-phase transaction with a gid of 'create_a' and then turn xc_maintenance_mode on so that the transaction only performs a rollback in dn002.
## 3. Find two-phase transaction residuals in the cluster:
session2—cn2
```
select * from pg_clean_check_txn();
```
![image](https://github.com/ztword/docs/assets/35316898/19104658-1850-4ac5-a1ca-963a625b5fac)

The above figure prints out the two-phase transaction remaining in the cluster. Where gid denotes the global identifier of the transaction, global_transaction_status denotes the status of the transaction globally, and transaction_status_on_allnodes denotes the status of the transaction in all nodes.

## 4. View 2PC residual file names
Query all 2PC residual file names under the data directory pg_2pc in node cn1

session1-cn1 session 1 - cn1
```
	postgres=# select * from pgxc_get_record_list();
	 pgxc_get_record_list 
	----------------------
	 create_a
	(1 row)
```
## 5. Clean up the residual two-phase transactions in the cluster:
session2-cn2 Session 2 - CN2
```
select * from pg_clean_execute();
```
![image](https://github.com/ztword/docs/assets/35316898/3a4f5971-6727-4077-ad1e-24e4d7d8b2f1)

The above figure prints all the residual two-phase transactions, and the operations performed on them. Where operation indicates the operation performed on the transaction at each node and operation_status indicates whether the operation was performed successfully or not. Since the global transaction status of the transaction is ABORT, we go to each node with a status of prepare and perform a rollback operation on the transaction.

## 6. Check for residual documentation of cleaned two-phase transactions:
session1-cn1 Session 1 - CN1
```
	postgres=# select * from pgxc_get_record_list();
	 pgxc_get_record_list 
	----------------------
 
	(1 row)
```
Since in the previous step pg_clean_execute was executed successfully, the file records of the transaction 'create_a' that has been rolled back in all the nodes have been deleted, here we are looking at all the 2pc file records in cn1 and it shows that it is empty and the result is correct.




