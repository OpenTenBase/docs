# 问题定位及性能优化

## 日志管理 

### OpenTenBase 日志格式说明 

执行正确的语句产生的日志  

```
2017-10-11 16:23:55.178 CST,"pgxz","postgres",11499,"127.0.0.1:2329",59ddd50c.2ceb,1,"idle",2017-10-11 16:23:40 CST,3/26053,0,LOG,00000,"statement: select * from pg_class limit 1;",,,,,,,,,"psql"
```
```
执行时间                                                            | 2017-10-11 16:23:55.178
用户名                                                              | pgxz
数据库                                                              | postgres
进程id                                                              | 11499
客户端id                                                            | 127.0.0.1:2329
会话 ID                                                             | 59ddd50c.2ceb
每个会话的行号                                                        | 1
命令标签                                                             | idle
登录时间                                                             | 2017-10-11 16:23:40
虚拟事务 ID                                                          | 3/26053
普通事务 ID                                                          | 0
级别                                                                | LOG
SQLSTATE 代码                                                       | 00000
执行信息                                                             | statement: select * from pg_class limit 1;
详情                                                                | 
提示                                                                | 
导致错误的内部查询                                                    | 
错误位置所在的字符计数                                                 | 
错误上下文                                                           | 
导致错误的用户查询（如果有且被log_min_error_statement启用）              | 
错误位置所在的字符计数                                                 | 
在 PostgreSQL 源代码中错误的位置(如果log_error_verbosity被设置为verbose) | 
应用名                                                               | psql
```

错误日志解释  

```
2017-10-11 16:24:10.233 CST,"pgxz","postgres",11499,"127.0.0.1:2329",59ddd50c.2ceb,2,"idle",2017-10-11 16:23:40 CST,3/26054,0,LOG,00000,"statement: select * from pgxc_nodes limit 1;",,,,,,,,,"psql"
2017-10-11 16:24:10.233 CST,"pgxz","postgres",11499,"127.0.0.1:2329",59ddd50c.2ceb,3,"SELECT",2017-10-11 16:23:40 CST,3/26054,0,ERROR,42P01,"relation ""pgxc_nodes"" does not exist",,,,,,,,,"psql"

```
向 OpenTenBase 执行错误的语句会产生两条日志，一条是执行语句，一条提示出错的原因  

### 对日志进行分析  
#### 创建日志表 

```  
CREATE table opentenbase_log
(
  log_time timestamp without time zone,
  user_name text,
  database_name text,
  process_id integer,
  connection_from text,
  session_id text,
  session_line_num bigint,
  command_tag text,
  session_start_time timestamp without time zone,
  virtual_transaction_id text,
  transaction_id bigint,
  error_severity text,
  sql_state_code text,
  message text,
  detail text,
  hint text,
  internal_query text,
  internal_query_pos integer,
  context text,
  query text,
  query_pos integer,
  location text,
  application_name text
);
```
#### 导入日志数据  
OpenTenBase 日志文件默认存储在“数据目录/pg\_log”目录下面

```
postgres=# COPY opentenbase_log FROM '/data/pgxz/data/pgxz/dn001/pg_log/postgresql-Tuesday-16.csv' WITH csv; 
COPY 10790
```
#### 统计日志数据  
--按照session连接及操作时间排序

```
postgres=# select * from opentenbase_log order by process_id,log_time;
```

--查询错误日志

```
SELECT * FROM  opentenbase_log WHERE error_severity='ERROR' limit 1;  
``` 

--统计session操作数统计

```
postgres=#  select count(1),process_id,user_name,database_name from opentenbase_log group by process_id,user_name,database_name order by count(1) desc limit 10;
 count | process_id | user_name | database_name 
-------+------------+-----------+---------------
  2770 |      48067 | pgxz      | postgres
    10 |      22143 | pgxz      | postgres
    10 |      28778 | pgxz      | postgres
     9 |      28367 | pgxz      | postgres
     9 |      44280 | pgxz      | postgres
     8 |      32442 | pgxz      | postgres
     7 |      17911 | pgxz      | postgres
     7 |      21865 | pgxz      | postgres
     7 |      26159 | pgxz      | postgres
     7 |      45471 | pgxz      | postgres
(10 rows)
```

--用户操作统计

```
postgres=#  select count(1),user_name from opentenbase_log group by user_name order by count(1) desc limit 10;                                                           
 count | user_name 
-------+-----------
 10790 | pgxz
```

--数据库访问次数统计

```
postgres=#  select count(1),database_name from opentenbase_log group by database_name order by count(1) desc limit 10;             
 count | database_name 
-------+---------------
 10790 | postgres
(1 row)
```

--错误信息统计

```
postgres=# select count(1),user_name,database_name from opentenbase_log where error_severity='ERROR' group by user_name,database_name order by count(1) desc limit 10;           
 count | user_name | database_name 
-------+-----------+---------------
  1390 | pgxz      | postgres
(1 row)
```

### 配置只收集慢的sql语句  
\#用户访问日志格式  
log\_destination = 'csvlog'  

\#启用用户访问日志收集器  
logging\_collector = on  

\#配置sql语句执行超过多少毫秒数时，语句将被记录,值为-1时禁用，0时记录所有语句  
\#下面配置只收集运行超过1秒的语句  
log\_min\_duration\_statement = 1000  

\#默认不记录任何日志  
log\_statement = 'none'  

收集到的日志文件内容如下所示
  
```
2017-10-15 10:25:54.106 CST,"postgres","postgres",43799,"127.0.0.1:17899",59e2c65b.ab17,4,"SELECT",2017-10-15 10:22:19 CST,2/0,0,LOG,00000,"duration: 1338.366 ms  statement: select * from t where id=20000 or id=2000000;",,,,,,,,,"psql"
```

系统记录运行的语句及运行时间

## 如何查询数据是否倾斜  
连接上不同的dn节点，查询表的容量大小，如果大小偏差较大就可以判断存在数据倾斜  
连接dn001:

```
[pgxz@VM_0_29_centos pgxz]$ psql -p 15432 -h 172.16.0.47
psql (PostgreSQL 10 (opentenbase 2.01))
Type "help" for help.

postgres=# select pg_size_pretty(pg_table_size('opentenbase_1'));
 pg_size_pretty 
----------------
 2408 kB
(1 row)

postgres=# select pg_size_pretty(pg_table_size('opentenbase_2'));
 pg_size_pretty 
----------------
 896 kB
(1 row)

postgres=# \q
```

连接dn002:

```
[pgxz@VM_0_29_centos pgxz]$ psql -p 15431 -h 172.16.0.47 
psql (PostgreSQL 10 (opentenbase 2.01))
Type "help" for help.

postgres=# select pg_size_pretty(pg_table_size('opentenbase_1'));
 pg_size_pretty 
----------------
 2408 kB
(1 row)

postgres=#  select pg_size_pretty(pg_table_size('opentenbase_2'));
 pg_size_pretty 
----------------
 464 kB
(1 row)
```

上面数据表“opentenbase_2”容量相差为一半，基本可以判定存在数据倾斜。

## 如何优化有问题的Sql语句  
### 查看是否为分布键查询 

``` 
postgres=# explain select * from opentenbase_1 where f1=1;        
                                   QUERY PLAN                                   
--------------------------------------------------------------------------------
 Remote Fast Query Execution  (cost=0.00..0.00 rows=0 width=0)
   Node/s: dn001, dn002
   ->  Gather  (cost=1000.00..7827.20 rows=1 width=14)
         Workers Planned: 2
         ->  Parallel Seq Scan on opentenbase_1  (cost=0.00..6827.10 rows=1 width=14)
               Filter: (f1 = 1)
(6 rows)
```

```
postgres=# explain select * from opentenbase_1 where f2=1;
                                   QUERY PLAN                                   
--------------------------------------------------------------------------------
 Remote Fast Query Execution  (cost=0.00..0.00 rows=0 width=0)
   Node/s: dn001
   ->  Gather  (cost=1000.00..7827.20 rows=1 width=14)
         Workers Planned: 2
         ->  Parallel Seq Scan on opentenbase_1  (cost=0.00..6827.10 rows=1 width=14)
               Filter: (f2 = 1)
(6 rows)
```
上面第一个查询为非分布键查询，需要发往所有节点，这样最慢的节点决定了整个业务的速度，需要保持所有节点的响应性能一致，业务设计查询时尽可能带上分布键

### 查看是否使用上索引 

``` 
postgres=# create index opentenbase_2_f2_idx on opentenbase_2(f2); 
CREATE INDEX
postgres=# explain select * from opentenbase_2 where f2=1;
                                     QUERY PLAN                                      
-------------------------------------------------------------------------------------
 Remote Fast Query Execution  (cost=0.00..0.00 rows=0 width=0)
   Node/s: dn001, dn002
   ->  Index Scan using opentenbase_2_f2_idx on opentenbase_2  (cost=0.42..4.44 rows=1 width=14)
         Index Cond: (f2 = 1)
(4 rows)
```

```
postgres=# explain select * from opentenbase_2 where f3='1';
                                   QUERY PLAN                                   
--------------------------------------------------------------------------------
 Remote Fast Query Execution  (cost=0.00..0.00 rows=0 width=0)
   Node/s: dn001, dn002
   ->  Gather  (cost=1000.00..7827.20 rows=1 width=14)
         Workers Planned: 2
         ->  Parallel Seq Scan on opentenbase_2  (cost=0.00..6827.10 rows=1 width=14)
               Filter: (f3 = '1'::text)
(6 rows)

```

第一个查询使用了索引，第二个没有使用索引，通常情况下，使用索引可以加速查询速度，但要记住索引也会增加更新的开销

### 查看是否为分布key join 

``` 
postgres=# explain  select opentenbase_1.* from opentenbase_1,opentenbase_2 where opentenbase_1.f1=opentenbase_2.f1 ;           
                                           QUERY PLAN                                           
------------------------------------------------------------------------------------------------
 Remote Subquery Scan on all (dn001,dn002)  (cost=29.80..186.32 rows=3872 width=40)
   ->  Hash Join  (cost=29.80..186.32 rows=3872 width=40)
         Hash Cond: (opentenbase_1.f1 = opentenbase_2.f1)
         ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.00..158.40 rows=880 width=40)
               Distribute results by S: f1
               ->  Seq Scan on opentenbase_1  (cost=0.00..18.80 rows=880 width=40)
         ->  Hash  (cost=18.80..18.80 rows=880 width=4)
               ->  Seq Scan on opentenbase_2  (cost=0.00..18.80 rows=880 width=4)
(8 rows)
```

```
postgres=# explain  select opentenbase_1.* from opentenbase_1,opentenbase_2 where opentenbase_1.f2=opentenbase_2.f1 ;   
                                   QUERY PLAN                                    
---------------------------------------------------------------------------------
 Remote Fast Query Execution  (cost=0.00..0.00 rows=0 width=0)
   Node/s: dn001, dn002
   ->  Hash Join  (cost=18904.69..46257.08 rows=500564 width=14)
         Hash Cond: (opentenbase_1.f2 = opentenbase_2.f1)
         ->  Seq Scan on opentenbase_1  (cost=0.00..9225.64 rows=500564 width=14)
         ->  Hash  (cost=9225.64..9225.64 rows=500564 width=4)
               ->  Seq Scan on opentenbase_2  (cost=0.00..9225.64 rows=500564 width=4)
(7 rows)
```

第一查询需要数据重分布，而第二个是不需要，分布键join查询性能会更高。

### 查看join发生的节点  
```
postgres=#  explain  select opentenbase_1.* from opentenbase_1,opentenbase_2 where opentenbase_1.f1=opentenbase_2.f1 ;    
                                          QUERY PLAN                                           
-----------------------------------------------------------------------------------------------
 Hash Join  (cost=29.80..186.32 rows=3872 width=40)
   Hash Cond: (opentenbase_1.f1 = opentenbase_2.f1)
   ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.00..158.40 rows=880 width=40)
         ->  Seq Scan on opentenbase_1  (cost=0.00..18.80 rows=880 width=40)
   ->  Hash  (cost=126.72..126.72 rows=880 width=4)
         ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.00..126.72 rows=880 width=4)
               ->  Seq Scan on opentenbase_2  (cost=0.00..18.80 rows=880 width=4)
(7 rows)
```

```
postgres=# set prefer_olap to on;
SET
postgres=# explain  select opentenbase_1.* from opentenbase_1,opentenbase_2 where opentenbase_1.f1=opentenbase_2.f1 ;  
                                           QUERY PLAN                                           
------------------------------------------------------------------------------------------------
 Remote Subquery Scan on all (dn001,dn002)  (cost=29.80..186.32 rows=3872 width=40)
   ->  Hash Join  (cost=29.80..186.32 rows=3872 width=40)
         Hash Cond: (opentenbase_1.f1 = opentenbase_2.f1)
         ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.00..158.40 rows=880 width=40)
               Distribute results by S: f1
               ->  Seq Scan on opentenbase_1  (cost=0.00..18.80 rows=880 width=40)
         ->  Hash  (cost=18.80..18.80 rows=880 width=4)
               ->  Seq Scan on opentenbase_2  (cost=0.00..18.80 rows=880 width=4)
(8 rows)
```

上面join在cn节点执行，下面的在dn上重分布后再join，业务上设计一般oltp类业务在cn上进行少数据量join性能会更好
### 查看并行的worker数 

```
postgres=# explain select count(1) from opentenbase_1;
                                      QUERY PLAN                                       
---------------------------------------------------------------------------------------
 Finalize Aggregate  (cost=118.81..118.83 rows=1 width=8)
   ->  Remote Subquery Scan on all (dn001,dn002)  (cost=118.80..118.81 rows=1 width=0)
         ->  Partial Aggregate  (cost=18.80..18.81 rows=1 width=8)
               ->  Seq Scan on opentenbase_1  (cost=0.00..18.80 rows=880 width=0)
(4 rows)
```

```
postgres=# analyze opentenbase_1;
ANALYZE
postgres=# explain select count(1) from opentenbase_1;
                                             QUERY PLAN                                             
----------------------------------------------------------------------------------------------------
 Parallel Finalize Aggregate  (cost=14728.45..14728.46 rows=1 width=8)
   ->  Parallel Remote Subquery Scan on all (dn001,dn002)  (cost=14728.33..14728.45 rows=1 width=0)
         ->  Gather  (cost=14628.33..14628.44 rows=1 width=8)
               Workers Planned: 2
               ->  Partial Aggregate  (cost=13628.33..13628.34 rows=1 width=8)
                     ->  Parallel Seq Scan on opentenbase_1  (cost=0.00..12586.67 rows=416667 width=0)
(6 rows)
```

上面第一个查询没走并行，analyze后走并行才是正确的，建议大数据量更新再执行analyze。

### 检查各个节点的执行计划是否一致  

```
./opentenbase_run_sql_dn_master.sh "explain select * from opentenbase_2 where f2=1"  
dn006 --- psql -h 172.16.0.13 -p 11227 -d postgres -U opentenbase -c "explain select * from opentenbase_2 where f2=1"
                                 QUERY PLAN                                  
-----------------------------------------------------------------------------
 Bitmap Heap Scan on opentenbase_2  (cost=2.18..7.70 rows=4 width=40)
   Recheck Cond: (f2 = 1)
   ->  Bitmap Index Scan on opentenbase_2_f2_idx  (cost=0.00..2.18 rows=4 width=0)
         Index Cond: (f2 = 1)
(4 rows)

dn002 --- psql -h 172.16.0.42 -p 11012 -d postgres -U opentenbase -c "explain select * from opentenbase_2 where f2=1"
                                  QUERY PLAN                                   
-------------------------------------------------------------------------------
 Index Scan using opentenbase_2_f2_idx on opentenbase_2  (cost=0.42..4.44 rows=1 width=14)
   Index Cond: (f2 = 1)
(2 rows)
```

这两个dn的执行计划不一致，最大可能可以是数据倾斜或者是执行计划给禁用导致的。

如果有可能的话，DBA可以配置在系统空闲时执行全库analyze和vacuum。  

## 优化实例  
### count(distinct xx)优化 
```
postgres=# CREATE TABLE t1(f1 serial not null unique,f2 text,f3 text,f4 text,f5 text,f6 text,f7 text,f8 text,f9 text,f10 text,f11 text,f12 text) distribute by shard(f1);
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
Time: 89.938 ms

postgres=# insert into t1 select t,md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text) from generate_series(1,1000000) as t;
INSERT 0 1000000
Time: 14849.045 ms (00:14.849)

postgres=# analyze t1;
ANALYZE
Time: 1340.387 ms (00:01.340)

postgres=# explain (verbose)  select count(distinct f2) from t1;  
                                                              QUERY PLAN                                                               
---------------------------------------------------------------------------------------------------------------------------------------
 Aggregate  (cost=103320.00..103320.01 rows=1 width=8)
   Output: count(DISTINCT f2)
   ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=100.00..100820.00 rows=1000000 width=33)
         Output: f2
         ->  Seq Scan on public.t1  (cost=0.00..62720.00 rows=1000000 width=33)
               Output: f2
(6 rows)

Time: 0.748 ms
postgres=# select count(distinct f2) from t1;  
  count  
---------
 1000000
(1 row)

Time: 6274.684 ms (00:06.275)

postgres=# select count(distinct f2) from t1 where f1 <10;       
 count 
-------
     9
(1 row)

Time: 19.261 ms
```

上面发现count(distinct f2)是发生在cn节点，对于TP类业务，需要操作的数据量少的情况下，性能开销是没有问题的，而且往往比下推执行的性能开销还要小。但如果一次要操作的数据量比较大的ap类业务，则网络传输就会成功瓶颈，下面看看改写后的执行计划  

```
postgres=# explain (verbose)  select count(1) from (select f2 from t1 group by f2) as t ; 
                                                                           QUERY PLAN                                                                            
-----------------------------------------------------------------------------------------------------------------------------------------------------------------
 Finalize Aggregate  (cost=355600.70..355600.71 rows=1 width=8)
   Output: count(1)
   ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=355600.69..355600.70 rows=1 width=0)
         Output: PARTIAL count(1)
         ->  Partial Aggregate  (cost=355500.69..355500.70 rows=1 width=8)
               Output: PARTIAL count(1)
               ->  Group  (cost=340500.69..345500.69 rows=1000000 width=33)
                     Output: t1.f2
                     Group Key: t1.f2
                     ->  Sort  (cost=340500.69..343000.69 rows=1000000 width=0)
                           Output: t1.f2
                           Sort Key: t1.f2
                           ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=216192.84..226192.84 rows=1000000 width=0)
                                 Output: t1.f2
                                 Distribute results by S: f2
                                 ->  Group  (cost=216092.84..221092.84 rows=1000000 width=33)
                                       Output: t1.f2
                                       Group Key: t1.f2
                                       ->  Sort  (cost=216092.84..218592.84 rows=1000000 width=33)
                                             Output: t1.f2
                                             Sort Key: t1.f2
                                             ->  Seq Scan on public.t1  (cost=0.00..62720.00 rows=1000000 width=33)
                                                   Output: t1.f2
(23 rows)

```

改写后，并行推到dn去执行，现在看看执行的效果

```
postgres=# select count(1) from (select f2 from t1 group by f2) as t ; 
  count  
---------
 1000000
(1 row)

Time: 1328.431 ms (00:01.328)
postgres=# select count(1) from (select f2 from t1 where f1<10 group by f2) as t ; 
 count 
-------
     9
(1 row)

Time: 24.991 ms
postgres=# 
```

我们可以看到对于大量数据计算的AP类业务，性能提高了5倍

### 增大work_mem减少io访问  

```
postgres=# CREATE TABLE t1(f1 serial not null unique,f2 text,f3 text,f4 text,f5 text,f6 text,f7 text,f8 text,f9 text,f10 text,f11 text,f12 text) distribute by shard(f1);
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
Time: 70.545 ms

postgres=# CREATE TABLE t2(f1 serial not null unique,f2 text,f3 text,f4 text,f5 text,f6 text,f7 text,f8 text,f9 text,f10 text,f11 text,f12 text) distribute by shard(f1); 
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
Time: 61.913 ms

postgres=# insert into t1 select t,md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text) from generate_series(1,1000) as t;   
INSERT 0 1000
Time: 48.866 ms

postgres=# insert into t2 select t,md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text) from generate_series(1,50000) as t;     
INSERT 0 50000
Time: 792.858 ms

postgres=# analyze t1;
ANALYZE
Time: 175.946 ms

postgres=# analyze t2;
ANALYZE
Time: 318.802 ms
postgres=# 

postgres=# explain  select * from t1 where f2 not in (select f2 from t2);                
                                                                  QUERY PLAN                                                                   
-----------------------------------------------------------------------------------------------------------------------------------------------
 Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=0.00..2076712.50 rows=500 width=367)
   ->  Seq Scan on t1  (cost=0.00..2076712.50 rows=500 width=367)
         Filter: (NOT (SubPlan 1))
         SubPlan 1
           ->  Materialize  (cost=0.00..4028.00 rows=50000 width=33)
                 ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=0.00..3240.00 rows=50000 width=33)
                       ->  Seq Scan on t2  (cost=0.00..3240.00 rows=50000 width=33)
(7 rows)

Time: 0.916 ms
postgres=# select * from t1 where f2 not in (select f2 from t2);                
 f1 | f2 | f3 | f4 | f5 | f6 | f7 | f8 | f9 | f10 | f11 | f12 
----+----+----+----+----+----+----+----+----+-----+-----+-----
(0 rows)

Time: 4226.825 ms (00:04.227)
```
```
postgres=# set work_mem to '8MB';
SET
Time: 0.289 ms
postgres=# explain  select * from t1 where f2 not in (select f2 from t2);                
                                                               QUERY PLAN                                                                
-----------------------------------------------------------------------------------------------------------------------------------------
 Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=3365.00..3577.50 rows=500 width=367)
   ->  Seq Scan on t1  (cost=3365.00..3577.50 rows=500 width=367)
         Filter: (NOT (hashed SubPlan 1))
         SubPlan 1
           ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=0.00..3240.00 rows=50000 width=33)
                 ->  Seq Scan on t2  (cost=0.00..3240.00 rows=50000 width=33)
(6 rows)

Time: 0.890 ms
postgres=# select * from t1 where f2 not in (select f2 from t2);           
 f1 | f2 | f3 | f4 | f5 | f6 | f7 | f8 | f9 | f10 | f11 | f12 
----+----+----+----+----+----+----+----+----+-----+-----+-----
(0 rows)

Time: 105.249 ms
```
增大work\_mem后，性能提高了40倍，因为work\_mem足够放下filter的数据，不需要再做 Materialize物化，filter由原来的subplan变成了hash subplan，直接在内存hash表中filter，性能就上去了

注意，work\_mem默认不宜过大，建议在某个具体的查询语句中再根据需要进行调整即可。

### not in改写为anti join   
上面通过增大计算内存达到提高性能，但内存不可能无限扩大，下面通过改写语句也可以达到提高查询的性能。

```
postgres=#  explain select * from t1 left outer join t2 on t1.f2 = t2.f2 where t2.f2 is null; 
                                                                   QUERY PLAN                                                                    
-------------------------------------------------------------------------------------------------------------------------------------------------
 Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=6405.00..9260.75 rows=1 width=734)
   ->  Hash Anti Join  (cost=6405.00..9260.75 rows=1 width=734)
         Hash Cond: (t1.f2 = t2.f2)
         ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=100.00..682.00 rows=1000 width=367)
               Distribute results by S: f2
               ->  Seq Scan on t1  (cost=0.00..210.00 rows=1000 width=367)
         ->  Hash  (cost=21940.00..21940.00 rows=50000 width=367)
               ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=100.00..21940.00 rows=50000 width=367)
                     Distribute results by S: f2
                     ->  Seq Scan on t2  (cost=0.00..3240.00 rows=50000 width=367)
(10 rows)

Time: 1.047 ms
postgres=# select * from t1 left outer join t2 on t1.f2 = t2.f2 where t2.f2 is null; 
 f1 | f2 | f3 | f4 | f5 | f6 | f7 | f8 | f9 | f10 | f11 | f12 | f1 | f2 | f3 | f4 | f5 | f6 | f7 | f8 | f9 | f10 | f11 | f12 
----+----+----+----+----+----+----+----+----+-----+-----+-----+----+----+----+----+----+----+----+----+----+-----+-----+-----
(0 rows)

Time: 107.233 ms
postgres=# 
```
也可以修改not exists 

```
postgres=# explain select * from t1 where not exists( select 1 from t2 where t1.f2=t2.f2);
                                                                  QUERY PLAN                                                                   
-----------------------------------------------------------------------------------------------------------------------------------------------
 Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=3865.00..4078.75 rows=1 width=367)
   ->  Hash Anti Join  (cost=3865.00..4078.75 rows=1 width=367)
         Hash Cond: (t1.f2 = t2.f2)
         ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=100.00..682.00 rows=1000 width=367)
               Distribute results by S: f2
               ->  Seq Scan on t1  (cost=0.00..210.00 rows=1000 width=367)
         ->  Hash  (cost=5240.00..5240.00 rows=50000 width=33)
               ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=100.00..5240.00 rows=50000 width=33)
                     Distribute results by S: f2
                     ->  Seq Scan on t2  (cost=0.00..3240.00 rows=50000 width=33)
(10 rows)

Time: 0.974 ms
postgres=# select * from t1 where not exists( select 1 from t2 where t1.f2=t2.f2);        
 f1 | f2 | f3 | f4 | f5 | f6 | f7 | f8 | f9 | f10 | f11 | f12 
----+----+----+----+----+----+----+----+----+-----+-----+-----
(0 rows)

Time: 42.944 ms
```

### 分布key jon+limit优化   

```
--数据准备  
postgres=# CREATE TABLE t1(f1 serial not null unique,f2 text,f3 text,f4 text,f5 text,f6 text,f7 text,f8 text,f9 text,f10 text,f11 text,f12 text) distribute by shard(f1); 
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
postgres=# CREATE TABLE t2(f1 serial not null unique,f2 text,f3 text,f4 text,f5 text,f6 text,f7 text,f8 text,f9 text,f10 text,f11 text,f12 text) distribute by shard(f1); 
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
postgres=# insert into t1 select t,md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text) from generate_series(1,1000000) as t;
INSERT 0 1000000
postgres=# insert into t2 select t,md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text) from generate_series(1,1000000) as t; 
INSERT 0 1000000
postgres=# analyze t1;
ANALYZE
postgres=# analyze t2;
ANALYZE
postgres=# 

postgres=# \timing 
Timing is on.
postgres=# explain  select t1.* from t1,t2 where t1.f1=t2.f1 limit 10;
                                                                  QUERY PLAN                                                                  
----------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=0.25..1.65 rows=10 width=367)
   ->  Merge Join  (cost=0.25..140446.26 rows=1000000 width=367)
         Merge Cond: (t1.f1 = t2.f1)
         ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=100.12..434823.13 rows=1000000 width=367)
               ->  Index Scan using t1_f1_key on t1  (cost=0.12..62723.13 rows=1000000 width=367)
         ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=100.12..71823.13 rows=1000000 width=4)
               ->  Index Only Scan using t2_f1_key on t2  (cost=0.12..62723.13 rows=1000000 width=4)
(7 rows)

Time: 1.372 ms

postgres=# explain analyze  select t1.* from t1,t2 where t1.f1=t2.f1 limit 10;       
                                                                                         QUERY PLAN                                                                                         
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=0.25..1.65 rows=10 width=367) (actual time=2675.437..2948.199 rows=10 loops=1)
   ->  Merge Join  (cost=0.25..140446.26 rows=1000000 width=367) (actual time=2675.431..2675.508 rows=10 loops=1)
         Merge Cond: (t1.f1 = t2.f1)
         ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=100.12..434823.13 rows=1000000 width=367) (actual time=1.661..1.704 rows=10 loops=1)
         ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=100.12..71823.13 rows=1000000 width=4) (actual time=2673.761..2673.783 rows=10 loops=1)
 Planning time: 0.358 ms
 Execution time: 2973.948 ms
(7 rows)

Time: 2976.008 ms (00:02.976)
postgres=# 
```

看执行计划是在cn上面执行，merge join需要把要join的数据拉回cn再排序，然后再join，这里主切的开销在于网络，优化的话方法就是让语句其推下去计算

```
postgres=# set prefer_olap to on;
SET
Time: 0.291 ms
postgres=#  explain  select t1.* from t1,t2 where t1.f1=t2.f1 limit 10;
                                                           QUERY PLAN                                                           
--------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=100.25..101.70 rows=10 width=367)
   ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=100.25..101.70 rows=10 width=367)
         ->  Limit  (cost=0.25..1.65 rows=10 width=367)
               ->  Merge Join  (cost=0.25..140446.26 rows=1000000 width=367)
                     Merge Cond: (t1.f1 = t2.f1)
                     ->  Index Scan using t1_f1_key on t1  (cost=0.12..62723.13 rows=1000000 width=367)
                     ->  Index Only Scan using t2_f1_key on t2  (cost=0.12..62723.13 rows=1000000 width=4)
(7 rows)

Time: 1.061 ms

postgres=# explain analyze  select t1.* from t1,t2 where t1.f1=t2.f1 limit 10;   
                                                                                QUERY PLAN                                                                                 
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=100.25..101.70 rows=10 width=367) (actual time=1.527..3.899 rows=10 loops=1)
   ->  Remote Subquery Scan on all (dn01,dn02,dn03,dn04,dn05,dn06,dn07,dn08,dn09,dn10)  (cost=100.25..101.70 rows=10 width=367) (actual time=1.525..1.529 rows=10 loops=1)
 Planning time: 0.360 ms
 Execution time: 18.193 ms
(4 rows)

Time: 19.921 ms
```

相差150倍的性能，一般情况下，如果需要拉大量的数据回cn计算，则下推执行的效率会更好

### 非分布key join使用hash join性能一般最好 
  
为了提高tp类业务查询的性能，我们经常需要对一些字段建立索引，使用有索引字段join时系统往往也会使用Merge Cond和nestloop

```
--准备数据
mydb=# CREATE TABLE t1(f1 serial not null,f2 text,f3 text,f4 text,f5 text,f6 text,f7 text,f8 text,f9 text,f10 text,f11 text,f12 text) distribute by shard(f1); 
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
Time: 481.042 ms

mydb=# create index t1_f1_idx on t1(f2); 
CREATE INDEX
Time: 85.521 ms

mydb=# CREATE TABLE t2(f1 serial not null,f2 text,f3 text,f4 text,f5 text,f6 text,f7 text,f8 text,f9 text,f10 text,f11 text,f12 text) distribute by shard(f1); 
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
Time: 75.973 ms

mydb=# create index t2_f1_idx on t2(f2);  
CREATE INDEX
Time: 29.890 ms

mydb=# insert into t1 select t,md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text) from generate_series(1,1000000) as t;
INSERT 0 1000000
Time: 16450.623 ms (00:16.451)

mydb=# insert into t2 select t,md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text),md5(t::text) from generate_series(1,1000000) as t; 
INSERT 0 1000000
Time: 17218.738 ms (00:17.219)

mydb=# analyze t1;
ANALYZE

Time: 2219.341 ms (00:02.219)
mydb=# analyze t2;
ANALYZE

Time: 1649.506 ms (00:01.650)
mydb=# 
```

```
--merge join

mydb=# explain select t1.* from t1,t2 where t1.f2=t2.f2 limit 10;
                                                       QUERY PLAN                                                        
-------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=100.25..102.78 rows=10 width=367)
   ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.25..102.78 rows=10 width=367)
         ->  Limit  (cost=0.25..2.73 rows=10 width=367)
               ->  Merge Join  (cost=0.25..248056.80 rows=1000000 width=367)
                     Merge Cond: (t1.f2 = t2.f2)
                     ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.12..487380.85 rows=1000000 width=367)
                           Distribute results by S: f2
                           ->  Index Scan using t1_f1_idx on t1  (cost=0.12..115280.85 rows=1000000 width=367)
                     ->  Materialize  (cost=100.12..155875.95 rows=1000000 width=33)
                           ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.12..153375.95 rows=1000000 width=33)
                                 Distribute results by S: f2
                                 ->  Index Only Scan using t2_f1_idx on t2  (cost=0.12..115275.95 rows=1000000 width=33)
(12 rows)

Time: 4.183 ms

mydb=# explain analyze select t1.* from t1,t2 where t1.f2=t2.f2 limit 10;
                                                                QUERY PLAN                                                                 
-------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=100.25..102.78 rows=10 width=367) (actual time=6555.346..6556.296 rows=10 loops=1)
   ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.25..102.78 rows=10 width=367) (actual time=6555.343..6555.349 rows=10 loops=1)
 Planning time: 0.473 ms
 Execution time: 6569.828 ms
(4 rows)

Time: 6614.439 ms (00:06.614)
```

```
--nested loop  

mydb=# set enable_mergejoin to off;
SET
Time: 0.422 ms
mydb=# explain select t1.* from t1,t2 where t1.f2=t2.f2 limit 10;
                                                     QUERY PLAN                                                     
--------------------------------------------------------------------------------------------------------------------
 Limit  (cost=100.12..103.57 rows=10 width=367)
   ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.12..103.57 rows=10 width=367)
         ->  Limit  (cost=0.12..3.52 rows=10 width=367)
               ->  Nested Loop  (cost=0.12..339232.00 rows=1000000 width=367)
                     ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.00..434740.00 rows=1000000 width=367)
                           Distribute results by S: f2
                           ->  Seq Scan on t1  (cost=0.00..62640.00 rows=1000000 width=367)
                     ->  Materialize  (cost=100.12..100.31 rows=1 width=33)
                           ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.12..100.30 rows=1 width=33)
                                 Distribute results by S: f2
                                 ->  Index Only Scan using t2_f1_idx on t2  (cost=0.12..0.27 rows=1 width=33)
                                       Index Cond: (f2 = t1.f2)
(12 rows)

Time: 1.033 ms

mydb=# explain analyze select t1.* from t1,t2 where t1.f2=t2.f2 limit 10;
                                                                QUERY PLAN                                                                 
-------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=100.12..103.57 rows=10 width=367) (actual time=5608.326..5609.571 rows=10 loops=1)
   ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.12..103.57 rows=10 width=367) (actual time=5608.323..5608.349 rows=10 loops=1)
 Planning time: 0.347 ms
 Execution time: 5669.901 ms
(4 rows)

Time: 5672.584 ms (00:05.673)
```
```
--hash join

mydb=# set enable_nestloop to off;
SET
Time: 0.436 ms
mydb=#  explain select t1.* from t1,t2 where t1.f2=t2.f2 limit 10;
                                                       QUERY PLAN                                                        
-------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=85983.00..85984.94 rows=10 width=367)
   ->  Remote Subquery Scan on all (dn001,dn002)  (cost=85983.00..85984.94 rows=10 width=367)
         ->  Limit  (cost=85883.00..85884.89 rows=10 width=367)
               ->  Hash Join  (cost=85883.00..274580.00 rows=1000000 width=367)
                     Hash Cond: (t1.f2 = t2.f2)
                     ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.00..434740.00 rows=1000000 width=367)
                           Distribute results by S: f2
                           ->  Seq Scan on t1  (cost=0.00..62640.00 rows=1000000 width=367)
                     ->  Hash  (cost=100740.00..100740.00 rows=1000000 width=33)
                           ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.00..100740.00 rows=1000000 width=33)
                                 Distribute results by S: f2
                                 ->  Seq Scan on t2  (cost=0.00..62640.00 rows=1000000 width=33)
(12 rows)

Time: 1.141 ms

mydb=#  explain analyze select t1.* from t1,t2 where t1.f2=t2.f2 limit 10;
                                                                  QUERY PLAN                                                                   
-----------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=85983.00..85984.94 rows=10 width=367) (actual time=1083.691..1085.962 rows=10 loops=1)
   ->  Remote Subquery Scan on all (dn001,dn002)  (cost=85983.00..85984.94 rows=10 width=367) (actual time=1083.688..1083.699 rows=10 loops=1)
 Planning time: 0.530 ms
 Execution time: 1108.830 ms
(4 rows)

Time: 1117.713 ms (00:01.118)
```

### exists的优化  
 
exists在数据量比较大情况下，一般使用的是Semi Join ，在work_mem足够大的情况下走的是hash join，性能会更好

```
postgres=# show work_mem;
 work_mem 
----------
 4MB
(1 row)

Time: 0.298 ms
postgres=# explain  select count(1) from t1 where exists(select 1 from t2 where t2.t1_f1=t1.f1);
                                                      QUERY PLAN                                                       
-----------------------------------------------------------------------------------------------------------------------
 Finalize Aggregate  (cost=242218.32..242218.33 rows=1 width=8)
   ->  Remote Subquery Scan on all (dn001,dn002)  (cost=242218.30..242218.32 rows=1 width=0)
         ->  Partial Aggregate  (cost=242118.30..242118.31 rows=1 width=8)
               ->  Hash Semi Join  (cost=110248.00..242118.30 rows=505421 width=0)
                     Hash Cond: (t1.f1 = t2.t1_f1)
                     ->  Seq Scan on t1  (cost=0.00..17420.00 rows=1000000 width=4)
                     ->  Hash  (cost=79340.00..79340.00 rows=3000000 width=4)
                           ->  Remote Subquery Scan on all (dn001,dn002)  (cost=100.00..79340.00 rows=3000000 width=4)
                                 Distribute results by S: t1_f1
                                 ->  Seq Scan on t2  (cost=0.00..52240.00 rows=3000000 width=4)
(10 rows)

Time: 1.091 ms
postgres=# select count(1) from t1 where exists(select 1 from t2 where t2.t1_f1=t1.f1);         
 count  
--------
 500000
(1 row)

Time: 3779.401 ms (00:03.779)
```

```
postgres=# set work_mem to '128MB';
SET
Time: 0.368 ms
postgres=# explain  select count(1) from t1 where exists(select 1 from t2 where t2.t1_f1=t1.f1);
                                                    QUERY PLAN                                                    
------------------------------------------------------------------------------------------------------------------
 Finalize Aggregate  (cost=101763.76..101763.77 rows=1 width=8)
   ->  Remote Subquery Scan on all (dn001,dn002)  (cost=101763.75..101763.76 rows=1 width=0)
         ->  Partial Aggregate  (cost=101663.75..101663.76 rows=1 width=8)
               ->  Hash Join  (cost=89660.00..101663.75 rows=505421 width=0)
                     Hash Cond: (t2.t1_f1 = t1.f1)
                     ->  Remote Subquery Scan on all (dn001,dn002)  (cost=59840.00..69443.00 rows=505421 width=4)
                           Distribute results by S: t1_f1
                           ->  HashAggregate  (cost=59740.00..64794.21 rows=505421 width=4)
                                 Group Key: t2.t1_f1
                                 ->  Seq Scan on t2  (cost=0.00..52240.00 rows=3000000 width=4)
                     ->  Hash  (cost=17420.00..17420.00 rows=1000000 width=4)
                           ->  Seq Scan on t1  (cost=0.00..17420.00 rows=1000000 width=4)
(12 rows)

Time: 4.739 ms
postgres=# select count(1) from t1 where exists(select 1 from t2 where t2.t1_f1=t1.f1);         
 count  
--------
 500000
(1 row)

Time: 1942.037 ms (00:01.942)
postgres=# 
```

大约有一倍性能的提升
