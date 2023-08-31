# 主备切换

>在[快速入门](01-quickstart.md)文章中我们介绍了 OpenTenBase 的架构、源码编译安装、集群运行状态、启动停止等内容。
>
>在[应用接入](02-access.md)中我们介绍了应用程序连接 OpenTenBase 数据库进行建库、建表、数据导入、查询等操作。
>
>在[基本使用](03-basic-use.md)中我们介绍 OpenTenBase 中特有的shard表、冷热分区表、复制表的创建，和基本的DML操作。
>
>在[高级使用](04-advanced-use.md)中我们介绍 OpenTenBase 的高级使用操作内容，其中包含了各种窗口函数、Json/Jsonb、游标、事务、锁等的使用。
>
>在[组件安装及管理](05-component.md)中我们深入到 OpenTenBase 各种组件内部，对各种组件的初始化、参数配置、启停、运行状态查看、路由生效配置等进行单独的详细介绍。
>
>在本篇文章中我们将对 OpenTenBase 内部各种组件的主备角色如何切换进行详细介绍。

## 环境部署  
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


# DN主备切换
## 模似DN01主故障

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f  
```

## 将DN01备提升为主

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 promote 
```

## CN01主路由变更

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

## CN02主路由变更  

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

## DN01主路由变更

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

**注意这里要连接到新主**

## DN02主路由变更

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```
说明：CN的主备切换和DN类似，只是在模拟CN故障和提升备节点时将-Z参数改为coordinator，因此不在赘述  
pg_ctl -Z coordinator -D ${CN节点数据目录} [stop -m f | promote]

# GTM主备切换
## 模似GTM主故障

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop 
```
## 将GTM备提升为主

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm promote 
```
## CN01主路由变更

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```
## CN02主路由变更

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```
## DN01主路由变更

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```

**注意这里要连接到新主**
## DN02主路由变更

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```

