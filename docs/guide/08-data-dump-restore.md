# 数据导入导出

## pg_dump数据导出工具 

### pg_dump介绍

pg\_dump是用于备份 OpenTenBase 单个数据库的工具。即使数据库正在被并发使用，它也能创建一致的备份。pg\_dump不阻塞其他用户访问数据库（读取或写入）。

备份的数据可以是脚本或归档文件格式。脚本内容包含 SQL 命令的纯文本数据，它们可以用来重建数据库到它被备份时的状态。恢复一个这样的脚本，需要使用psql客户端工具。脚本文件还可以被用来在其他机器上重构数据库。在经过一些修改后，还可以在其他 SQL 数据库产品上重构数据库。另一种可选的归档文件格式必须与pg\_restore配合使用来重建数据库。pg\_dump提供了一种灵活的归档和传输机制。pg\_dump可以被用来备份整个数据库，然后pg\_restore可以被用来检查归档并/或选择数据库的哪些部分要被恢复。pg\_restore支持并行恢复并且默认是压缩的。  

### 连接数据库参数介绍
-d dbname  
--dbname=dbname  
指定要连接到的数据库名，不指定该参数时默认是从PGDATABASE环境变量中取得（如果被设置）。   

-h host  
--host=host  
指定要连接服务器机器的主机名或者ip地址。不指定该参数时默认是从PGHOST环境变量中取得（如果被设置）。   

-p port  
--port=port  
指定要连接服务器监听的 TCP 端口，不指定该参数时默认是从PGPORT环境变量中（如果被设置），否则使用编译在程序中的默认值。   

-U username  
--username=username  
指定要连接服务的用户名，不指定该参数时默认是从PGUSER环境变量中（如果被设置），否则使用当前操作系统用户名做为默认值。   

-w  
--no-password  
从不发出一个口令提示。如果服务器要求口令认证并且没有其他方式提供口令（例如一个.pgpass文件），那么连接尝试将失败。这个选项对于批处理任务和脚本有用，因为在其中没有一个用户来输入口令。   

-W  
--password  
强制pg\_dump在连接到一个数据库之前提示要求一个口令。  

### 使用介绍  
#### 整库备份
-	备份成文本格式

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 >/data/opentenbase/opentenbase.sql
```

-	备份成归档格式

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -Fc>/data/opentenbase/opentenbase.sql  
```

#### 只备份指定模式下的对象  
备份opentenbase模式下的对象  

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -n opentenbase>/data/opentenbase/opentenbase.sql
```

备份opentenbase和pgxz模式下的对象，多个模式使用多组-n  

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -n opentenbase -n pgxz>/data/opentenbase/opentenbase.sql
```

#### 不备份指定模式下的对象  

不备份opentenbase模式下的对象

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -N opentenbase>/data/opentenbase/opentenbase.sql
```

不备份opentenbase和pgxz模式下的对象，多个模式使用多组-N  

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -N opentenbase -N pgxz>/data/opentenbase/opentenbase.sql
```

#### 只备份某些数据表

备份数据表opentenbase.t

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -t 'opentenbase.t' >/data/opentenbase/opentenbase.sql
```

备份数据表opentenbase.t，pgxz.t  

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -t 'opentenbase.t' -t 'pgxz.t1'>/data/opentenbase/opentenbase.sql
```

备份模式opentenbase下所有t开头的数据表

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -t 'opentenbase.t*' >/data/opentenbase/opentenbase.sql
```

#### 不备份某些数据表

不备份数据表opentenbase.t  

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -T 'opentenbase.t' >/data/opentenbase/opentenbase.sql
```

不备份数据表opentenbase.t，pgxz.t1

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -T 'opentenbase.t' -T 'pgxz.t1'>/data/opentenbase/opentenbase.sql
```

不备份模式opentenbase下所有t开头的数据表

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -T 'opentenbase.t*' >/data/opentenbase/opentenbase.sql
```

#### 只备份出对象定义

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -s >/data/opentenbase/opentenbase.sql
```

#### 只备份出数据

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -a >/data/opentenbase/opentenbase.sql
```

#### 备份出的数据格式为insert values(xxx)

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 --inserts >/data/opentenbase/opentenbase.sql
```

#### 备份出的数据格式为insert(xxx) values(xxx)  

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 --column-inserts >/data/opentenbase/opentenbase.sql
```

#### 备份带group信息  

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 --include-nodes >/data/opentenbase/opentenbase.sql
```

#### 不备份带非日志表数据  
```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 --no-unlogged-table-data >/data/opentenbase/opentenbase.sql
```

## pg_dumpall数据导出工具  
### pg_dumpall介绍  

pg\_dumpall是用于备份 OpenTenBase 所有数据库的工具，所以使用pg\_dumpall时不能指定数据库。即使数据库正在被并发使用，它也能创建一致的备份。pg\_dumpall不阻塞其他用户访问数据库（读取或写入）。与pg\_dump不同的地方是pg\_dumpall可以用于备份 OpenTenBase 全局对象，如用户和表空间定义。pg\_dumpall备份时无法指定备份数据的格式，即无法使用-Fc这样的参数。

### 连接数据库参数介绍 

-h host  
--host=host  
指定要连接服务器机器的主机名或者ip地址。不指定该参数时默认是从PGHOST环境变量中取得（如果被设置）。   

-p port  
--port=port  
指定要连接服务器监听的 TCP 端口，不指定该参数时默认是从PGPORT环境变量中（如果被设置），否则使用编译在程序中的默认值。  

-U username  
--username=username  
指定要连接服务的用户名，不指定该参数时默认是从PGUSER环境变量中（如果被设置），否则使用当前操作系统用户名做为默认值。  

-w  
--no-password  
从不发出一个口令提示。如果服务器要求口令认证并且没有其他方式提供口令（例如一个.pgpass文件），那么连接尝试将失败。这个选项对于批处理任务和脚本有用，因为在其中没有一个用户来输入口令。   

-W  
--password  
强制pg\_dump在连接到一个数据库之前提示要求一个口令。   

-l dbname  
--database=dbname  
指定要连接到哪个数据库备份全局对象以及发现要备份哪些其他数据库。如果没有指定，将会使用postgres数据库，如果postgres不存在，就使用 template1。  

### 使用介绍  
#### 只备份全局对象  

```
pg_dumpall -h 127.0.0.1 -U opentenbase -p 15432 -g >/data/opentenbase/opentenbase.sql
```

#### 只备份用户角色  

```
pg_dumpall -h 127.0.0.1 -U opentenbase -p 15432 -r >/data/opentenbase/opentenbase.sql
```

#### 只备份表空间  

```
pg_dumpall -h 127.0.0.1 -U opentenbase -p 15432 -t>/data/opentenbase/opentenbase.sql
```

## pg_restore数据导入工具  

### pg_restore介绍  

pg\_restore是一个用来从pg\_dump创建的非文本格式归档恢复PostgreSQL数据库的工具。这些归档文件还允许pg\_restore选择恢复哪些内容。pg\_restore可以在两种模式下操作。如果指定了一个数据库名称，pg\_restore会连接那个数据库并且把归档内容直接恢复到该数据库中。否则，会创建一个脚本，其中包含着重建该数据库所必要的 SQL 命令，它会被写入到一个文件或者标准输出。这个脚本输出等效于pg\_dump的纯文本输出格式。因此，一些控制输出的选项与pg\_dump的选项类似。  

### 连接参数介绍  

-d dbname  
--dbname=dbname  
指定要连接到的数据库名。   

-h host  
--host=host  
指定要连接服务器机器的主机名或者ip地址。不指定该参数时默认是从PGHOST环境变量中取得（如果被设置）。   

-p port  
--port=port  
指定要连接服务器监听的 TCP 端口，不指定该参数时默认是从PGPORT环境变量中（如果被设置），否则使用编译在程序中的默认值。   

-U username  
--username=username  
指定要连接服务的用户名，不指定该参数时默认是从PGUSER环境变量中（如果被设置），否则使用当前操作系统用户名做为默认值。   

-w  
--no-password  
从不发出一个口令提示。如果服务器要求口令认证并且没有其他方式提供口令（例如一个.pgpass文件），那么连接尝试将失败。这个选项对于批处理任务和脚本有用，因为在其中没有一个用户来输入口令。   

-W  
--password  
强制pg\_restore在连接到一个数据库之前提示要求一个口令。  

### 使用介绍  

#### 输出等效于pg_dump的纯文本格式  

```
pg_restore opentenbase.dump
```

命令中不要使用-d dbname 参数，则pg\_restore输出等效于pg\_dump的纯文本输出格式。

#### 输出文本重定向于某个文件中  

```
pg_restore opentenbase.dump -f  opentenbase.sql 
```
或者得  

```
pg_restore opentenbase.dump > opentenbase.sql  
```

将输出的文本重定向于opentenbase.sql文件中。  

#### 恢复时先创建数据库

```
pg_dump -h 127.0.0.1 -p 15432 -U opentenbase -d opentenbase -Fc > opentenbase.dump
dropdb -h 127.0.0.1 -p 15432 -U opentenbase opentenbase   
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -C -d postgres opentenbase.dump 
```

在使用这个选项时，-d提到的数据库只被用于发出初始的DROP DATABASE和CREATE DATABASE命令。所有要恢复到该数据库名中的数据都出现在归档中  

#### 只恢复ddl  

```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -d opentenbase -s opentenbase.dump
```

#### 只恢复数据  

```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -d opentenbase -a opentenbase.dump
```

#### 在重新创建数据库对象之前清除  
```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -d opentenbase -c opentenbase.dump
```

####只恢复某些模式  

```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -n 'public' -d opentenbase opentenbase.dump
```

#### 只恢复某些表

恢复所有模式下的t_txt表  

```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -t 't_txt' -d opentenbase opentenbase.dump
```

恢复所有模式下的t_txt表和t表

```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -t 't_txt' -t 't' opentenbase.dump
```

恢复public模式下的t_txt表  

```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -n 'public' -t 't_txt' -d opentenbase opentenbase.dump
```

## psql数据导入工具  
### psql介绍 
 
psql是一个基于终端的 OpenTenBase 客户端工具，类似Oracle中的命令行工具sqlplus，但比sqlplus强大多了。它让你能交互式地键入查询，把它们发送给 OpenTenBase ，并且查看查询结果。或者，输入可以来自于一个文件或者命令行参数。此外，psql还提供一些元命令和多种类似 shell 的特性来为编写脚本和自动化多种任务提供便利。psql还支持命令补全，历史命令回找。  

### 连接数据库参数介绍  

-d dbname  
--dbname=dbname  
指定要连接到的数据库名，不指定该参数时默认是从PGDATABASE环境变量中取得（如果被设置）。   

-h host  
--host=host  
指定要连接服务器机器的主机名或者ip地址。不指定该参数时默认是从PGHOST环境变量中取得（如果被设置）。   

-p port  
--port=port  
指定要连接服务器监听的 TCP 端口，不指定该参数时默认是从PGPORT环境变量中（如果被设置），否则使用编译在程序中的默认值。   

-U username  
--username=username  
指定要连接服务的用户名，不指定该参数时默认是从PGUSER环境变量中（如果被设置），否则使用当前操作系统用户名做为默认值。   

-w  
--no-password  
从不发出一个口令提示。如果服务器要求口令认证并且没有其他方式提供口令（例如一个.pgpass文件），那么连接尝试将失败。这个选项对于批处理任务和脚本有用，因为在其中没有一个用户来输入口令。   

-W  
--password  
强制pg\_dump在连接到一个数据库之前提示要求一个口令。  

### 使用介绍  
#### psql执行一个sql文件中所有命令  

-	在外部执行

```
[pgxz@VM_0_3_centos ~]$ cat /data/opentenbase/opentenbase.sql 
set search_path = public;
insert into opentenbase values(1,2);
select count(1) from opentenbase;
```

```
[pgxz@VM_0_3_centos ~]$ psql -h 172.16.0.29 -p 15432 -U opentenbase -d postgres -f /data/opentenbase/opentenbase.sql 
SET
INSERT 0 1
 count 
-------
 10001
(1 row)
```

- 在内部执行

```
[pgxz@VM_0_3_centos ~]$ psql -h 172.16.0.29 -p 15432 -U opentenbase -d postgres 
psql (PostgreSQL 10 (opentenbase 2.01))
Type "help" for help.

postgres=# \i  /data/opentenbase/opentenbase.sql 
SET
INSERT 0 1
 count 
-------
 10002
(1 row)

```

## 结语
OpenTenBase 是企业级分布式HTAP数据库管理系统。通过单一数据库集群同时为客户提供高一致性的分布式数据库服务和高性能的数据仓库服务，形成一套融合完整的企业级解决方案。大家在数据库领域遇到相关问题时，欢迎随时留言我们。