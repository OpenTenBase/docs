# 高级使用

>在[快速入门](01-quickstart.md)文章中我们介绍了 OpenTenBase 的架构、源码编译安装、集群运行状态、启动停止等内容。
>
>在[应用接入](02-access.md)中我们介绍了应用程序连接 OpenTenBase 数据库进行建库、建表、数据导入、查询等操作。
>
>在[基本使用](03-basic-use.md)中我们介绍 OpenTenBase 中特有的shard表、复制表的创建，和基本的DML操作。
>
>本篇将继续介绍OpenTenBase的高级使用操作内容，其中包含了各种窗口函数、Json/Jsonb、游标、事务、锁等的使用。

## 1、窗口函数
### 1.1、环境准备

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

### 1.2、row_number() --返回行号，不分组

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

### 1.3、row_number() --返回行号，按amount排序

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

### 1.4、row_number() --返回行号，按begincity分组，pubtime排序，注意绿色记录行号不间断

![OpenTenBase_shard普通表说明](images/1.4row_number.png)

### 1.5、rank()--返回行号,对比值重复时行号重复并间断，即返回1,2,3,3,5...

![OpenTenBase_shard普通表说明](images/1.5rank.png)

### 1.6、dance_rank()--返回行号,对比值重复时行号重复但不间断，即返回1,2,3,3,4...

![OpenTenBase_shard普通表说明](images/1.6dance_rank.png)

### 1.7、percent_rank()从当前开始，计算在分组中的比例 (行号-1)*(1/(总记录数-1))

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

### 1.8、cume_dist() --返回行数除以记录数值

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

### 1.9、ntile(分组数量)--让所有记录尽可以的均匀分布

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

### 1.10、lag(value any [, offset integer [, default any]] )--返回偏移量值  

offset integer是偏移值，正数时取前值，负数时取后值，没有取到值时用default代替

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

### 1.11、lead(value any [,offset integer [, default any]] )--返回偏移量值  

offset integer是偏移值，正数时取后值，负数时取前值，没有取到值时用default代替  

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

### 1.12、first_value(value any)返回第一值

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

### 1.13、last_value(value any)返回最后值 

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

注意不要加上order by id，默认情况下，带了order by 参数会从分组的起始值开始一直叠加，
直到当前值（不是当前记录）不同为止，当忽略order by 参数则是整个分组。下面通过修改分组的统计范围就可以实现order by参数取最后值  

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

### 1.14、nth_value(value any, nth integer)：返回窗口框架中的指定值

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

### 1.15、统计各个城市的总运费及平均每单的运费

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

### 1.16、窗口函数别名使用

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

### 1.17、获取每个城市运费前两名订单

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

## 2、json/jsonb使用
OpenTenBase不只是一个分布式关系型数据库系统，同时它还支持非关系数据类型JSON，JSON 数据类型是用来存储 JSON（JavaScript Object Notation） 数据的。这种数据也可以被存储为text，但是 JSON 数据类型的 优势在于能强制要求每个被存储的值符合 JSON 规则。 也有很多 JSON 相关的函数和操作符可以用于存储在这些数据类型中的数据。JSON 数据类型有json 和 jsonb。它们接受完全相同的值集合作为输入。主要的实际区别是效率。json数据类型存储输入文本的精准拷贝，处理函数必须在每次执行时必须重新解析该数据。而jsonb数据被存储在一种分解好的二进制格式中，它在输入时要稍慢一些，因为需要做附加的转换。但是 jsonb在处理时要快很多，因为不需要解析。jsonb也支持索引，这也是一个令人瞩目的优势。 

### 2.1、json应用
#### 2.1.1、创建json类型字段表

```
postgres=# create table t_json(id int,f_json json);
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
```

#### 2.1.2、插入数据
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

#### 2.1.3、通过键获得 JSON 对象域

```
postgres=# select f_json ->'col2' as col2 ,f_json -> 'col3' as col3 from t_json;  
  col2   |  col3  
---------+--------
 "opentenbase" | 
 "opentenbase" | "pgxz"
(2 rows)
```

#### 2.1.4、以文本形式获取对象值

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

### 2.2、jsonb应用
#### 2.2.1、创建jsonb类型字段表

```
postgres=# create table t_jsonb(id int,f_jsonb jsonb);
NOTICE:  Replica identity is needed for shard table, please add to this table through "alter table" command.
CREATE TABLE
postgres=# 
```

#### 2.2.2、插入数据

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

--jsonb插入时会移除重复的键，如下所示

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

#### 2.2.3、更新数据

--增加元素

```
postgres=# update t_jsonb set f_jsonb = f_jsonb || '{"col3":"pgxz"}'::jsonb where id=1;  
UPDATE 1
```

--更新原来的元素

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

--删除某个键

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

#### 2.2.4、jsonb_set()函数更新数据 

```
jsonb_set(target jsonb, path text[], new_value jsonb, [create_missing boolean]) 
```

说明：target指要更新的数据源，path指路径，new_value指更新后的键值，create_missing值为true表示如果键不存在则添加，create_missing值为false表示如果键不存在则不添加。

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

### 2.3、jsonb函数应用
#### 2.3.1、jsonb_each()将json对象转变键和值

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

#### 2.3.2、jsonb_each_text()将json对象转变文本类型的键和值

```
postgres=#  select * from  jsonb_each_text((select  f_jsonb  from t_jsonb where id=1)); 
 key  | value 
------+-------
 col  | pgxz
 col1 | 1
 col2 | opentenbase
(3 rows)
```

#### 2.3.3、row_to_json()将一行记录变成一个json对象

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

#### 2.3.4、json_object_keys()返回一个对象中所有的键

```
postgres=#  select * from json_object_keys((select  f_jsonb  from t_jsonb where id=1)::json); 
 json_object_keys 
------------------
 col
 col1
 col2
(3 rows)
```

### 2.4、jsonb索引使用 

OpenTenBase为文档jsonb提供了GIN索引，GIN 索引可以被用来有效地搜索在大量jsonb文档（数据）中出现 的键或者键值对。

#### 2.4.1、创建立jsonb索引

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

#### 2.4.2、测试查询的性能

```
postgres=# select count(1) from t_jsonb;
  count   
----------
 10000000
(1 row)

postgres=# analyze t_jsonb;
ANALYZE

```

--没有索引开销

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
--有索引开销

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

## 3、游标使用
### 3.1、定义一个游标

```
postgres=# begin;
BEGIN
postgres=#  DECLARE opentenbase_cur SCROLL CURSOR FOR SELECT * from opentenbase ORDER BY id;              
DECLARE CURSOR
```

注意：游标需要放在一个事务中使用


### 3.2、提取下一行数据

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

### 3.3、提取前一行数据

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

### 3.4、提取最后一行

```
postgres=# FETCH LAST from opentenbase_cur ;         
 id |  nickname  
----+------------
  5 | opentenbase swap
(1 row)
```

### 3.5、提取第一行

```
postgres=# FETCH FIRST from opentenbase_cur ;       
 id |  nickname   
----+-------------
  1 | hello opentenbase
(1 row)
```

### 3.6、提取该查询的第x行

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
X为负数时则从尾部向上提


### 3.7、提取当前位置后的第x行

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
每提取一次数据，游标的位置都是会前行

### 3.8、向前提取x行数据

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

### 3.9、向前提取剩下的所有数据

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

### 3.10、向后提取x行数据

```
postgres=# FETCH BACKWARD 2 from opentenbase_cur ;   
 id |   nickname    
----+---------------
  5 | opentenbase swap
  4 | opentenbase default
(2 rows)
```

### 3.11、向后提取剩下的所有数据

```
postgres=# FETCH BACKWARD all from opentenbase_cur ; 
 id |  nickname   
----+-------------
  3 | opentenbase好
  2 | opentenbase好
  1 | hello opentenbase
(3 rows)
```

## 4、事务使用
### 4.1、开始一个事务

```
postgres=# begin;
BEGIN
```

或者

```
postgres=# begin TRANSACTION ; 
BEGIN
```


也可以定义事务的级别

```
postgres=# begin transaction isolation level read committed ;
BEGIN
```

### 4.2、提交事务
进程#1访问 

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
  
 OpenTenBase也是完全支持ACID特性，没提交前开启另一个连接查询，你会看到是5条记录，这是OpenTenBase隔离性和多版本视图的实现，如下所示

进程#2访问

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
进程#1提交数据

```
postgres=# commit;
COMMIT
postgres=# 
```

进程#2再查询数据，这时能看到已经提交的数据了，这个级别叫“读已提交”

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

### 4.3、回滚事务

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

Rollback后数据又回来了

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

### 4.4、事务读一致性REPEATABLE READ

这种事务级别表示事务自始至终读取的数据都是一致的，如下所示

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

### 4.5、行锁在事务中的运用
#### 4.5.1、环境准备

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

#### 4.5.2、直接update获取

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

上面session1与session2分别持有mc=pgxz行和mc=opentenbase的行锁

#### 4.5.3、select...for update获取
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

上面session1与session2分别持有mc=pgxz行和mc=opentenbase的行锁

#### 4.5.4、排它锁检查

```
postgres=# select pid,pg_blocking_pids(pid),wait_event_type,query from pg_stat_activity where wait_event_type = 'Lock' and pid!=pg_backend_pid()
```

