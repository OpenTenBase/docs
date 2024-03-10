**Upgrade Features of pg_clean V2.3.0 Usage Guide**

1. Install the pg_clean tool:
   Connect to any primary coordinator (CN):

   ```sql
   CREATE EXTENSION pg_clean;
   ```

2. Create a two-phase transaction residue case:
   Session 1—cn1

   ```sql
   begin;
   create table a (id int);
   prepare transaction 'create_a';
   set xc_maintenance_mode = on;
   execute direct on (dn002) 'rollback prepared ''create_a''';
   set xc_maintenance_mode = off;
   \q
   ```

   In this case, a two-phase transaction with a GID of 'create_a' is created. The `xc_maintenance_mode` is then turned on, allowing the transaction to execute a rollback only on dn002.

3. Find residual two-phase transactions in the cluster:
   Session 2—cn2

   ```sql
   select * from pg_clean_check_txn();
   ```

   The output displays residual two-phase transactions in the cluster. GID represents the global identifier of the transaction, global_transaction_status indicates the global status of the transaction, and transaction_status_on_allnodes indicates the status of the transaction on all nodes.

4. View 2PC residue file names:
   Query all 2PC residue file names in the data directory pg_2pc on node cn1:

   Session 1—cn1

   ```sql
   select * from pgxc_get_record_list();
   ```

   The result will show the 'create_a' transaction.

5. Clean up residual two-phase transactions in the cluster:
   Session 2—cn2

   ```sql
   select * from pg_clean_execute();
   ```

   The output displays all residual two-phase transactions and the operations performed on them. The operation column indicates the operation performed on the transaction on each node, and operation_status indicates whether the operation was successful. Since the global transaction status is ABORT, a rollback operation is performed on each node with a prepare status.

6. Check if the cleaned two-phase transactions still have residual file records:
   Session 1—cn1

   ```sql
   select * from pgxc_get_record_list();
   ```

After the successful execution of pg_clean_execute in the previous step, the 'create_a' transaction, which has been rolled back, should have no file records on all nodes. The result should be empty, confirming the correct outcome.
