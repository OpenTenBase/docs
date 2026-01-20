# V2.3.0 Upgrade feature opentenbase_subscription usage instructions

## 1. Modify wal_level

Because Multi-Active is implemented using logical replication, it is necessary to configure the wal_level of all CN/DN nodes in all clusters where Multi-Active is configured to be logical.

```
vim postgres.comf
wal_level = logical
:wq
```

## 2. Install the opentenbase_subscription tool:
Connect and configure the two clusters with multiple active CNs respectively (for any cluster, you can choose any CN to execute, but both clusters need to be installed) and execute:

```
CREATE EXTENSION opentenbase_subscription;
```

## 3. One-way sync configuration

Here we take the publisher 1CN+2DN and the subscriber 1CN+2DN as examples. The configuration steps for other cluster scales are similar.

### 3.1 Connect to any CN on the publishing side to create a table

```
postgres=# create table users(id int,name varchar(30),f3 int,PRIMARY KEY(id));
postgres=# insert into users select i, 'a', i+1 from generate_series(1, 399999) i;
INSERT 0 399999
```

### 3.2 Data publishing on the publishing side DN

Note: If there are multiple DNs in the publishing cluster, each DN needs to be configured and published.

Publishing side DN1:

```
CREATE PUBLICATION mypub_dn001 FOR ALL TABLES;
```

Publishing side DN2:

```
CREATE PUBLICATION mypub_dn002 FOR ALL TABLES;
```


### 3.3 Perform data subscription on the subscriber CN
Subscriber CN:

```
create table users(id int,name varchar(30),f3 int,PRIMARY KEY(id)) ;

CREATE OPENTENBASE SUBSCRIPTION sub_dn001 CONNECTION 'host=100.105.39.157 port=20008 user=jennyer dbname=postgres' PUBLICATION mypub_dn001 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);

CREATE OPENTENBASE SUBSCRIPTION sub_dn002 CONNECTION 'host=100.105.39.157 port=20009 user=jennyer dbname=postgres' PUBLICATION mypub_dn002 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);

```

Query and verify the existing data synchronized from the publisher

Subscriber CN:

```
select count(*) from users;
 count  
--------
 399999
(1 row)

```

### 3.4 Verify incremental data synchronization
Connect the publisher CN to insert incremental data:

```
insert into users select i, 'a', i+1 from generate_series(400000, 500000) i;
INSERT 0 100001
```

Query and verify the incremental data synchronized from the publisher  

Subscriber CN:

```
select count(*) from users;
 count  
--------
 500000
(1 row)
```


## 4. Two-way sync configuration

## 4.1 Create tables for each active-active cluster
Cluster 1-CN:

```
create table test(id int,name varchar(30),PRIMARY KEY(id));
```

Cluster 2-CN:
 
```
create table test(id int,name varchar(30),PRIMARY KEY(id));
```


## 4.2 Cluster 1 is the publishing end and publishes data on all DNs.
Cluster 1-DN1:

```
CREATE PUBLICATION cluster1_dn001 FOR ALL TABLES;
```

Cluster 1-DN2:

```
CREATE PUBLICATION cluster1_dn002 FOR ALL TABLES;
```	

## 4.3 Cluster 2 serves as the publishing end, publishing data on all DNs
Cluster 2-DN1:

```
CREATE PUBLICATION cluster2_dn001 FOR ALL TABLES;
```

Cluster 2-DN2:

```
CREATE PUBLICATION cluster2_dn002 FOR ALL TABLES;
```	

### 4.4 Cluster 1 is the subscriber and performs data subscription on any CN.
Cluster 1-CN:

```
CREATE OPENTENBASE SUBSCRIPTION sub_cluster2_dn001 CONNECTION 'host=100.105.50.198 port=20008 user=jennyer dbname=postgres' PUBLICATION cluster2_dn001 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
CREATE OPENTENBASE SUBSCRIPTION sub_cluster2_dn002 CONNECTION 'host=100.105.50.198 port=20009 user=jennyer dbname=postgres' PUBLICATION cluster2_dn002 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
```

### 4.5 Cluster 2 is the subscriber and performs data subscription on any CN.

Cluster 2-CN:

```
CREATE OPENTENBASE SUBSCRIPTION sub_cluster1_dn001 CONNECTION 'host=100.105.39.157 port=20008 user=jennyer dbname=postgres' PUBLICATION cluster1_dn001 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
CREATE OPENTENBASE SUBSCRIPTION sub_cluster1_dn002 CONNECTION 'host=100.105.39.157 port=20009 user=jennyer dbname=postgres' PUBLICATION cluster1_dn002 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
```

### 4.6 Write some data in cluster 1
Cluster 1-CN:

```
insert into test values(1,'a'),(3,'a'),(5,'a'),(7,'a'),(9,'a'),(11,'a'),(13,'a'),(15,'a');
```

### 4.7 Write some data in cluster 2
Cluster 2-CN:

```
insert into test values(2,'b'),(4,'b'),(6,'b'),(8,'b'),(10,'b'),(12,'b'),(14,'b'),(16,'b');
```

### 4.8 Verify the results of cluster 1 synchronization (data source local writing and remote synchronization)
Cluster 1-CN:

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

### 4.9 Verify the full results of cluster 2 synchronization (data source local writing and remote synchronization)
Cluster 2-CN:

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

Writing can be done on either cluster 1 or 2, and eventually both clusters 1 and 2 have full data.
 