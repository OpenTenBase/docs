# Advanced Use

> In the [Quick Start](01-quickstart.md) article, we introduced the architecture, source code compilation and installation, cluster running status, startup and shutdown, and other contents of OpenTenBase.
>
> In [Application Access](02-access.md), we introduced how applications can connect to OpenTenBase databases for operations such as database creation, table creation, data import, and querying.
>
> In [Basic Use](03-basic-use.md), we introduce the creation of shard tables, hot and cold partition tables, replication tables, and basic DML operations unique to OpenTenBase.
>
> This article will continue to introduce the advanced usage operations of OpenTenBase, which includes the use of various window functions, Json/Jsonb, cursors, transactions, locks, and more.

## 1.Window Function

### 1.1.Environmental preparation

```
drop table if  exists bills ;
create table bills 
(
  id serial not null,
  goodsdesc text not null,
  beginunit text not null,
  begincity text not null,
  pubtime timestamp not null,
  amount float8 not null default 0,
  primary key (id)
) distribute by shard(id) to group default_group;

COMMENT ON TABLE bills is 'bills';
COMMENT ON COLUMN bills.id IS 'id';
COMMENT ON COLUMN bills.goodsdesc IS 'cargo_name';
COMMENT ON COLUMN bills.beginunit IS 'begin_state';
COMMENT ON COLUMN bills.begincity IS 'begin_city';
COMMENT ON COLUMN bills.pubtime IS 'publish_time';
COMMENT ON COLUMN bills.amount IS 'amount';

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'cloths','Hainan','Sanya','2015-10-05 09:32:01',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'building_equipment','Fujian','Sanming','2015-10-05 07:21:22',ROUND((random()*10000)::NUMERIC,2)); 

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'equipment','Fujian','Sanming','2015-10-05 11:21:54',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'general_cargo','Fujian','Sanming','2015-10-05 15:19:17',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'5 0forklift,dump_truck','Henan','Sanmenxia','2015-10-05 07:53:13',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'mushroom _1kg','Henan','Sanmenxia','2015-10-05 10:38:29',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'rotary_excavation_accessory_38t','Henan','Sanmenxia','2015-10-05 10:48:38',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'rotary_excavation_accessory_35t','Henan','Sanmenxia','2015-10-05 10:48:38',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'rotary_excavation_accessory_39t','Henan','Sanmenxia','2015-10-05 11:38:38',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'equipment','Shanghai','Shanghai','2015-10-05 07:59:35',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'general_cargo_40t_with_13m_semi_hanging','Shanghai','Shanghai','2015-10-05 08:13:59',ROUND((random()*10000)::NUMERIC,2));
```

### 1.2.row_number()--Return line number without grouping


```
postgres=# select row_number() over(),* from bills limit 2;  
 row_number | id | goodsdesc | beginunit | begincity |       pubtime       | amount  
------------+----+-----------+-----------+-----------+---------------------+---------
          1 |  1 | cloths      | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
          2 |  2 | building_equipment  | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
(2 rows)

postgres=# select row_number() over(),* from bills limit 2 offset 2; 
 row_number | id |       goodsdesc       | beginunit | begincity |       pubtime       | amount  
------------+----+-----------------------+-----------+-----------+---------------------+---------
          3 |  6 | 5 0forklift,dump_truck | Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
          4 |  8 | rotary_excavation_accessory_38t          | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
(2 rows)
```

### 1.3.row_number()--Return line number,sorting by amount

```
postgres=# select row_number() over(order by amount),* from bills;
 row_number | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
------------+----+------------------------+-----------+-----------+---------------------+---------
          1 | 11 | equipment             | Shanghai  | Shanghai   | 2015-10-05 07:59:35 |  971.54
          2 |  6 | 5 0forklift,dump_truck| Henan     | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
          3 |  4 | general_cargo         | Fujian    | Sanming    | 2015-10-05 15:19:17 | 1316.27
          4 |  1 | cloths                | Hainan    | Sanya      | 2015-10-05 09:32:01 | 1915.86
          5 |  2 | building_equipment    | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
          6 |  7 | mushroom _1kg         | Henan     | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
          7 |  8 | rotary_excavation_accessory_38t | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
          8 | 10 | rotary_excavation_accessory_39t | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
          9 |  3 | equipment             | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
         10 |  9 | rotary_excavation_accessory_35t | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
         11 |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
(11 rows)
```

### 1.4.row_number()--Return line number,group by begincity,sorting by pubtime,note that the green record line numbers are uninterrupted.

![OpenTenBase_shard general table description](images/1.4row_number.png)

### 1.5.rank()--Return line number,When the comparison value is repeated, the line number is repeated and interrupted, which returns 1, 2, 3, 3, 5...

![OpenTenBase_shard general table description](images/1.5rank.png)

### 1.6.dance_rank()--Return the line number. When the comparison value is repeated, the line number is repeated but not interrupted, that is, return 1, 2, 3, 3, 4...

![OpenTenBase_shard general table description](images/1.6dance_rank.png)

### 1.7.percent_rank()--Starting from the current, calculate the proportion in the group (line number -1) * (1/(total number of records -1))

```
postgres=# select percent_rank() over(partition by begincity order by id),* from bills;  
 percent_rank | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
--------------+----+------------------------+-----------+-----------+---------------------+---------
            0 |  1 | cloths                | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
            0 |  2 | building_equipment    | Fujian    | Sanming  | 2015-10-05 07:21:22 | 2022.31
          0.5 |  3 | equipment             | Fujian    | Sanming  | 2015-10-05 11:21:54 | 8771.11
            1 |  4 | general_cargo         | Fujian    | Sanming  | 2015-10-05 15:19:17 | 1316.27
            0 |  6 | 5 0forklift,dump_truck| Henan     | Sanmenxia| 2015-10-05 07:53:13 |  1030.9
         0.25 |  7 | mushroom _1kg         | Henan    | Sanmenxia | 2015-10-05 10:38:29 | 4182.68
          0.5 |  8 | rotary_excavation_accessory_38t | Henan | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
         0.75 |  9 | rotary_excavation_accessory_35t | Henan | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
            1 | 10 | rotary_excavation_accessory_39t | Henan | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
            0 |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai   | Shanghai    | 2015-10-05 08:13:59 | 9886.15
            1 | 11 | equipment              | Shanghai  | Shanghai    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.8.cume_dist()--Return the number of rows divided by the recorded value

```
postgres=# select ROUND((cume_dist() over(partition by begincity order by id))::NUMERIC,2) AS cume_dist,* from bills;   
 cume_dist | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
-----------+----+------------------------+-----------+-----------+---------------------+---------
      1.00 |  1 | cloths                | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
      0.33 |  2 | building_equipment    | Fujian    | Sanming  | 2015-10-05 07:21:22 | 2022.31
      0.67 |  3 | equipment             | Fujian    | Sanming  | 2015-10-05 11:21:54 | 8771.11
      1.00 |  4 | general_cargo         | Fujian    | Sanming  | 2015-10-05 15:19:17 | 1316.27
      0.20 |  6 | 5 0forklift,dump_truck| Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
      0.40 |  7 | mushroom _1kg         | Henan    | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
      0.60 |  8 | rotary_excavation_accessory_38t | Henan | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
      0.80 |  9 | rotary_excavation_accessory_35t | Henan | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
      1.00 | 10 | rotary_excavation_accessory_39t | Henan | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
      0.50 |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai   | Shanghai    | 2015-10-05 08:13:59 | 9886.15
      1.00 | 11 | equipment             | Shanghai  | Shanghai   | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.9.ntile(Number of groups)--Make all records as evenly distributed as possible

```
postgres=# select ntile(2) over(partition by begincity order by id),* from bills;  
 ntile | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
-------+----+------------------------+-----------+-----------+---------------------+---------
     1 |  1 | cloths                | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
     1 |  2 | building_equipment    | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
     1 |  3 | equipment             | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
     2 |  4 | general_cargo         | Fujian    | Sanming    | 2015-10-05 15:19:17 | 1316.27
     1 |  6 | 5 0forklift,dump_truck| Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
     1 |  7 | mushroom _1kg         | Henan    | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
     1 |  8 | rotary_excavation_accessory_38t | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
     2 |  9 | rotary_excavation_accessory_35t | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
     2 | 10 | rotary_excavation_accessory_39t | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
     1 |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
     2 | 11 | equipment             | Shanghai    | Shanghai    | 2015-10-05 07:59:35 |  971.54
(11 rows)

postgres=# select ntile(3) over(partition by begincity order by id),* from bills;  
 ntile | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
-------+----+------------------------+-----------+-----------+---------------------+---------
     1 |  1 | cloths                | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
     1 |  2 | building_equipment    | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
     2 |  3 | equipment             | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
     3 |  4 | general_cargo         | Fujian    | Sanming    | 2015-10-05 15:19:17 | 1316.27
     1 |  6 | 5 0forklift,dump_truck| Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
     1 |  7 | mushroom _1kg         | Henan    | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
     2 |  8 | rotary_excavation_accessory_38t | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
     2 |  9 | rotary_excavation_accessory_35t | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
     3 | 10 | rotary_excavation_accessory_39t | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
     1 |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
     2 | 11 | equipment             | Shanghai    | Shanghai    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.10.lag(value any[, offset interger [,default any]])--Return offset value

Offset integer is the offset value. When positive, it takes the leading value, when negative, it takes the trailing value, and when no value is found, it is replaced with default

```
postgres=# select lag(amount,1,null) over(partition by begincity order by id),* from bills;   
   lag   | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
---------+----+------------------------+-----------+-----------+---------------------+---------
         |  1 | cloths                   | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
         |  2 | building_equipment               | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
 2022.31 |  3 | equipment                   | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
 8771.11 |  4 | general_cargo                   | Fujian    | Sanming    | 2015-10-05 15:19:17 | 1316.27
         |  6 | 5 0forklift,dump_truck  | Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
  1030.9 |  7 | mushroom _1kg           | Henan    | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
 4182.68 |  8 | rotary_excavation_accessory_38t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
 5365.04 |  9 | rotary_excavation_accessory_35t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
 9621.37 | 10 | rotary_excavation_accessory_39t           | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
         |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
 9886.15 | 11 | equipment                   | Shanghai    | Shanghai    | 2015-10-05 07:59:35 |  971.54
(11 rows)

postgres=# select lag(amount,2,0::float8) over(partition by begincity order by id),* from bills;  
   lag   | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
---------+----+------------------------+-----------+-----------+---------------------+---------
       0 |  1 | cloths                   | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
       0 |  2 | building_equipment               | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
       0 |  3 | equipment                   | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
 2022.31 |  4 | general_cargo                   | Fujian    | Sanming    | 2015-10-05 15:19:17 | 1316.27
       0 |  6 | 5 0forklift,dump_truck  | Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
       0 |  7 | mushroom _1kg           | Henan    | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
  1030.9 |  8 | rotary_excavation_accessory_38t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
 4182.68 |  9 | rotary_excavation_accessory_35t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
 5365.04 | 10 | rotary_excavation_accessory_39t           | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
       0 |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
       0 | 11 | equipment                   | Shanghai    | Shanghai    | 2015-10-05 07:59:35 |  971.54
(11 rows)

postgres=# select lag(amount,-2,0::float8) over(partition by begincity order by id),* from bills;
   lag   | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
---------+----+------------------------+-----------+-----------+---------------------+---------
       0 |  1 | cloths                   | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
 1316.27 |  2 | building_equipment               | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
       0 |  3 | equipment                   | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
       0 |  4 | general_cargo                   | Fujian    | Sanming    | 2015-10-05 15:19:17 | 1316.27
 5365.04 |  6 | 5 0forklift,dump_truck  | Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
 9621.37 |  7 | mushroom _1kg           | Henan    | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
  8290.5 |  8 | rotary_excavation_accessory_38t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
       0 |  9 | rotary_excavation_accessory_35t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
       0 | 10 | rotary_excavation_accessory_39t           | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
       0 |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
       0 | 11 | equipment                   | Shanghai    | Shanghai    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.11.lead(value any [,offset integer [, default any]] )--Return offset value

Offset integer is the offset value. When positive, it takes the leading value, when negative, it takes the trailing value, and when no value is found, it is replaced with default

```
postgres=# select lead(amount,2,null) over(partition by begincity order by id),* from bills;
  lead   | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
---------+----+------------------------+-----------+-----------+---------------------+---------
         |  1 | cloths                   | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
 1316.27 |  2 | building_equipment               | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
         |  3 | equipment                   | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
         |  4 | general_cargo                   | Fujian    | Sanming    | 2015-10-05 15:19:17 | 1316.27
 5365.04 |  6 | 5 0forklift,dump_truck  | Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
 9621.37 |  7 | mushroom _1kg           | Henan    | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
  8290.5 |  8 | rotary_excavation_accessory_38t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
         |  9 | rotary_excavation_accessory_35t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
         | 10 | rotary_excavation_accessory_39t           | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
         |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
         | 11 | equipment                   | Shanghai    | Shanghai    | 2015-10-05 07:59:35 |  971.54
(11 rows)

postgres=# select lead(amount,-2,null) over(partition by begincity order by id),* from bills;
  lead   | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
---------+----+------------------------+-----------+-----------+---------------------+---------
         |  1 | cloths                   | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
         |  2 | building_equipment               | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
         |  3 | equipment                   | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
 2022.31 |  4 | general_cargo                   | Fujian    | Sanming    | 2015-10-05 15:19:17 | 1316.27
         |  6 | 5 0forklift,dump_truck  | Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
         |  7 | mushroom _1kg           | Henan    | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
  1030.9 |  8 | rotary_excavation_accessory_38t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
 4182.68 |  9 | rotary_excavation_accessory_35t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
 5365.04 | 10 | rotary_excavation_accessory_39t           | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
         |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
         | 11 | equipment                   | Shanghai    | Shanghai    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```


### 1.12.first_value(value any)--Return the first value

```
postgres=# select first_value(amount) over(partition by begincity order by  id),* from bills;
 first_value | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
-------------+----+------------------------+-----------+-----------+---------------------+---------
     1915.86 |  1 | cloths                   | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
     2022.31 |  2 | building_equipment               | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
     2022.31 |  3 | equipment                   | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
     2022.31 |  4 | general_cargo                   | Fujian    | Sanming    | 2015-10-05 15:19:17 | 1316.27
      1030.9 |  6 | 5 0forklift,dump_truck  | Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
      1030.9 |  7 | mushroom _1kg           | Henan    | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
      1030.9 |  8 | rotary_excavation_accessory_38t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
      1030.9 |  9 | rotary_excavation_accessory_35t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
      1030.9 | 10 | rotary_excavation_accessory_39t           | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
     9886.15 |  5 | 普货40吨需13米半挂一辆 | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
     9886.15 | 11 | equipment                   | Shanghai    | Shanghai    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.13.last_value(value any)--Return the last value

``` 
postgres=# select last_value(amount) over(partition by begincity order by pubtime),* FROM bills;  
 last_value | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
------------+----+------------------------+-----------+-----------+---------------------+---------
    1915.86 |  1 | cloths                   | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
    2022.31 |  2 | building_equipment               | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
    8771.11 |  3 | equipment                   | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
    1316.27 |  4 | general_cargo                   | Fujian    | Sanming    | 2015-10-05 15:19:17 | 1316.27
     1030.9 |  6 | 5 0forklift,dump_truck  | Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
    4182.68 |  7 | mushroom _1kg           | Henan    | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
    9621.37 |  8 | rotary_excavation_accessory_38t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
    9621.37 |  9 | rotary_excavation_accessory_35t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
     8290.5 | 10 | rotary_excavation_accessory_39t           | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
     971.54 | 11 | equipment                   | Shanghai    | Shanghai    | 2015-10-05 07:59:35 |  971.54
    9886.15 |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
(11 rows)

postgres=# select last_value(amount) over(partition by begincity),* FROM bills;
 last_value | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
------------+----+------------------------+-----------+-----------+---------------------+---------
    1915.86 |  1 | cloths                   | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
    1316.27 |  2 | building_equipment               | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
    1316.27 |  3 | equipment                   | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
    1316.27 |  4 | general_cargo                   | Fujian    | Sanming    | 2015-10-05 15:19:17 | 1316.27
    9621.37 |  7 | mushroom _1kg           | Henan    | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
    9621.37 | 10 | rotary_excavation_accessory_39t           | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
    9621.37 |  6 | 5 0forklift,dump_truck  | Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
    9621.37 |  8 | rotary_excavation_accessory_38t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
    9621.37 |  9 | rotary_excavation_accessory_35t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
     971.54 |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
     971.54 | 11 | equipment                   | Shanghai    | Shanghai    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

Note that not to add the order by id parameter. By default, adding the order by parameter will stack continuously from the starting value of the group,
Until the current value (not the current record) is different, ignoring the order by parameter will result in the entire group. By modifying the statistical range of the grouping, the last value of the order by parameter can be obtained

```
postgres=# select last_value(amount) over(partition by begincity order by id range between unbounded preceding and unbounded following),* FROM bills;
 last_value | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
------------+----+------------------------+-----------+-----------+---------------------+---------
    1915.86 |  1 | cloths                   | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
    1316.27 |  2 | building_equipment               | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
    1316.27 |  3 | equipment                   | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
    1316.27 |  4 | general_cargo                   | Fujian    | Sanming    | 2015-10-05 15:19:17 | 1316.27
     8290.5 |  6 | 5 0forklift,dump_truck  | Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
     8290.5 |  7 | mushroom _1kg           | Henan    | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
     8290.5 |  8 | rotary_excavation_accessory_38t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
     8290.5 |  9 | rotary_excavation_accessory_35t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
     8290.5 | 10 | rotary_excavation_accessory_39t           | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
     971.54 |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
     971.54 | 11 | equipment                   | Shanghai    | Shanghai    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.14.nth_value(value any, nth integer):Returns the specified value in the window frame

```
postgres=# select nth_value(amount,2) over(partition by begincity order by id),* from bills;
 nth_value | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
-----------+----+------------------------+-----------+-----------+---------------------+---------
           |  1 | cloths                   | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
           |  2 | building_equipment               | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
   8771.11 |  3 | equipment                   | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
   8771.11 |  4 | general_cargo                   | Fujian    | Sanming    | 2015-10-05 15:19:17 | 1316.27
           |  6 | 5 0forklift,dump_truck  | Henan    | Sanmenxia  | 2015-10-05 07:53:13 |  1030.9
   4182.68 |  7 | mushroom _1kg           | Henan    | Sanmenxia  | 2015-10-05 10:38:29 | 4182.68
   4182.68 |  8 | rotary_excavation_accessory_38t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 5365.04
   4182.68 |  9 | rotary_excavation_accessory_35t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
   4182.68 | 10 | rotary_excavation_accessory_39t           | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
           |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
    971.54 | 11 | equipment                   | Shanghai    | Shanghai    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.15.Calculate the total shipping cost and average shipping cost per order for each city

```
postgres=# select sum(amount) over(partition by begincity),avg(amount) over(partition by begincity),begincity,amount from bills;
   sum    |       avg        | begincity | amount  
----------+------------------+-----------+---------
  1915.86 |          1915.86 | Sanya    | 1915.86
 12109.69 | 4036.56333333333 | Sanming    | 2022.31
 12109.69 | 4036.56333333333 | Sanming    | 8771.11
 12109.69 | 4036.56333333333 | Sanming    | 1316.27
 28490.49 |         5698.098 | Sanmenxia  | 4182.68
 28490.49 |         5698.098 | Sanmenxia  |  8290.5
 28490.49 |         5698.098 | Sanmenxia  |  1030.9
 28490.49 |         5698.098 | Sanmenxia  | 5365.04
 28490.49 |         5698.098 | Sanmenxia  | 9621.37
 10857.69 |         5428.845 | Shanghai    | 9886.15
 10857.69 |         5428.845 | Shanghai    |  971.54
(11 rows)
```

### 1.16.The use of window function aliases

```
postgres=# select sum(amount) over w,avg(amount) over w,begincity,amount from bills window w as (partition by begincity);
   sum    |       avg        | begincity | amount  
----------+------------------+-----------+---------
  1915.86 |          1915.86 | Sanya    | 1915.86
 12109.69 | 4036.56333333333 | Sanming    | 2022.31
 12109.69 | 4036.56333333333 | Sanming    | 8771.11
 12109.69 | 4036.56333333333 | Sanming    | 1316.27
 28490.49 |         5698.098 | Sanmenxia  | 4182.68
 28490.49 |         5698.098 | Sanmenxia  |  8290.5
 28490.49 |         5698.098 | Sanmenxia  |  1030.9
 28490.49 |         5698.098 | Sanmenxia  | 5365.04
 28490.49 |         5698.098 | Sanmenxia  | 9621.37
 10857.69 |         5428.845 | Shanghai    | 9886.15
 10857.69 |         5428.845 | Shanghai    |  971.54
(11 rows)
```

### 1.17.Get the top two shipping orders for each city


```
postgres=# select * from (select row_number() over(partition by begincity order by amount desc),* from bills) where row_number<3;     
 row_number | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
------------+----+------------------------+-----------+-----------+---------------------+---------
          1 |  1 | cloths                   | Hainan    | Sanya    | 2015-10-05 09:32:01 | 1915.86
          1 |  3 | equipment                   | Fujian    | Sanming    | 2015-10-05 11:21:54 | 8771.11
          2 |  2 | building_equipment               | Fujian    | Sanming    | 2015-10-05 07:21:22 | 2022.31
          1 |  9 | rotary_excavation_accessory_35t           | Henan    | Sanmenxia  | 2015-10-05 10:48:38 | 9621.37
          2 | 10 | rotary_excavation_accessory_39t           | Henan    | Sanmenxia  | 2015-10-05 11:38:38 |  8290.5
          1 |  5 | general_cargo_40t_with_13m_semi_hanging | Shanghai    | Shanghai    | 2015-10-05 08:13:59 | 9886.15
          2 | 11 | equipment                   | Shanghai    | Shanghai    | 2015-10-05 07:59:35 |  971.54
(7 rows)
```

## 2.The use of json/jsonb

OpenTenBase is not just a distributed relational database system, but it also supports non relational data types such as json, which are used to store json (JavaScript Object Notation) data. This type of data can also be stored as text, but the advantage of json data types is that they can force every stored value to comply with json rules. There are also many json related functions and operators that can be used to store data in these data types. json data types include json and jsonb. They accept exactly the same set of values as input. The main practical difference is efficiency. The json data type stores an accurate copy of the input text, and the processing function must parse the data again every time it is executed. The JSONB data is stored in a decomposed binary format, which is slightly slower to input as additional conversions are required. But jsonb is much faster in processing because it does not require parsing. jsonb also supports indexing, which is a remarkable advantage.

### 2.1.The use of json

#### 2.1.1.Create a json type table

```
postgres=# create table t_json(id int,f_json json);
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
```

##### 2.1.2.Insert data

```
postgres=# insert into t_json values(1,'{"col1":1,"col2":"opentenbase"}');
INSERT 0 1
postgres=# insert into t_json values(2,'{"col1":1,"col2":"opentenbase","col3":"pgxz"}');
INSERT 0 1
postgres=# select * from t_json;
 id |                 f_json                  
----+-----------------------------------------
  1 | {"col1":1,"col2":"opentenbase"}
  2 | {"col1":1,"col2":"opentenbase","col3":"pgxz"}
(2 rows)
```

#### 2.1.3.Get json object field by key

```
postgres=# select f_json ->'col2' as col2 ,f_json -> 'col3' as col3 from t_json;  
  col2   |  col3  
---------+--------
 "opentenbase" | 
 "opentenbase" | "pgxz"
(2 rows)
```

#### 2.1.4.Get data value by text type

```
postgres=# select f_json ->>'col2' as col2 ,f_json ->> 'col3' as col3 from t_json;
 col2  | col3 
-------+------
 opentenbase | 
 opentenbase | pgxz
(2 rows)

postgres=# select f_json ->>'col2' as col2 ,f_json ->> 'col3' as col3 from t_json where f_json ->> 'col3' is not null;
 col2  | col3 
-------+------
 opentenbase | pgxz
(1 row)
```

### 2.2.The use of jsonb

#### 2.2.1.Create a jsonb type table

```
postgres=# create table t_jsonb(id int,f_jsonb jsonb);
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
postgres=# 
```

#### 2.2.2.Insert data

```
postgres=# insert into t_jsonb values(1,'{"col1":1,"col2":"opentenbase"}');
INSERT 0 1
postgres=# insert into t_jsonb values(2,'{"col1":1,"col2":"opentenbase","col3":"pgxz"}');
INSERT 0 1

postgres=# select * from t_jsonb;
 id |                   f_jsonb                    
----+----------------------------------------------
  1 | {"col1": 1, "col2": "opentenbase"}
  2 | {"col1": 1, "col2": "opentenbase", "col3": "pgxz"}
(2 rows)
```

-- When inserting jsonb, duplicate keys will be removed, as shown below

```
postgres=# insert into t_jsonb values(3,'{"col1":1,"col2":"opentenbase","col2":"pgxz"}');
INSERT 0 1
postgres=# select * from t_jsonb;
 id |                   f_jsonb                    
----+----------------------------------------------
  1 | {"col1": 1, "col2": "opentenbase"}
  3 | {"col1": 1, "col2": "pgxz"}
  2 | {"col1": 1, "col2": "opentenbase", "col3": "pgxz"}
(3 rows)
```

#### 2.2.3.Update data

-- Add element

```
postgres=# update t_jsonb set f_jsonb = f_jsonb || '{"col3":"pgxz"}'::jsonb where id=1;  
UPDATE 1
```

-- Update previous element

```
postgres=# update t_jsonb set f_jsonb = f_jsonb || '{"col2":"opentenbase"}'::jsonb where id=3;     
UPDATE 1

postgres=# select * from t_jsonb;
 id |                   f_jsonb                    
----+----------------------------------------------
  2 | {"col1": 1, "col2": "opentenbase", "col3": "pgxz"}
  1 | {"col1": 1, "col2": "opentenbase", "col3": "pgxz"}
  3 | {"col1": 1, "col2": "opentenbase"}
(3 rows)
```

-- Delete a key

```
postgres=# update t_jsonb set f_jsonb = f_jsonb - 'col3';    
UPDATE 3

postgres=# select * from t_jsonb;
 id |           f_jsonb            
----+------------------------------
  2 | {"col1": 1, "col2": "opentenbase"}
  1 | {"col1": 1, "col2": "opentenbase"}
  3 | {"col1": 1, "col2": "opentenbase"}
(3 rows)
```

#### 2.2.4.jsonb_set()--Update data by function

```
jsonb_set(target jsonb, path text[], new_value jsonb, [create_missing boolean]) 
```

Notice: Target refers to the data source to be updated, path refers to the path, new_value refers to the updated key value, create.missing value is true to add if the key does not exist, and create.missing value is false to not add if the key does not exist.

```
postgres=# update t_jsonb set f_jsonb = jsonb_set( f_jsonb , '{col}' , '"pgxz"' , true ) where id=1;
UPDATE 1
postgres=# update t_jsonb set f_jsonb = jsonb_set( f_jsonb , '{col}' , '"pgxz"' , false ) where id=2;         
UPDATE 1
postgres=# update t_jsonb set f_jsonb = jsonb_set( f_jsonb , '{col2}' , '"pgxz"' , false ) where id=3;          
UPDATE 1
postgres=# select * from t_jsonb;
 id |                   f_jsonb                   
----+---------------------------------------------
  1 | {"col": "pgxz", "col1": 1, "col2": "opentenbase"}
  2 | {"col1": 1, "col2": "opentenbase"}
  3 | {"col1": 1, "col2": "pgxz"}
(3 rows)
```

### 2.3.The use of jsonb function

#### 2.3.1.jsonb_each()--Transform json object into key:value

```
postgres=# select  f_jsonb  from t_jsonb where id=1;
                   f_jsonb                   
---------------------------------------------
 {"col": "pgxz", "col1": 1, "col2": "opentenbase"}
(1 row)

postgres=#  select * from  jsonb_each((select  f_jsonb  from t_jsonb where id=1)); 
 key  |  value  
------+---------
 col  | "pgxz"
 col1 | 1
 col2 | "opentenbase"
(3 rows)
```

#### 2.3.2.jsonb_each_text()--Transform json object into key:value(text type)

```
postgres=#  select * from  jsonb_each_text((select  f_jsonb  from t_jsonb where id=1)); 
 key  | value 
------+-------
 col  | pgxz
 col1 | 1
 col2 | opentenbase
(3 rows)
```

#### 2.3.3.row_to_json()--Transform a row of data into a json object

```
postgres=# \d+ opentenbase
                                    Table "public.opentenbase"
  Column  |  Type   | Collation | Nullable | Default | Storage  | Stats target | Description 
----------+---------+-----------+----------+---------+----------+--------------+-------------
 id       | integer |           | not null |         | plain    |              | 
 nickname | text    |           |          |         | extended |              | 
Indexes:
    "opentenbase_pkey" PRIMARY KEY, btree (id)
Distribute By: SHARD(id)
Location Nodes: ALL DATANODES

postgres=# select * from opentenbase;
 id | nickname 
----+----------
  1 | opentenbase
  2 | pgxz
(2 rows)

postgres=# select row_to_json(opentenbase) from opentenbase;
         row_to_json         
-----------------------------
 {"id":1,"nickname":"opentenbase"}
 {"id":2,"nickname":"pgxz"}
(2 rows)
```

#### 2.3.4.json_object_keys()--Return all keys of an object

```
postgres=#  select * from json_object_keys((select  f_jsonb  from t_jsonb where id=1)::json); 
 json_object_keys 
------------------
 col
 col1
 col2
(3 rows)
```

### 2.4.The use of jsonb index

OpenTenBase provides a GIN index for document jsonb, which can be effectively used to search for keys or key value pairs that appear in a large number of jsonb documents (data).

#### 2.4.1.Create a jsonb index

```
postgres=# create index t_jsonb_f_jsonb_idx on t_jsonb using gin(f_jsonb);
CREATE INDEX

postgres=# \d+ t_jsonb
                                   Table "public.t_jsonb"
 Column  |  Type   | Collation | Nullable | Default | Storage  | Stats target | Description 
---------+---------+-----------+----------+---------+----------+--------------+-------------
 id      | integer |           |          |         | plain    |              | 
 f_jsonb | jsonb   |           |          |         | extended |              | 
Indexes:
    "t_jsonb_f_jsonb_idx" gin (f_jsonb)
Distribute By: SHARD(id)
Location Nodes: ALL DATANODES
```

#### 2.4.2.Test the performance of queries

```
postgres=# select count(1) from t_jsonb;
  count   
----------
 10000000
(1 row)

postgres=# analyze t_jsonb;
ANALYZE
```

-- when there's no index overhead

```
postgres=# select * from t_jsonb where f_jsonb @> '{"col1":9999}';
  id  |            f_jsonb             
------+--------------------------------
 9999 | {"col1": 9999, "col2": "9999"}
 9999 | {"col1": 9999, "col2": "9999"}
 9999 | {"col1": 9999, "col2": "9999"}
 9999 | {"col1": 9999, "col2": "9999"}
 9999 | {"col1": 9999, "col2": "9999"}
(5 rows)

Time: 2473.488 ms (00:02.473)
```

-- when there is index overhead

```
postgres=# select * from t_jsonb where f_jsonb @> '{"col1":9999}';
  id  |            f_jsonb             
------+--------------------------------
 9999 | {"col1": 9999, "col2": "9999"}
 9999 | {"col1": 9999, "col2": "9999"}
 9999 | {"col1": 9999, "col2": "9999"}
 9999 | {"col1": 9999, "col2": "9999"}
 9999 | {"col1": 9999, "col2": "9999"}
(5 rows)

Time: 217.968 ms
```

## 3.The use of cursor

### 3.1.Define a cursor

```
postgres=# begin;
BEGIN
postgres=#  DECLARE opentenbase_cur SCROLL CURSOR FOR SELECT * from opentenbase ORDER BY id;              
DECLARE CURSOR
```

notice: Cursor must be used in a transaction

### 3.2.Extract the next line data

```
postgres=# DECLARE opentenbase_cur SCROLL CURSOR FOR SELECT * from opentenbase ORDER BY id; 
DECLARE CURSOR
postgres=# FETCH NEXT from opentenbase_cur ;               
 id |  nickname   
----+-------------
  1 | hello opentenbase
(1 row)

postgres=# FETCH NEXT from opentenbase_cur ;
 id | nickname  
----+-----------
  2 | opentenbase好
(1 row)
```

### 3.3.Extract the last line data

```
postgres=# FETCH PRIOR from opentenbase_cur ;      
 id |  nickname   
----+-------------
  1 | hello opentenbase
(1 row)

postgres=# FETCH PRIOR from opentenbase_cur ;
 id | nickname 
----+----------
(0 rows)
```

### 3.4.Extract the last line

```
postgres=# FETCH LAST from opentenbase_cur ;         
 id |  nickname  
----+------------
  5 | opentenbase swap
(1 row)
```

### 3.5.Extract the first line

```
postgres=# FETCH FIRST from opentenbase_cur ;       
 id |  nickname   
----+-------------
  1 | hello opentenbase
(1 row)
```

### 3.6.Extract the Xth line of this query

```
postgres=# FETCH ABSOLUTE 2 from opentenbase_cur ;                
 id | nickname  
----+-----------
  2 | opentenbase good
(1 row)

postgres=# FETCH ABSOLUTE -1 from opentenbase_cur ; 
 id |  nickname  
----+------------
  5 | opentenbase swap
(1 row)

postgres=# FETCH ABSOLUTE -2 from opentenbase_cur ; 
 id |   nickname    
----+---------------
  4 | opentenbase default
(1 row)
```

start from the last line when X is negative.

### 3.7.Extract the Xth line after this line

```
postgres=#  FETCH ABSOLUTE 1 from opentenbase_cur ; 
 id |  nickname   
----+-------------
  1 | hello opentenbase
(1 row)

postgres=# FETCH RELATIVE 2 from opentenbase_cur ;
 id | nickname  
----+-----------
  3 | opentenbase good
(1 row)

postgres=# FETCH RELATIVE 2 from opentenbase_cur ;
 id |  nickname  
----+------------
  5 | opentenbase swap
(1 row)
```

the cursor will be at the previous line after each extraction.

### 3.8.Extract x rows of data forward

```
postgres=# FETCH FORWARD 2 from opentenbase_cur ;             
 id |  nickname   
----+-------------
  1 | hello opentenbase
  2 | opentenbase good
(2 rows)

postgres=# FETCH FORWARD 2 from opentenbase_cur ; 
 id |   nickname    
----+---------------
  3 | opentenbase good
  4 | opentenbase default
(2 rows)
```

### 3.9.Extract all the remaining data forward

```
postgres=# FETCH FORWARD 2 from opentenbase_cur ;    
 id |  nickname   
----+-------------
  1 | hello opentenbase
  2 | opentenbase good
(2 rows)

postgres=# FETCH FORWARD all from opentenbase_cur ;                                         
 id |   nickname    
----+---------------
  3 | opentenbase good
  4 | opentenbase default
  5 | opentenbase swap
(3 rows)
```

### 3.10.Extract x rows of date backwards

```
postgres=# FETCH BACKWARD 2 from opentenbase_cur ;   
 id |   nickname    
----+---------------
  5 | opentenbase swap
  4 | opentenbase default
(2 rows)
```

### 3.11.Extract all the remaining data backwards

```
postgres=# FETCH BACKWARD all from opentenbase_cur ; 
 id |  nickname   
----+-------------
  3 | opentenbase good
  2 | opentenbase good
  1 | hello opentenbase
(3 rows)
```

## 4.The use of transaction

### 4.1.Begin a transaction

```
postgres=# begin;
BEGIN
```

or

```
postgres=# begin TRANSACTION ; 
BEGIN
```

you can also define the level of transaction

```
postgres=# begin transaction isolation level read committed ;
BEGIN
```

### 4.2.Commit transaction

process#1 access 

```
postgres=# begin;
BEGIN
postgres=# delete from opentenbase where id=5;
DELETE 1
postgres=#
postgres=# select * from opentenbase order by id;
 id |   nickname    
----+---------------
  1 | hello opentenbase
  2 | opentenbase good
  3 | opentenbase good
  4 | opentenbase default
```

OpenTenBase also fully supports the ACID feature. If you open another connection query before submitting, you will see 5 records. This is the implementation of OpenTenBase isolation and multi version views, as shown below

process#2 access

```
postgres=# select * from opentenbase order by id;
 id |   nickname    
----+---------------
  1 | hello opentenbase
  2 | opentenbase good
  3 | opentenbase good
  4 | opentenbase default
  5 | opentenbase swap
(5 rows)
```

process#1 commit data

```
postgres=# commit;
COMMIT
postgres=# 
```

process#2 when you query data again, the data committed is already here, this level calls 'read already commit'

```
postgres=# select * from opentenbase order by id;
 id |   nickname    
----+---------------
  1 | hello opentenbase
  2 | opentenbase good
  3 | opentenbase good
  4 | opentenbase default
(4 rows)
```

### 4.3.Rollback transaction

```
postgres=# begin;
BEGIN
postgres=# delete from opentenbase where id in (3,4);
DELETE 2
postgres=# select * from opentenbase;
 id |  nickname   
----+-------------
  1 | hello opentenbase
  2 | opentenbase good
(2 rows)

postgres=# rollback;
ROLLBACK
```

after rollback, the data came back again

```
postgres=# select * from opentenbase;
 id |   nickname    
----+---------------
  1 | hello opentenbase
  2 | opentenbase good
  3 | opentenbase good
  4 | opentenbase default
(4 rows)
```

### 4.4.Transaction read consistency--REPEATABLE READ

This transaction level indicates that the data read by the transaction is consistent from beginning to end, as shown below

\#session1

```
postgres=# create table t_repeatable_read (id int,mc text);
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
postgres=# insert into t_repeatable_read values(1,'opentenbase');
INSERT 0 1

postgres=# begin isolation level repeatable read ;
BEGIN
postgres=# select * from t_repeatable_read ;
 id |  mc   
----+-------
  1 | opentenbase
(1 row)
```

\#session2

```
postgres=# insert into t_repeatable_read values(1,'pgxz'); 
INSERT 0 1
postgres=# select * from t_repeatable_read;
 id |  mc   
----+-------
  1 | opentenbase
  1 | pgxz
(2 rows)
```

\#session1

```
postgres=# select * from t_repeatable_read ;
 id |  mc   
----+-------
  1 | opentenbase
(1 row)

postgres=#
```

### 4.5.The use of row lock in transaction

#### 4.5.1.Environment preparation

```
postgres=# create table t_row_lock(id int,mc text,primary key (id));
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
postgres=# 

postgres=# insert into t_row_lock values(1,'opentenbase'),(2,'pgxz');       
INSERT 0 2
postgres=# select * from t_row_lock;
 id |  mc   
----+-------
  1 | opentenbase
  2 | pgxz
(2 rows)
```

#### 4.5.2.Get lock by update directly

\#session1

```
postgres=# begin;
BEGIN
postgres=# set lock_timeout to 1;
SET
postgres=# update t_row_lock set mc='postgres' where mc='pgxz';
UPDATE 1
postgres=# 
```

\#session2

```
postgres=# begin;
BEGIN
postgres=# set lock_timeout to 1;
SET
postgres=#  update t_row_lock set mc='postgresql' where mc='opentenbase';        
UPDATE 1
postgres=# 
```

Session1 and Session2 above hold row locks for mc=pgxz and mc=opentenbase, respectively

#### 4.5.3.Get by select...for update

\#session1

```
postgres=#  
BEGIN
postgres=# set lock_timeout to 1; 
SET
postgres=# select * from t_row_lock where mc='pgxz' for update;
 id |  mc  
----+------
  2 | pgxz
(1 row)
```

\#session2 

```
postgres=# begin;
BEGIN
postgres=# set lock_timeout to 1; 
SET
postgres=# select * from t_row_lock where mc='opentenbase' for update;
 id |  mc  
----+------
  2 | pgxz
(1 row)
```

Session1 and Session2 above hold row locks for mc=pgxz and mc=opentenbase, respectively

#### 4.5.4.Exclusion lock inspection

```
postgres=# select pid,pg_blocking_pids(pid),wait_event_type,query from pg_stat_activity where wait_event_type = 'Lock' and pid!=pg_backend_pid()
```