# V2.3.0 upgrade feature pg_clean usage instructions

## 1. Install the pg_clean tool：
Connect to any main CN：

```
CREATE EXTENSION pg_clean;
```

## 2. Two-Phase Transaction Case：  
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

## 3. Find remnants of two-phase transactions in a cluster：
session2—cn2  

```
select * from pg_clean_check_txn();
```
![pg_clean_check_txn](images/v.2.3.0_pg_clean_check_txn.png)
 
The above figure prints out the remaining two-phase transactions in the cluster. Among them, gid represents the global identifier of the transaction, global\_transaction\_status represents the global status of the transaction, and transaction\_status\_on\_allnodes represents the status of the transaction in all nodes.

## 4. View 2PC residual file names

Query all 2PC residual file names under the data directory pg_2pc in node cn1

session1—cn1 

```
	postgres=# select * from pgxc_get_record_list();
	 pgxc_get_record_list 
	----------------------
	 create_a
	(1 row)
```

## 5. Clean up the remnants of two-phase transactions in the cluster：
session2—cn2

```
select * from pg_clean_execute();
```
![pg_clean_execute](images/v2.3.0_pg_clean_execute.png)
 
The above image prints all remaining two-phase transactions, and the operations performed on them. Where operation represents the operation performed on each node of the transaction, and operation\_status represents whether the operation was successfully executed. Since the global transaction status of the transaction is ABORT, we go to each node with the prepare status to perform a rollback operation on the transaction.

## 6. Check whether the cleaned two-phase transaction has any remaining file records：
session1—cn1

```
	postgres=# select * from pgxc_get_record_list();
	 pgxc_get_record_list 
	----------------------
 
	(1 row)
```
 
Since pg\_clean\_execute was successfully executed in the previous step, the file records of the rolled back transaction 'create_a' on all nodes have been deleted. Here we view all 2pc file records in cn1, which is displayed as empty and the result is correct.