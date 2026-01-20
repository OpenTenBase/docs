# Advanced use

> In [Quick start](01-quickstart.md) this article, we introduce the architecture of OpenTenBase, source code compilation and installation, cluster running status, startup and stop, etc. > > In [Application access](02-access.md), we introduced how the application connects to the OpenTenBase database for database creation, table creation, data import, query, and other operations. > > In [Basic use](03-basic-use.md), we introduce the unique shard tables, hot and cold partition tables, the creation of replicated tables, and basic DML operations in OpenTenBase. > > This article will continue to introduce the advanced use and operation of OpenTenBase, including the use of various window functions, Json/Jsonb, cursors, transactions, locks, etc.

## 1. Window function
### 1.1. Environmental preparation


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

COMMENT ON TABLE bills is '运单记录';
COMMENT ON COLUMN bills.id IS 'id号';
COMMENT ON COLUMN bills.goodsdesc IS '货物名称';
COMMENT ON COLUMN bills.beginunit IS '启运省份';
COMMENT ON COLUMN bills.begincity IS '启运城市';
COMMENT ON COLUMN bills.pubtime IS '发布时间';
COMMENT ON COLUMN bills.amount IS '运费';

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'衣服','海南省','三亚市','2015-10-05 09:32:01',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'建筑设备','福建省','三明市','2015-10-05 07:21:22',ROUND((random()*10000)::NUMERIC,2)); 

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'设备','福建省','三明市','2015-10-05 11:21:54',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'普货','福建省','三明市','2015-10-05 15:19:17',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'5 0铲车，后八轮翻斗车','河南省','三门峡市','2015-10-05 07:53:13',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'鲜香菇2000斤','河南省','三门峡市','2015-10-05 10:38:29',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'旋挖附件38吨','河南省','三门峡市','2015-10-05 10:48:38',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'旋挖附件35吨','河南省','三门峡市','2015-10-05 10:48:38',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'旋挖附件39吨','河南省','三门峡市','2015-10-05 11:38:38',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'设备','上海市','上海市','2015-10-05 07:59:35',ROUND((random()*10000)::NUMERIC,2));

INSERT INTO bills(id,goodsdesc,beginunit,begincity,pubtime,amount) 
VALUES(default,'普货40吨需13米半挂一辆','上海市','上海市','2015-10-05 08:13:59',ROUND((random()*10000)::NUMERIC,2));
```

### 1.2. Row _ number () -- Returns the row number without grouping


```
postgres=# select row_number() over(),* from bills limit 2;  
 row_number | id | goodsdesc | beginunit | begincity |       pubtime       | amount  
------------+----+-----------+-----------+-----------+---------------------+---------
          1 |  1 | 衣服      | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
          2 |  2 | 建筑设备  | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
(2 rows)

postgres=# select row_number() over(),* from bills limit 2 offset 2; 
 row_number | id |       goodsdesc       | beginunit | begincity |       pubtime       | amount  
------------+----+-----------------------+-----------+-----------+---------------------+---------
          3 |  6 | 5 0铲车，后八轮翻斗车 | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
          4 |  8 | 旋挖附件38吨          | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
(2 rows)
```

### 1.3. Row _ number () -- Returns the row number, sorted by amount


```
postgres=# select row_number() over(order by amount),* from bills;
 row_number | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
------------+----+------------------------+-----------+-----------+---------------------+---------
          1 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
          2 |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
          3 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
          4 |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
          5 |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
          6 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
          7 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
          8 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
          9 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
         10 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
         11 |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
(11 rows)
```

### 1.4. Row _ number () -- Return the row number, grouped by begincity and sorted by pubtime. Note that the green record row number is uninterrupted.

![OpenTenBase _ shard Common Table Description](images/1.4row_number.png)

### 1.5. Rank () -- Returns the line number. When the value is repeated, the line number is repeated and interrupted, that is, 1, 2, 3, 3, 5..

![OpenTenBase _ shard Common Table Description](images/1.5rank.png)

### 1.6. Dance _ rank () -- Returns the line number. When the value is repeated, the line number is repeated without interruption, that is, 1, 2, 3, 3, 4..

![OpenTenBase _ shard Common Table Description](images/1.6dance_rank.png)

### 1.7, percent _ rank () calculates the proportion in the group from the current (line number-1) * (1/ (total number of records-1))


```
postgres=# select percent_rank() over(partition by begincity order by id),* from bills;  
 percent_rank | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
--------------+----+------------------------+-----------+-----------+---------------------+---------
            0 |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
            0 |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
          0.5 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
            1 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
            0 |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
         0.25 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
          0.5 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
         0.75 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
            1 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
            0 |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
            1 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.8. Cume _ dist () -- Returns the number of rows divided by the record value.


```
postgres=# select ROUND((cume_dist() over(partition by begincity order by id))::NUMERIC,2) AS cume_dist,* from bills;   
 cume_dist | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
-----------+----+------------------------+-----------+-----------+---------------------+---------
      1.00 |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
      0.33 |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
      0.67 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
      1.00 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
      0.20 |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
      0.40 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
      0.60 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
      0.80 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
      1.00 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
      0.50 |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
      1.00 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.9, ntile (number of groups) -- so that all records can be evenly distributed


```
postgres=# select ntile(2) over(partition by begincity order by id),* from bills;  
 ntile | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
-------+----+------------------------+-----------+-----------+---------------------+---------
     1 |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
     1 |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
     1 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
     2 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
     1 |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
     1 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
     1 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
     2 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
     2 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
     1 |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
     2 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(11 rows)

postgres=# select ntile(3) over(partition by begincity order by id),* from bills;  
 ntile | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
-------+----+------------------------+-----------+-----------+---------------------+---------
     1 |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
     1 |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
     2 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
     3 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
     1 |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
     1 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
     2 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
     2 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
     3 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
     1 |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
     2 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.10, lag (value any [, offset integer [, default any]]) -- return the offset value

The offset integer is the offset value. The previous value is taken when the number is positive, and the later value is taken when the number is negative. The default value is used instead when the value is not taken.


```
postgres=# select lag(amount,1,null) over(partition by begincity order by id),* from bills;   
   lag   | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
---------+----+------------------------+-----------+-----------+---------------------+---------
         |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
         |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
 2022.31 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
 8771.11 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
         |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
  1030.9 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
 4182.68 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
 5365.04 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
 9621.37 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
         |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
 9886.15 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(11 rows)

postgres=# select lag(amount,2,0::float8) over(partition by begincity order by id),* from bills;  
   lag   | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
---------+----+------------------------+-----------+-----------+---------------------+---------
       0 |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
       0 |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
       0 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
 2022.31 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
       0 |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
       0 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
  1030.9 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
 4182.68 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
 5365.04 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
       0 |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
       0 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(11 rows)

postgres=# select lag(amount,-2,0::float8) over(partition by begincity order by id),* from bills;
   lag   | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
---------+----+------------------------+-----------+-----------+---------------------+---------
       0 |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
 1316.27 |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
       0 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
       0 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
 5365.04 |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
 9621.37 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
  8290.5 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
       0 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
       0 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
       0 |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
       0 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.11, lead (value any [, offset integer [, default any]]) -- return the offset value

Offset integer is the offset value. When the number is positive, the latter value is taken; when the number is negative, the former value is taken; when the value is not taken, it is replaced by default


```
postgres=# select lead(amount,2,null) over(partition by begincity order by id),* from bills;
  lead   | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
---------+----+------------------------+-----------+-----------+---------------------+---------
         |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
 1316.27 |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
         |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
         |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
 5365.04 |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
 9621.37 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
  8290.5 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
         |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
         | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
         |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
         | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(11 rows)

postgres=# select lead(amount,-2,null) over(partition by begincity order by id),* from bills;
  lead   | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
---------+----+------------------------+-----------+-----------+---------------------+---------
         |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
         |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
         |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
 2022.31 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
         |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
         |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
  1030.9 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
 4182.68 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
 5365.04 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
         |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
         | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.12. First _ value (value any) returns the first value


```
postgres=# select first_value(amount) over(partition by begincity order by  id),* from bills;
 first_value | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
-------------+----+------------------------+-----------+-----------+---------------------+---------
     1915.86 |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
     2022.31 |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
     2022.31 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
     2022.31 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
      1030.9 |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
      1030.9 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
      1030.9 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
      1030.9 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
      1030.9 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
     9886.15 |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
     9886.15 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.13. The last _ value (value any) returns the last value


``` 
postgres=# select last_value(amount) over(partition by begincity order by pubtime),* FROM bills;  
 last_value | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
------------+----+------------------------+-----------+-----------+---------------------+---------
    1915.86 |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
    2022.31 |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
    8771.11 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
    1316.27 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
     1030.9 |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
    4182.68 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
    9621.37 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
    9621.37 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
     8290.5 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
     971.54 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
    9886.15 |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
(11 rows)

postgres=# select last_value(amount) over(partition by begincity),* FROM bills;
 last_value | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
------------+----+------------------------+-----------+-----------+---------------------+---------
    1915.86 |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
    1316.27 |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
    1316.27 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
    1316.27 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
    9621.37 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
    9621.37 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
    9621.37 |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
    9621.37 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
    9621.37 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
     971.54 |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
     971.54 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

Be careful not to add the order by ID. By default, the order by parameter will be added from the starting value of the group until the current value (not the current record) is different. When the order by parameter is ignored, it is the whole group. Next, the order by parameter can take the last value by modifying the statistical range of the group


```
postgres=# select last_value(amount) over(partition by begincity order by id range between unbounded preceding and unbounded following),* FROM bills;
 last_value | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
------------+----+------------------------+-----------+-----------+---------------------+---------
    1915.86 |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
    1316.27 |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
    1316.27 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
    1316.27 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
     8290.5 |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
     8290.5 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
     8290.5 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
     8290.5 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
     8290.5 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
     971.54 |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
     971.54 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.14. Nth _ value (value any, nth integer): Returns the specified value in the window frame.


```
postgres=# select nth_value(amount,2) over(partition by begincity order by id),* from bills;
 nth_value | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
-----------+----+------------------------+-----------+-----------+---------------------+---------
           |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
           |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
   8771.11 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
   8771.11 |  4 | 普货                   | 福建省    | 三明市    | 2015-10-05 15:19:17 | 1316.27
           |  6 | 5 0铲车，后八轮翻斗车  | 河南省    | 三门峡市  | 2015-10-05 07:53:13 |  1030.9
   4182.68 |  7 | 鲜香菇2000斤           | 河南省    | 三门峡市  | 2015-10-05 10:38:29 | 4182.68
   4182.68 |  8 | 旋挖附件38吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 5365.04
   4182.68 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
   4182.68 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
           |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
    971.54 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(11 rows)
```

### 1.15. Count the total freight of each city and the average freight of each order


```
postgres=# select sum(amount) over(partition by begincity),avg(amount) over(partition by begincity),begincity,amount from bills;
   sum    |       avg        | begincity | amount  
----------+------------------+-----------+---------
  1915.86 |          1915.86 | 三亚市    | 1915.86
 12109.69 | 4036.56333333333 | 三明市    | 2022.31
 12109.69 | 4036.56333333333 | 三明市    | 8771.11
 12109.69 | 4036.56333333333 | 三明市    | 1316.27
 28490.49 |         5698.098 | 三门峡市  | 4182.68
 28490.49 |         5698.098 | 三门峡市  |  8290.5
 28490.49 |         5698.098 | 三门峡市  |  1030.9
 28490.49 |         5698.098 | 三门峡市  | 5365.04
 28490.49 |         5698.098 | 三门峡市  | 9621.37
 10857.69 |         5428.845 | 上海市    | 9886.15
 10857.69 |         5428.845 | 上海市    |  971.54
(11 rows)
```

### 1.16. Use of window function alias


```
postgres=# select sum(amount) over w,avg(amount) over w,begincity,amount from bills window w as (partition by begincity);
   sum    |       avg        | begincity | amount  
----------+------------------+-----------+---------
  1915.86 |          1915.86 | 三亚市    | 1915.86
 12109.69 | 4036.56333333333 | 三明市    | 2022.31
 12109.69 | 4036.56333333333 | 三明市    | 8771.11
 12109.69 | 4036.56333333333 | 三明市    | 1316.27
 28490.49 |         5698.098 | 三门峡市  | 4182.68
 28490.49 |         5698.098 | 三门峡市  |  8290.5
 28490.49 |         5698.098 | 三门峡市  |  1030.9
 28490.49 |         5698.098 | 三门峡市  | 5365.04
 28490.49 |         5698.098 | 三门峡市  | 9621.37
 10857.69 |         5428.845 | 上海市    | 9886.15
 10857.69 |         5428.845 | 上海市    |  971.54
(11 rows)
```

### 1.17. Obtain the first two orders of freight in each city


```
postgres=# select * from (select row_number() over(partition by begincity order by amount desc),* from bills) where row_number<3;     
 row_number | id |       goodsdesc        | beginunit | begincity |       pubtime       | amount  
------------+----+------------------------+-----------+-----------+---------------------+---------
          1 |  1 | 衣服                   | 海南省    | 三亚市    | 2015-10-05 09:32:01 | 1915.86
          1 |  3 | 设备                   | 福建省    | 三明市    | 2015-10-05 11:21:54 | 8771.11
          2 |  2 | 建筑设备               | 福建省    | 三明市    | 2015-10-05 07:21:22 | 2022.31
          1 |  9 | 旋挖附件35吨           | 河南省    | 三门峡市  | 2015-10-05 10:48:38 | 9621.37
          2 | 10 | 旋挖附件39吨           | 河南省    | 三门峡市  | 2015-10-05 11:38:38 |  8290.5
          1 |  5 | 普货40吨需13米半挂一辆 | 上海市    | 上海市    | 2015-10-05 08:13:59 | 9886.15
          2 | 11 | 设备                   | 上海市    | 上海市    | 2015-10-05 07:59:35 |  971.54
(7 rows)
```

## 2. Use JSON/JSON B
OpenTenBase is not just a distributed relational database system, but it also supports the non-relational data type JSON, which is used to store JSON (JavaScript Object Notation) data. This data can also be stored as text, but the JSON data type has the advantage of enforcing that each stored value conforms to JSON rules. There are also many JSON-related functions and operators that can be used with data stored in these data types. The JSON data types are JSON and JSON B. They accept exactly the same set of values as input. The main practical difference is efficiency. The JSON data type stores an exact copy of the input text, and the processing function must re-parse the data each time it executes. The jsonb data, on the other hand, is stored in a shredded binary format, which is a little slower to input because of the additional conversion required. But jsonb is much faster at processing because no parsing is required. Indexing is also supported by jsonb, which is another notable advantage.

### 2.1, JSON application
#### 2.1.1. Create a JSON type field table


```
postgres=# create table t_json(id int,f_json json);
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
```

#### 2.1.2 Inserting data

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

#### 2.1.3 Obtain the JSON object field through the key


```
postgres=# select f_json ->'col2' as col2 ,f_json -> 'col3' as col3 from t_json;  
  col2   |  col3  
---------+--------
 "opentenbase" | 
 "opentenbase" | "pgxz"
(2 rows)
```

#### 2.1.4 Obtain the object value in the form of text


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

### 2.2, jsonb application
#### 2.2.1. Create jsonb type field table


```
postgres=# create table t_jsonb(id int,f_jsonb jsonb);
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
postgres=# 
```

#### 2.2.2 Inserting data


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

--jsonb inserts remove duplicate keys, as shown below


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

#### 2.2.3 Updating data

-- Add element


```
postgres=# update t_jsonb set f_jsonb = f_jsonb || '{"col3":"pgxz"}'::jsonb where id=1;  
UPDATE 1
```

-- Update the original element


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

#### 2.2.4 JSON B _ set () function update data


```
jsonb_set(target jsonb, path text[], new_value jsonb, [create_missing boolean]) 
```

Description: target refers to the data source to be updated, path refers to the path, new _ value refers to the updated key value, create _ missing value of true means that the key is added if it does not exist, and create _ missing value of false means that the key is not added if it does not exist.


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

### 2.3. Application of jsonb function
#### 2.3.1. JSON B _ each () Transforms a JSON object into a key and a value


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

#### 2.JSON B _ each _ text () converts a JSON object into a text-type key and value


```
postgres=#  select * from  jsonb_each_text((select  f_jsonb  from t_jsonb where id=1)); 
 key  | value 
------+-------
 col  | pgxz
 col1 | 1
 col2 | opentenbase
(3 rows)
```

#### 2.3.3. Row _ to _ JSON () turns a line of records into a JSON object


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

#### 2.3.4. JSON _ object _ keys () returns all keys in an object


```
postgres=#  select * from json_object_keys((select  f_jsonb  from t_jsonb where id=1)::json); 
 json_object_keys 
------------------
 col
 col1
 col2
(3 rows)
```

### 2.4. Use of JSON B index

OpenTenBase provides a GIN index for jsonb documents, which can be used to efficiently search for keys or key-value pairs that appear in a large number of jsonb documents (data).

#### 2.4.1. Create a JSON B index


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

#### 2.4.2. Test query performance


```
postgres=# select count(1) from t_jsonb;
  count   
----------
 10000000
(1 row)

postgres=# analyze t_jsonb;
ANALYZE

```

-- No index overhead


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
-- There is index overhead


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

## 3. Cursor usage
### 3.1. Define a cursor


```
postgres=# begin;
BEGIN
postgres=#  DECLARE opentenbase_cur SCROLL CURSOR FOR SELECT * from opentenbase ORDER BY id;              
DECLARE CURSOR
```

Note: Cursors need to be used within a transaction


### 3.2. Extract the next line of data


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

### 3.3. Extract the previous row of data


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

### 3.4. Extract the last line


```
postgres=# FETCH LAST from opentenbase_cur ;         
 id |  nickname  
----+------------
  5 | opentenbase swap
(1 row)
```

### 3.5. Extract the first row


```
postgres=# FETCH FIRST from opentenbase_cur ;       
 id |  nickname   
----+-------------
  1 | hello opentenbase
(1 row)
```

### 3.6. Extract row X of the query


```
postgres=# FETCH ABSOLUTE 2 from opentenbase_cur ;                
 id | nickname  
----+-----------
  2 | opentenbase好
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
When X is negative, it is lifted up from the tail


### 3.7. Extract the xth line after the current position


```
postgres=#  FETCH ABSOLUTE 1 from opentenbase_cur ; 
 id |  nickname   
----+-------------
  1 | hello opentenbase
(1 row)

postgres=# FETCH RELATIVE 2 from opentenbase_cur ;
 id | nickname  
----+-----------
  3 | opentenbase好
(1 row)

postgres=# FETCH RELATIVE 2 from opentenbase_cur ;
 id |  nickname  
----+------------
  5 | opentenbase swap
(1 row)

```
Each time the data is fetched, the cursor moves forward

### 3.8. Extract X rows of data forward


```
postgres=# FETCH FORWARD 2 from opentenbase_cur ;             
 id |  nickname   
----+-------------
  1 | hello opentenbase
  2 | opentenbase好
(2 rows)

postgres=# FETCH FORWARD 2 from opentenbase_cur ; 
 id |   nickname    
----+---------------
  3 | opentenbase好
  4 | opentenbase default
(2 rows)
```

### 3.9. Extract all remaining data forward


```
postgres=# FETCH FORWARD 2 from opentenbase_cur ;    
 id |  nickname   
----+-------------
  1 | hello opentenbase
  2 | opentenbase好
(2 rows)

postgres=# FETCH FORWARD all from opentenbase_cur ;                                         
 id |   nickname    
----+---------------
  3 | opentenbase好
  4 | opentenbase default
  5 | opentenbase swap
(3 rows)
```

### 3.10. Extract X rows of data backward


```
postgres=# FETCH BACKWARD 2 from opentenbase_cur ;   
 id |   nickname    
----+---------------
  5 | opentenbase swap
  4 | opentenbase default
(2 rows)
```

### 3.11. Extract all remaining data backwards


```
postgres=# FETCH BACKWARD all from opentenbase_cur ; 
 id |  nickname   
----+-------------
  3 | opentenbase好
  2 | opentenbase好
  1 | hello opentenbase
(3 rows)
```

## 4. Transaction usage
### 4.1. Start a transaction


```
postgres=# begin;
BEGIN
```

Or


```
postgres=# begin TRANSACTION ; 
BEGIN
```


You can also define the level of the transaction


```
postgres=# begin transaction isolation level read committed ;
BEGIN
```

### 4.2. Commit the transaction
Process # 1 Access


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
  2 | opentenbase好
  3 | opentenbase好
  4 | opentenbase default
  
```  
  
OpenTenBase also fully supports the ACID feature. Open another connection query before submission, and you will see five records. This is the implementation of OpenTenBase isolation and multi-version view, as shown below.

Process # 2 Access


```
postgres=# select * from opentenbase order by id;
 id |   nickname    
----+---------------
  1 | hello opentenbase
  2 | opentenbase好
  3 | opentenbase好
  4 | opentenbase default
  5 | opentenbase swap
(5 rows)

```
Process # 1 commits data


```
postgres=# commit;
COMMIT
postgres=# 
```

Process # 2 queries the data again, and now you can see the data that has been submitted. This level is called "Read Submitted".


```
postgres=# select * from opentenbase order by id;
 id |   nickname    
----+---------------
  1 | hello opentenbase
  2 | opentenbase好
  3 | opentenbase好
  4 | opentenbase default
(4 rows)
```

### 4.3. Roll back the transaction


```
postgres=# begin;
BEGIN
postgres=# delete from opentenbase where id in (3,4);
DELETE 2
postgres=# select * from opentenbase;
 id |  nickname   
----+-------------
  1 | hello opentenbase
  2 | opentenbase好
(2 rows)

postgres=# rollback;
ROLLBACK
```

The data came back after Rollback.


```
postgres=# select * from opentenbase;
 id |   nickname    
----+---------------
  1 | hello opentenbase
  2 | opentenbase好
  3 | opentenbase好
  4 | opentenbase default
(4 rows)
```

### 4.4. Transaction read consistency REPEATABLE READ

This transaction level means that the data read is consistent throughout the transaction, as shown below

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

### 4.5. Application of row lock in transaction
#### 4.5.1 Environmental preparation


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

#### 4.5.2. Direct update acquisition

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

Above, session1 and session 2 hold row locks for MC = pgxz and MC = opentenbase, respectively

#### 4.5.3、select... For update get
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

Above, session1 and session 2 hold row locks for MC = pgxz and MC = opentenbase, respectively

#### 4.5.4 Inspection of exclusive lock


```
postgres=# select pid,pg_blocking_pids(pid),wait_event_type,query from pg_stat_activity where wait_event_type = 'Lock' and pid!=pg_backend_pid()
```

