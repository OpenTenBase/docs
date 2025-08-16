# V2.3.0 Upgrade Feature opentenbase_subscription Usage Notes
## 1. Modify wal_level
Because multi-live is realized by logical replication, you need to configure the wal_level of all CN/DN nodes in all clusters of multi-live to be set to logical.
```shell script
 vim postgres.comf
 wal_level = logical
 :wq
 ```
## 2. Install the opentenbase_subscription tool:
Connect the CNs of each of the 2 clusters configured for multi-activity (for any cluster, just choose any CN to execute, but both clusters need to be installed) to execute it:
```shell script
CREATE EXTENSION opentenbase_subscription;
```
## 3. One-way synchronization configuration
Here we take 1CN+2DN on the publishing side and 1CN+2DN on the subscribing side as an example, and the configuration steps are similar for other cluster sizes.
### 3.1 Connect to any CN on the publish side to build a table.
```shell script
postgres=# create table users(id int,name varchar(30),f3 int,PRIMARY KEY(id));
postgres=# insert into users select i, 'a', i+1 from generate_series(1, 399999) i;
INSERT 0 399999
```
### 3.2 Publishing Data on a Publisher DN
Note: If there is a publisher cluster with multiple DNs, each DN needs to be configured for publishing
Publisher DN1.
```shell script
CREATE PUBLICATION mypub_dn001 FOR ALL TABLES;
```
Publisher DN2.
```shell script
CREATE PUBLICATION mypub_dn002 FOR ALL TABLES;
```
### 3.3 Data subscription on the subscription side CN
Subscription end CN:
```shell script
create table users(id int,name varchar(30),f3 int,PRIMARY KEY(id)) ;

CREATE OPENTENBASE SUBSCRIPTION sub_dn001 CONNECTION 'host=100.105.39.157 port=20008 user=jennyer dbname=postgres' PUBLICATION mypub_dn001 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);

CREATE OPENTENBASE SUBSCRIPTION sub_dn002 CONNECTION 'host=100.105.39.157 port=20009 user=jennyer dbname=postgres' PUBLICATION mypub_dn002 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
```
Query validation of stock data synchronized from the publishing side

CN on the subscription side:
```shell script
select count(*) from users;
 count  
--------
 399999
(1 row)

```
### 3.4 Verifying incremental data synchronization
Connect the publisher CN to insert incremental data:
```shell script
insert into users select i, 'a', i+1 from generate_series(400000, 500000) i;
INSERT 0 100001
```
Query to validate incremental data synchronized from the publish side
CN on the subscription side:
```shell script
select count(*) from users;
 count  
--------
 500000
(1 row)
```
## 4. Bidirectional synchronization configuration
### 4.1 Dual-Active Cluster Individual Table Building
Cluster 1-CN:
```shell script
create table test(id int,name varchar(30),PRIMARY KEY(id));
```
Cluster 2-CN:
```shell script
create table test(id int,name varchar(30),PRIMARY KEY(id));
```
### 4.2 Cluster 1 is the most publishing end, with data publishing on all DNs
Cluster 1-DN1.
```shell script
CREATE PUBLICATION cluster1_dn001 FOR ALL TABLES;
```
Cluster 1-DN2.
```shell script
CREATE PUBLICATION cluster1_dn002 FOR ALL TABLES;
```
### 4.3 Cluster 2 is the most publishing end, with data publishing on all DNs
Cluster 2-DN1.
```shell script
CREATE PUBLICATION cluster2_dn001 FOR ALL TABLES;
```
Cluster 2-DN2.
```shell script
CREATE PUBLICATION cluster2_dn002 FOR ALL TABLES;
```
### 4.4 Cluster 1 is the most subscribed side, subscribing to data on any CN
Cluster 1-CN:
```shell script
CREATE OPENTENBASE SUBSCRIPTION sub_cluster2_dn001 CONNECTION 'host=100.105.50.198 port=20008 user=jennyer dbname=postgres' PUBLICATION cluster2_dn001 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
CREATE OPENTENBASE SUBSCRIPTION sub_cluster2_dn002 CONNECTION 'host=100.105.50.198 port=20009 user=jennyer dbname=postgres' PUBLICATION cluster2_dn002 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
```
### 4.5 Cluster 2 is the most subscribed side, with data subscription on any CN
Cluster 2-CN:
```shell script
CREATE OPENTENBASE SUBSCRIPTION sub_cluster1_dn001 CONNECTION 'host=100.105.39.157 port=20008 user=jennyer dbname=postgres' PUBLICATION cluster1_dn001 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
CREATE OPENTENBASE SUBSCRIPTION sub_cluster1_dn002 CONNECTION 'host=100.105.39.157 port=20009 user=jennyer dbname=postgres' PUBLICATION cluster1_dn002 WITH (connect=true, enabled=true, create_slot=true, copy_data=true, synchronous_commit=on, ignore_pk_conflict = true, parallel_number=4);
```
### 4.6 Write partial data performed in cluster 1
Cluster 1-CN:
```shell script
insert into test values(1,'a'),(3,'a'),(5,'a'),(7,'a'),(9,'a'),(11,'a'),(13,'a'),(15,'a');
```
### 4.7 Write partial data performed in cluster 2
Cluster 2-CN:
```shell script
insert into test values(2,'b'),(4,'b'),(6,'b'),(8,'b'),(10,'b'),(12,'b'),(14,'b'),(16,'b');
```
### 4.8 Results of validating cluster 1 synchronization (data source local writes and remote synchronization)
Cluster 1-CN:
```shell script
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
### 4.9 Validate full volume results of cluster 2 synchronization (data sources local writes and remote synchronization)
Cluster 2-CN:
```shell script
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
Writes can be done on either cluster 1 or 2, and eventually both clusters 1 and 2 have the full amount of data.