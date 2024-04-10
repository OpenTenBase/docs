# V2.3.0 upgrade feature opentenbase_subscription usage instructions

## 1. Modify wal_level

Because multiplexing is implemented using logical replication, it is necessary to configure wal_level on all CN/DN nodes in all clusters of multiplexing to be logical


```
vim postgres.comf
wal_level = logical
:wq
```

## 2. Install the opentenbase_subscription tool:
Connect to the CN of each of the two config live clusters (for any cluster, choose any CN to execute, but both clusters need to be installed) :


```
CREATE EXTENSION opentenbase_subscription;
```

## 3. One-way synchronous configuration

Here, 1CN+2DN at the publisher and 1CN+2DN at the subscriber are taken as examples, and other cluster size configuration steps are similar

### 3.1. Connect any CN on the publishing side to build a table


```
postgres=# create table users(id int,name varchar(30),f3 int,PRIMARY KEY(id));
postgres=# insert into users select i, 'a', i+1 from generate_series(1, 399999) i;
INSERT 0 399999
```

### 3.2 Perform data publishing on the publishing side DN

Note: If there is a publisher cluster with multiple DN, each DN needs to be configured for publication

Publisher DN1:


```
CREATE PUBLICATION mypub_dn001 FOR ALL TABLES;
```

Publisher DN2:


```
CREATE PUBLICATION mypub_dn002 FOR ALL TABLES;
```


### 3.3 Subscribe data on the subscriber CN
Subscriber CN:


```
create table users(id int,name varchar(30),f3 int,PRIMARY KEY(id)) ;

CREATE OPENTENBASE SUBSCRIPTION sub_dn001 CONNECTION 'host=100.105.39.157 port=20008 user=jennyer dbname=postgres' PUBLICATION mypub_dn001 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);

CREATE OPENTENBASE SUBSCRIPTION sub_dn002 CONNECTION 'host=100.105.39.157 port=20009 user=jennyer dbname=postgres' PUBLICATION mypub_dn002 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);

```

The query validates the stock data synchronized from the publisher

Subscriber CN:


```
select count(*) from users;
 count  
--------
 399999
(1 row)

```

### 3.Verify incremental data synchronization
Connect the publisher CN to insert incremental data:


```
insert into users select i, 'a', i+1 from generate_series(400000, 500000) i;
INSERT 0 100001
```

The query validates the incremental data subscriber CN synchronized from the publisher:


```
select count(*) from users;
 count  
--------
 500000
(1 row)
```


## 4. Bidirectional synchronous configuration

## 4.1 Doubly active clusters build their own tables
Cluster 1-CN:


```
create table test(id int,name varchar(30),PRIMARY KEY(id));
```

Cluster 2-CN:

 
```
create table test(id int,name varchar(30),PRIMARY KEY(id));
```


## 4.2 Cluster 1 is the publishing end, and performs data publishing on all DN
Cluster 1-DN1:


```
CREATE PUBLICATION cluster1_dn001 FOR ALL TABLES;
```

Cluster 1-DN2:


```
CREATE PUBLICATION cluster1_dn002 FOR ALL TABLES;
```	

## 4.3 Cluster 2 is the publishing end, and performs data publishing on all DN
Cluster 2-DN1:


```
CREATE PUBLICATION cluster2_dn001 FOR ALL TABLES;
```

Cluster 2-DN2:


```
CREATE PUBLICATION cluster2_dn002 FOR ALL TABLES;
```	

### 4.4 Cluster 1 acts as a subscriber and subscribes data on any CN
Cluster 1-CN:


```
CREATE OPENTENBASE SUBSCRIPTION sub_cluster2_dn001 CONNECTION 'host=100.105.50.198 port=20008 user=jennyer dbname=postgres' PUBLICATION cluster2_dn001 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
CREATE OPENTENBASE SUBSCRIPTION sub_cluster2_dn002 CONNECTION 'host=100.105.50.198 port=20009 user=jennyer dbname=postgres' PUBLICATION cluster2_dn002 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
```

### 4.5 Cluster 2 acts as the subscriber and subscribes data on any CN

Cluster 2-CN:


```
CREATE OPENTENBASE SUBSCRIPTION sub_cluster1_dn001 CONNECTION 'host=100.105.39.157 port=20008 user=jennyer dbname=postgres' PUBLICATION cluster1_dn001 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
CREATE OPENTENBASE SUBSCRIPTION sub_cluster1_dn002 CONNECTION 'host=100.105.39.157 port=20009 user=jennyer dbname=postgres' PUBLICATION cluster1_dn002 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
```

### 4.6 Cluster 1 to write partial data
Cluster 1-CN:


```
insert into test values(1,'a'),(3,'a'),(5,'a'),(7,'a'),(9,'a'),(11,'a'),(13,'a'),(15,'a');
```

### 4.7 Cluster 2 to write some data
Cluster 2-CN:


```
insert into test values(2,'b'),(4,'b'),(6,'b'),(8,'b'),(10,'b'),(12,'b'),(14,'b'),(16,'b');
```

### 4.8 Validate cluster 1 sync results (source local write and remote sync)
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

### 4.9 Verify full results of cluster 2 synchronization (source local write and remote sync)
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

You can write to either cluster 1 or 2, and you'll end up with clusters 1 and 2 both having full data.
 