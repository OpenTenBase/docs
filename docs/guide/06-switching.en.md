# Failover

>In [Quick Start](01-quickstart.en.md) article, we introduced opentenbase architecture, source code compilation and installation, cluster running status, startup and stop, etc.
>
>In [Access](02-access.md) article, we introduced the application program to connect opentenbase for database creation, table creation, data import, query and other operations.
>
>In [Basic Use](03-basic-use.md) article, we introduced the creation of shard table, cold and hot partition table, replication table in opentenbase, and basic DML operations.
>
>In [Advanced Use](04-advanced-use.md) article, we introduced the advanced use of opentenbase, including the use of various window functions, Json/Jsonb, cursors, transactions, locks, etc.
>
>In [组件安装及管理](05-component.md) article, we dive into the internal of various components of opentenbase, and introduced the initialization, parameter configuration, startup and stop, running status viewing, routing effective configuration of various components separately.
>
>In this article, we will introduce in detail how to switch the master and standby roles of various components in opentenbase.

## Environment Deployment
- Number of servers

  Two servers, IP's are： 172.16.0.29，172.16.0.47

- Hardware configuration

  CPU：4 core+
  Memory：8 GB+
  System Disk：50GB+  
  Data Disk：200G+  

- Operation system requirements

  CentOS 7.3  

## Create OS user
-	Create operating system running user

```
[root@VM_0_29_centos ~]# adduser -d /data/opentenbase opentenbase
```

- Configure the operating system user password

```
[root@VM_0_29_centos pgxztmp]# passwd opentenbase
```

- Create opentenbase application program running directory

```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/install/pgxz
```

- Create opentenbase data directory

```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/data/pgxz
```

-	Upload `pgxz` application program to directory `/data/opentenbase/install/pgxz`, the directory structure is

```
[opentenbase@VM_0_29_centos pgxz]$ ll /data/opentenbase/install/pgxz
total 4
drwxrwxr-x 2 pgxz pgxz 4096 Nov 10 04:33 bin
drwxrwxr-x 4 pgxz pgxz  189 Nov 10 04:33 include
drwxrwxr-x 4 pgxz pgxz  172 Nov 10 04:33 lib
drwxrwxr-x 3 pgxz pgxz   24 Oct  1 14:54 share
[opentenbase@VM_0_29_centos pgxz]$ 
```

- Configure the environment variables for user 'pgxz'

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

## Configure public parameters

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

## Install and configure GTM

 | Node     IP    |  Directory
-------|:-----------:|-------------------------
gtm master  | 172.16.0.29 | /data/opentenbase/data/pgxz/gtm
gtm standby | 172.16.0.47 | /data/opentenbase/data/pgxz/gtm
cn01	| 172.16.0.29 | /data/opentenbase/data/pgxz/cn01
cn02	| 172.16.0.47 | /data/opentenbase/data/pgxz/cn02
dn01 master	| 172.16.0.29 | /data/opentenbase/data/pgxz/dn01
dn01 standby	| 172.16.0.47 | /data/opentenbase/data/pgxz/dn01
dn02 master	| 172.16.0.47 | /data/opentenbase/data/pgxz/dn02
dn02 stangdy	| 172.16.0.29 | /data/opentenbase/data/pgxz/dn02


# DN Failover
## Simulate DN01 master failure

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f  
```

## Switch DN01 standby to master

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 promote 
```

## Switch main route of CN01

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

## Switch main route of CN02

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

## Switch main route of DN01

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

**Notice that here we need connect to new route**

## Switch main route of DN02

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```
说明：CN的主备切换和DN类似，只是在模拟CN故障和提升备节点时将-Z参数改为coordinator，因此不在赘述  
pg_ctl -Z coordinator -D ${CN节点数据目录} [stop -m f | promote]

# GTM Failover
## Simulate GTM master failure

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop 
```

## Promote GTM standby to master

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm promote 
```

## Switch main route of CN01

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```

## Switch main route of CN02

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```

## Switch main route of DN01

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```

**Notice that here we need connect to new route**
## Switch main route of DN02

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```
