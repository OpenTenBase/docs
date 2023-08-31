# V2.3.0升级特性pg_clean使用说明

## 1. 安装 pg_clean 工具：
连接任意主CN：

```
CREATE EXTENSION pg_clean;
```

## 2. 构造两阶段事务残留用例：  
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

该用例中我们创建了一个gid为 'create\_a' 的两阶段事务，然后将 xc\_maintenance\_mode 打开，使得该事务仅在dn002中执行rollback。

## 3. 查找集群中两阶段事务残留：
session2—cn2  

```
select * from pg_clean_check_txn();
```
![pg_clean_check_txn](images/v.2.3.0_pg_clean_check_txn.png)
 
上图打印出了集群中残留的两阶段事务。其中gid表示该事务的全局标识，global\_transaction\_status表示该事务在全局的状态，transaction\_status\_on\_allnodes表示该事务在所有节点中的状态。

## 4. 查看2PC残留文件名

查询节点cn1中数据目录pg_2pc下所有的2PC残留文件名  

session1—cn1 

```
	postgres=# select * from pgxc_get_record_list();
	 pgxc_get_record_list 
	----------------------
	 create_a
	(1 row)
```

## 5. 清理集群中两阶段事务残留：
session2—cn2

```
select * from pg_clean_execute();
```
![pg_clean_execute](images/v2.3.0_pg_clean_execute.png)
 
上图打印了所有残留的两阶段事务，以及对它们执行的操作。其中operation表示对事务在每个节点执行的操作，operation\_status表示该操作是否执行成功。由于该事务的全局事务状态为ABORT因此，我们去到每个状态为prepare的节点中对该事务执行rollback操作。

## 6. 检查已清理的两阶段事务是否残留文件记录：
session1—cn1

```
	postgres=# select * from pgxc_get_record_list();
	 pgxc_get_record_list 
	----------------------
 
	(1 row)
```
 
由于在上个步骤pg\_clean\_execute执行成功，因此已经回滚的事务'create_a'在所有节点的文件记录均已删除，这里我们在cn1查看所有2pc文件记录，显示为空，结果正确。
