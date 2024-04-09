# 组件安装及管理

>在[快速入门](01-quickstart.md)文章中我们介绍了 OpenTenBase 的架构、源码编译安装、集群运行状态、启动停止等内容。
>
>在[应用接入](02-access.md)中我们介绍了应用程序连接 OpenTenBase 数据库进行建库、建表、数据导入、查询等操作。
>
>在[基本使用](03-basic-use.md)中我们介绍 OpenTenBase 中特有的shard表、复制表的创建，和基本的DML操作。
>
>在[高级使用](04-advanced-use.md)中我们介绍 OpenTenBase 的高级使用操作内容，其中包含了各种窗口函数、Json/Jsonb、游标、事务、锁等的使用。
>
>在本篇文章中我们将深入到 OpenTenBase 各种组件内部，对各种组件的初始化、参数配置、启停、运行状态查看、路由生效配置等进行单独的详细介绍。

## 机器准备

- 服务器数量

  2台，IP分别为： 172.16.0.29，172.16.0.47

- 硬件配置

  CPU：4核  
  内存：8G  
  系统盘：50G  
  数据盘：200G  

- 操作系统要求

  centos7.3  

## 创建OS用户

-	创建操作系统运行用户  

```
[root@VM_0_29_centos ~]# adduser -d /data/opentenbase opentenbase
```

-	配置操作系统用户密码  

```
[root@VM_0_29_centos pgxztmp]# passwd opentenbase
```

-	创建opentenbase应用程序运行目录  

```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/install/pgxz
```

-	创建opentenbase数据目录  

```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/data/pgxz
```

-	上传pgxz应用程序到目录/data/opentenbase/install/pgxz下面，目录的结构为  

```
[opentenbase@VM_0_29_centos pgxz]$ ll /data/opentenbase/install/pgxz
total 4
drwxrwxr-x 2 pgxz pgxz 4096 Nov 10 04:33 bin
drwxrwxr-x 4 pgxz pgxz  189 Nov 10 04:33 include
drwxrwxr-x 4 pgxz pgxz  172 Nov 10 04:33 lib
drwxrwxr-x 3 pgxz pgxz   24 Oct  1 14:54 share
[opentenbase@VM_0_29_centos pgxz]$ 
```

- 配置pgxz用户的环境变量

```
[opentenbase@VM_0_29_centos ~]$ vim /data/opentenbase/.bashrc 
# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

export OPENTENBASE_HOME=/data/opentenbase/install/pgxz
export PATH=$OPENTENBASE_HOME/bin:$PATH
export LD_LIBRARY_PATH=$OPENTENBASE_HOME/lib:${LD_LIBRARY_PATH}
```

## 配置公共参数

```
[opentenbase@VM_0_29_centos ~]# mkdir -p /data/opentenbase/global/
[opentenbase@VM_0_29_centos ~]#vim /data/opentenbase/global/postgresql.conf.user

listen_addresses = '0.0.0.0'
max_connections = 500
max_pool_size = 65535
shared_buffers = 1GB                    
max_prepared_transactions = 2000
maintenance_work_mem = 256MB
wal_level = logical
max_wal_senders = 64
max_wal_size = 1GB
min_wal_size = 256MB
log_destination = 'csvlog'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%A-%H.log' 
synchronous_commit = local
synchronous_standby_names = '' 
```

## 安装配置拓补结构说明


节点名称 |     IP	    |  目录
-------|:-----------:|-------------------------
gtm主  | 172.16.0.29 | /data/opentenbase/data/pgxz/gtm
gtm备	| 172.16.0.47	 | /data/opentenbase/data/pgxz/gtm
cn01	| 172.16.0.29	 | /data/opentenbase/data/pgxz/cn01
cn02	| 172.16.0.47	 | /data/opentenbase/data/pgxz/cn02
dn01主	| 172.16.0.29	 | /data/opentenbase/data/pgxz/dn01
dn01备	| 172.16.0.47	 | /data/opentenbase/data/pgxz/dn01
dn02主	| 172.16.0.47	 | /data/opentenbase/data/pgxz/dn02
dn02备	| 172.16.0.29	 | /data/opentenbase/data/pgxz/dn02


# GTM主管理
## 初始化

```
[opentenbase@VM_0_29_centos ~]# mkdir -p /data/opentenbase/data/pgxz
[opentenbase@VM_0_29_centos ~]# initgtm -Z gtm -D /data/opentenbase/data/pgxz/gtm
```

## 参数配置

```
#配置gtm节点名称
nodename = gtm_1 

#允许服务监听范围，*允许监听所有 IP 地址  
listen_addresses = '*' 

#监听端口号
port = 21000

#做为GTM主节点提供服务
startup = ACT
```

## 服务管理
-	启动服务

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm start
```

-	关闭服务

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop
```

-	查询状态

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm status -H 127.0.0.1 -P 21000
```

# GTM备管理
## 初始化

```
[opentenbase@VM_0_47_centos ~]# mkdir -p /data/opentenbase/data/pgxz
[opentenbase@VM_0_47_centos ~]# initgtm -Z gtm -D /data/opentenbase/data/pgxz/gtm
```
## 参数配置

```
[opentenbase@VM_0_47_centos ~]# vim /data/opentenbase/data/pgxz/gtm/gtm.conf
#配置gtm节点名称
nodename = gtm_1

#允许服务监听范围，*允许监听所有 IP 地址
listen_addresses = '*' 

#监听端口号
port = 21000

#做为GTM备节点提供运行
startup = STANDBY 

#配置GTM主节点信息
active_host = '172.16.0.29' 
active_port = 21000
```

## 服务管理
-	启动服务

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm start
```

-	关闭服务

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop
```

-	查询状态

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm status -H 127.0.0.1 -P 21000
```

# cn01管理
## 初始化

```
[opentenbase@VM_0_29_centos ~]# initdb --locale=zh_CN.UTF-8 -U opentenbase -E utf8 -D /data/opentenbase/data/pgxz/cn01 --nodename=cn01 --nodetype=coordinator --master_gtm_nodename gtm_1 --master_gtm_ip 172.16.0.29 --master_gtm_port 21000
```

## 参数配置

```
[opentenbase@VM_0_29_centos ~]# vim /data/opentenbase/data/pgxz/cn01/postgresql.conf

port = 15432
pooler_port=15433
include_if_exists ='/data/opentenbase/global/postgresql.conf.user'
```

```
[opentenbase@VM_0_29_centos ~]# vim /data/opentenbase/data/pgxz/cn01/pg_hba.conf

local   all             all                    trust 
host    all             all    127.0.0.1/32    trust

host    replication    all    172.16.0.29/32    trust 
host    all            all    172.16.0.29/32    trust 
 
host    replication    all    172.16.0.47/32    trust 
host    all            all    172.16.0.47/32    trust

host    all            all       0.0.0.0/0        md5
```

## 服务管理
-	启动服务

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 start
```

-	关闭服务

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 stop -m f #快速关闭
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 stop -m i #强制关闭
```

-	重载参数

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn01 reload
```

-	查询状态

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn01 status
```

# cn02管理
## 初始化
```
[opentenbase@VM_0_47_centos ~]# initdb --locale=zh_CN.UTF-8 -U opentenbase -E utf8 -D /data/opentenbase/data/pgxz/cn02 --nodename=cn02 --nodetype=coordinator --master_gtm_nodename gtm_1 --master_gtm_ip 172.16.0.29 --master_gtm_port 21000
```

## 参数配置
```
[opentenbase@VM_0_47_centos ~]# vim /data/opentenbase/data/pgxz/cn02/postgresql.conf

port = 15432
pooler_port=15433
include_if_exists ='/data/opentenbase/global/postgresql.conf.user'

[opentenbase@VM_0_47_centos ~]# vim /data/opentenbase/data/pgxz/cn02/pg_hba.conf

local   all             all                    trust 
host    all             all    127.0.0.1/32    trust

host    replication    all    172.16.0.29/32    trust 
host    all            all    172.16.0.29/32    trust 
 
host    replication    all    172.16.0.47/32    trust 
host    all            all    172.16.0.47/32    trust
 
host    all            all       0.0.0.0/0        md5
```

## 服务管理

-	启动服务 
 
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 start
```

-	关闭服务
  
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 stop -m f #快速关闭
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 stop -m i #强制关闭
```

-	重载参数
  
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn02 reload
```

-	查询状态 
 
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn02 status
```

# dn01主管理
## 初始化

```
[opentenbase@VM_0_29_centos ~]# initdb --locale=zh_CN.UTF-8 -U opentenbase -E utf8 -D /data/opentenbase/data/pgxz/dn01 --nodename=dn01 --nodetype=datanode --master_gtm_nodename gtm_1 --master_gtm_ip 172.16.0.29 --master_gtm_port 21000
```

## 参数配置

```
[opentenbase@VM_0_29_centos ~]# vim /data/opentenbase/data/pgxz/dn01/postgresql.conf

port = 23001
pooler_port=24001
include_if_exists ='/data/opentenbase/global/postgresql.conf.user'

[opentenbase@VM_0_29_centos ~]# vim /data/opentenbase/data/pgxz/dn01/pg_hba.conf

local   all             all                    trust 
host    all             all    127.0.0.1/32    trust

host    replication    all    172.16.0.29/32    trust 
host    all            all    172.16.0.29/32    trust 
 
host    replication    all    172.16.0.47/32    trust 
host    all            all    172.16.0.47/32    trust 
```

## 服务管理

-	启动服务

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 start
```

-	关闭服务

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f #快速关闭
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m i #强制关闭
```

-	重载参数

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 reload
```

-	查询状态

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 status
```

# dn02主管理
## 初始化

```
[opentenbase@VM_0_47_centos ~]# initdb --locale=zh_CN.UTF-8 -U opentenbase -E utf8 -D /data/opentenbase/data/pgxz/dn02 --nodename=dn02 --nodetype=datanode --master_gtm_nodename gtm_1 --master_gtm_ip 172.16.0.29 --master_gtm_port 21000
```

## 参数配置

```
[opentenbase@VM_0_47_centos ~]# vim /data/opentenbase/data/pgxz/dn02/postgresql.conf

port = 23002
pooler_port=24002
include_if_exists ='/data/opentenbase/global/postgresql.conf.user'

[opentenbase@VM_0_47_centos ~]# vim /data/opentenbase/data/pgxz/dn01/pg_hba.conf

local   all             all                    trust 
host    all             all    127.0.0.1/32    trust

host    replication    all    172.16.0.29/32    trust 
host    all            all    172.16.0.29/32    trust 
 
host    replication    all    172.16.0.47/32    trust 
host    all            all    172.16.0.47/32    trust 
```
 
## 服务管理

-	启动服务

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 start
```

-	关闭服务

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m f #快速关闭
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m i #强制关闭
```

-	重载参数

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 reload
```

-	查询状态

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 status
```

# dn01备管理
## 生成备节点

```
[opentenbase@VM_0_47_centos ~]# pg_basebackup -p 23001 -h 172.16.0.29 -U opentenbase -D /data/opentenbase/data/pgxz/dn01 -X f -P -v
```

## 参数配置

```
[opentenbase@VM_0_47_centos ~]# vim /data/opentenbase/data/pgxz/dn01/recovery.conf

standby_mode = on 
primary_conninfo = 'host = 172.16.0.29 port = 23001 user = opentenbase application_name = s1'
```

## 服务管理

-	启动服务

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 start
```

-	关闭服务

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f #快速关闭
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m i #强制关闭
```

-	重载参数

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 reload
```

-	查询状态

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 status
```

# dn02备管理
## 生成备节点

```
[opentenbase@VM_0_29_centos ~]# pg_basebackup -p 23002 -h 172.16.0.47 -U opentenbase -D /data/opentenbase/data/pgxz/dn02 -X f -P -v
```

## 参数配置

```
[opentenbase@VM_0_29_centos ~]# vim /data/opentenbase/data/pgxz/dn02/recovery.conf

standby_mode = on 
primary_conninfo = 'host = 172.16.0.47 port = 23002 user = opentenbase application_name = s1'
```

## 服务管理

- 启动服务

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 start
```

- 关闭服务

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m f #快速关闭
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m i #强制关闭
```

- 重载参数

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 reload
```

- 查询状态

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 status
```

# 路由配置
## cn01

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# 
alter node cn01 with (host='172.16.0.29',port=15432);
create node cn02 with (type=coordinator,host='172.16.0.47',port=15432,primary=false,preferred=false);
create node dn01 with (type=datanode,host='172.16.0.29',port=23001,primary=false,preferred=false);
create node dn02 with (type=datanode,host='172.16.0.47',port=23002,primary=false,preferred=false);
select pgxc_pool_reload();
```

## cn02

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#
alter node cn02 with (host='172.16.0.47',port=15432);
create node cn01 with (type=coordinator,host='172.16.0.29',port=15432,primary=false,preferred=false);
create node dn01 with (type=datanode,host='172.16.0.29',port=23001,primary=false,preferred=false);
create node dn02 with (type=datanode,host='172.16.0.47',port=23002,primary=false,preferred=false);
select pgxc_pool_reload();
```

## dn01

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#
alter node dn01 with (host='172.16.0.29',port=23001);
create node cn01 with (type=coordinator,host='172.16.0.29',port=15432,primary=false,preferred=false);
create node cn02 with (type=coordinator,host='172.16.0.47',port=15432,primary=false,preferred=false);
create node dn02 with (type=datanode,host='172.16.0.47',port=23002,primary=false,preferred=false);
select pgxc_pool_reload();
```

## dn02

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#
alter node dn02 with (host='172.16.0.47',port=23001);
create node cn01 with (type=coordinator,host='172.16.0.29',port=15432,primary=false,preferred=false);
create node cn02 with (type=coordinator,host='172.16.0.47',port=15432,primary=false,preferred=false);
create node dn01 with (type=datanode,host='172.16.0.29',port=23001,primary=false,preferred=false);
select pgxc_pool_reload();
```

## 路由表信息  

所有节点的路由信息配置完成后如下所示

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase

postgres=# select * from pgxc_node;
 node_name | node_type | node_port |  node_host  | nodeis_primary | nodeis_preferred |   node_id   | node_cluster_name 
-----------+-----------+-----------+-------------+----------------+------------------+-------------+-------------------
 gtm_1     | G         |     21000 | 172.16.0.29 | t              | f                | -1500995709 | opentenbase_cluster
 cn01      | C         |     15432 | 172.16.0.29 | f              | f                |    53994174 | opentenbase_cluster
 cn02      | C         |     15432 | 172.16.0.47 | f              | f                |  -613255070 | opentenbase_cluster
 dn01      | D         |     23001 | 172.16.0.29 | f              | f                | -1085152094 | opentenbase_cluster
 dn02      | D         |     23002 | 172.16.0.47 | f              | f                |  -506537247 | opentenbase_cluster
(5 rows)
```

# GROUP（存储组）配置
## 创建默认GROUP  

创建默认GROUP

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#
create default node group default_group with(dn01, dn02);
create sharding group to group default_group;
clean sharding;
```

至此，OpenTenBase 就可以像单机数据库一样使用了。

## 查询已经创建的GROUP

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase

select * from pgxc_group;

```

