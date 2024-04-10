# Active/standby switchover

> In [Quick Start](01-quickstart.md) this article, we introduce the architecture of OpenTenBase, source code compilation and installation, cluster running status, startup and stop, etc. > > In [Application Access Guide](02-access.md), we introduced how the application connects to the OpenTenBase database for database creation, table creation, data import, query, and other operations. > > In [Basic Usage](03-basic-use.md), we describe the unique shard tables, hot and cold partition tables, the creation of replicated tables, and basic DML operations in OpenTenBase. > > In [Advanced Usage](04-advanced-use.md), we introduce the advanced use and operation of OpenTenBase, including the use of various window functions, Json/Jsonb, cursors, transactions, locks, etc. > > In [Component Installation and Management](05-component.md), we go deep into the various components of OpenTenBase, and make a separate detailed introduction to the initialization, parameter configuration, start and stop, running status view, and routing effective configuration of various components. > > In this article, we will describe in detail how to switch the active and standby roles of various components within OpenTenBase.

## Environment deployment
- Number of servers

  2 sets, IP: 172.16.0.29, 172.16.0.47

- Hardware configuration

  CPU: 4-core Memory: 8G System Disk: 50G Data Disk: 200G

- Operating system requirements

  centos7.3

## Create an OS user
-	Create an operating system running user


```
[root@VM_0_29_centos ~]# adduser -d /data/opentenbase opentenbase
```

-	Configure the operating system user password


```
[root@VM_0_29_centos pgxztmp]# passwd opentenbase
```

-	Create the opentenbase application run directory


```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/install/pgxz
```

-	Create the opentenbase data directory


```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/data/pgxz
```

-	Upload the pgxz application to the directory/data/opentenbase/install/pgxz. The directory structure is


```
[opentenbase@VM_0_29_centos pgxz]$ ll /data/opentenbase/install/pgxz
total 4
drwxrwxr-x 2 pgxz pgxz 4096 Nov 10 04:33 bin
drwxrwxr-x 4 pgxz pgxz  189 Nov 10 04:33 include
drwxrwxr-x 4 pgxz pgxz  172 Nov 10 04:33 lib
drwxrwxr-x 3 pgxz pgxz   24 Oct  1 14:54 share
[opentenbase@VM_0_29_centos pgxz]$ 
```

- Configure environment variables for the pgxz user


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

## Installation Configuration Topology Description

Node Name | IP | Directory
-------|:-----------:|-------------------------
GTM primary | 172.16.0.29 |/data/opentenbase/data/pgxz/GTM
GTM backup | 172.16.0.47 |/data/opentenbase/data/pgxz/GTM
cn01	| 172.16.0.29	 | /data/opentenbase/data/pgxz/cn01
cn02	| 172.16.0.47	 | /data/opentenbase/data/pgxz/cn02
Dn01 primary | 172.16.0.29 |/data/opentenbase/data/pgxz/dn01
Dn01standby | 172.16.0.47 |/data/opentenbase/data/pgxz/dn01
Dn02 primary | 172.16.0.47 |/data/opentenbase/data/pgxz/dn02
Dn02 | 172.16.0.29 |/data/opentenbase/data/pgxz/dn02


# DN active-standby switchover
## Simulate DN01 main fault


```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f  
```

## Lift DN01standby as the main


```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 promote 
```

## CN01 Main Route Change


```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

## CN02 Main Route Change


```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

## DN01 Main Route Change


```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

**Note here to connect to the new master.**

## DN02 main route change


```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```
Note: The active-standby switchover of CN is similar to that of DN, except that the -Z parameter is changed to coordinator when simulating CN failure and promoting the standby node, so I will not repeat the PG _ CTL -Z coordinator-D ${ CN node data directory } [stop -m f | promote]

# GTM active-standby switching
## Mimic GTM master failure


```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop 
```
## Promote GTM backup as the main


```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm promote 
```
## CN01 Main Route Change


```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```
## CN02 Main Route Change


```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```
## DN01 Main Route Change


```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```

**Note here to connect to the new master.**
## DN02 main route change


```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```

