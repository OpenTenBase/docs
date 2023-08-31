# V2.3.0升级特性opentenbase_subscription使用说明

## 1. 修改wal_level

因为多活使用的是逻辑复制来实现，因此需要配置多活的所有集群中，所有CN/DN节点的 wal_level 全部设置为 logical

```
vim postgres.comf
wal_level = logical
:wq
```

## 2. 安装 opentenbase_subscription 工具：
连接配置多活的2个集群分别各自的CN（针对任意集群，选择任意一个CN执行即可，但是2个集群都需要安装）执行：

```
CREATE EXTENSION opentenbase_subscription;
```

## 3. 单向同步配置

这里以发布端1CN+2DN，订阅端1CN+2DN为例，其他集群规模配置步骤相似

### 3.1 连接发布端任意CN建表

```
postgres=# create table users(id int,name varchar(30),f3 int,PRIMARY KEY(id));
postgres=# insert into users select i, 'a', i+1 from generate_series(1, 399999) i;
INSERT 0 399999
```

### 3.2 在发布端 DN上进行数据发布

注意：如果有发布端集群有多个DN，则每个DN都需要进行配置发布 

发布端DN1:

```
CREATE PUBLICATION mypub_dn001 FOR ALL TABLES;
```

发布端DN2:

```
CREATE PUBLICATION mypub_dn002 FOR ALL TABLES;
```


### 3.3 在订阅端 CN上进行数据订阅
订阅端CN：

```
create table users(id int,name varchar(30),f3 int,PRIMARY KEY(id)) ;

CREATE OPENTENBASE SUBSCRIPTION sub_dn001 CONNECTION 'host=100.105.39.157 port=20008 user=jennyer dbname=postgres' PUBLICATION mypub_dn001 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);

CREATE OPENTENBASE SUBSCRIPTION sub_dn002 CONNECTION 'host=100.105.39.157 port=20009 user=jennyer dbname=postgres' PUBLICATION mypub_dn002 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);

```

查询验证从发布端同步过来的存量数据

订阅端CN：

```
select count(*) from users;
 count  
--------
 399999
(1 row)

```

### 3.4 验证增量数据同步
连接发布端CN插入增量数据：

```
insert into users select i, 'a', i+1 from generate_series(400000, 500000) i;
INSERT 0 100001
```

查询验证从发布端同步过来的增量数据  
订阅端CN：

```
select count(*) from users;
 count  
--------
 500000
(1 row)
```


## 4. 双向同步配置

## 4.1 双活集群各自建表
集群1-CN：

```
create table test(id int,name varchar(30),PRIMARY KEY(id));
```

集群2-CN： 
 
```
create table test(id int,name varchar(30),PRIMARY KEY(id));
```


## 4.2 集群1最为发布端，在所有DN上进行数据发布
集群1-DN1:

```
CREATE PUBLICATION cluster1_dn001 FOR ALL TABLES;
```

集群1-DN2：

```
CREATE PUBLICATION cluster1_dn002 FOR ALL TABLES;
```	

## 4.3 集群2最为发布端，在所有DN上进行数据发布
集群2-DN1:

```
CREATE PUBLICATION cluster2_dn001 FOR ALL TABLES;
```

集群2-DN2：

```
CREATE PUBLICATION cluster2_dn002 FOR ALL TABLES;
```	

### 4.4 集群1最为订阅端, 在任意CN上进行数据订阅
集群1-CN：

```
CREATE OPENTENBASE SUBSCRIPTION sub_cluster2_dn001 CONNECTION 'host=100.105.50.198 port=20008 user=jennyer dbname=postgres' PUBLICATION cluster2_dn001 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
CREATE OPENTENBASE SUBSCRIPTION sub_cluster2_dn002 CONNECTION 'host=100.105.50.198 port=20009 user=jennyer dbname=postgres' PUBLICATION cluster2_dn002 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
```

### 4.5 集群2最为订阅端, 在任意CN上进行数据订阅

集群2-CN：

```
CREATE OPENTENBASE SUBSCRIPTION sub_cluster1_dn001 CONNECTION 'host=100.105.39.157 port=20008 user=jennyer dbname=postgres' PUBLICATION cluster1_dn001 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
CREATE OPENTENBASE SUBSCRIPTION sub_cluster1_dn002 CONNECTION 'host=100.105.39.157 port=20009 user=jennyer dbname=postgres' PUBLICATION cluster1_dn002 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
```

### 4.6 集群1中进行写入部分数据
集群1-CN：

```
insert into test values(1,'a'),(3,'a'),(5,'a'),(7,'a'),(9,'a'),(11,'a'),(13,'a'),(15,'a');
```

### 4.7 集群2中进行写入部分数据
集群2-CN：	

```
insert into test values(2,'b'),(4,'b'),(6,'b'),(8,'b'),(10,'b'),(12,'b'),(14,'b'),(16,'b');
```

### 4.8 验证集群1同步的结果（数据来源本端写入和远端同步）
集群1-CN：

```
select  * from test;
postgres=# select  * from test order by 1;
 id | name 
----+------
  1 | a
  2 | b
  3 | a
  4 | b
  5 | a
  6 | b
  7 | a
  8 | b
  9 | a
 10 | b
 11 | a
 12 | b
 13 | a
 14 | b
 15 | a
 16 | b
(16 rows)
```

### 4.9 验证集群2同步的全量结果（数据来源本端写入和远端同步）
集群2-CN：

```
postgres=# select  * from test order by 1;
 id | name 
----+------
  1 | a
  2 | b
  3 | a
  4 | b
  5 | a
  6 | b
  7 | a
  8 | b
  9 | a
 10 | b
 11 | a
 12 | b
 13 | a
 14 | b
 15 | a
 16 | b
(16 rows)
```

可以在集群1或者2上任意一方进行写入，最终集群1和2都有着全量数据。
 