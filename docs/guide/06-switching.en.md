# Master-Standby Switchover

>In the [Quick Start](01-quickstart.md) article, we introduced the architecture of OpenTenBase, source code compilation and installation, cluster operation status, and start and stop operations.
>
>In [Access](02-access.md), we introduced how applications connect to the OpenTenBase database to perform operations such as creating databases, tables, data import, and queries.
>
>In [Basic Usage](03-basic-use.md), we introduced the creation of shard tables, cold-hot partition tables, and replication tables unique to OpenTenBase, as well as basic DML operations.
>
>In [Advanced Usage](04-advanced-use.md), we introduced advanced usage operations in OpenTenBase, including various window functions, Json/Jsonb, cursors, transactions, locks, etc.
>
>In [Component Installation and Management](05-component.md), we delved into the internals of various components of OpenTenBase, providing detailed individual introductions to the initialization, parameter configuration, start and stop, operation status viewing, and routing activation configuration of various components.
>
>In this article, we will provide a detailed introduction on how to switch the master-standby roles of various components within OpenTenBase.

## Environment Deployment
- Number of servers
  2, with IP addresses: 172.16.0.29, 172.16.0.47
- Hardware configuration
  CPU: 4 cores
  Memory: 8G
  System disk: 50G
  Data disk: 200G
- Operating system requirements
  centos7.3

## Create OS User
- Create an operating system user for running services

```
[root@VM_0_29_centos ~]# adduser -d /data/opentenbase opentenbase
```

- Configure the operating system user password

```
[root@VM_0_29_centos pgxztmp]# passwd opentenbase
```

- Create a directory for the OpenTenBase application to run

```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/install/pgxz
```

- Create a data directory for OpenTenBase

```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/data/pgxz
```

- Upload the pgxz application to the directory /data/opentenbase/install/pgxz, the directory structure is

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

## Configure Common Parameters

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

## Installation Configuration Topology Explanation

Node Name | IP | Directory
-------|:-----------:|--------------
gtm master | 172.16.0.29 | /data/opentenbase/data/pgxz/gtm
gtm standby | 172.16.0.47 | /data/opentenbase/data/pgxz/gtm
cn01 | 172.16.0.29 | /data/opentenbase/data/pgxz/cn01
cn02 | 172.16.0.47 | /data/opentenbase/data/pgxz/cn02
dn01 master | 172.16.0.29 | /data/opentenbase/data/pgxz/dn01
dn01 standby | 172.16.0.47 | /data/opentenbase/data/pgxz/dn01
dn02 master | 172.16.0.47 | /data/opentenbase/data/pgxz/dn02
dn02 standby | 172.16.0.29 | /data/opentenbase/data/pgxz/dn02

# DN Master-Standby Switchover
## Simulate DN01 Master Failure

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f  
```

## Promote DN01 Standby to Master

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 promote 
```

## CN01 Master Routing Change

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

## CN02 Master Routing Change

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

## DN01 Master Routing Change

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

**Note: Here you need to connect to the new master**

## DN02 Master Routing Change

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

Explanation: The master-standby switchover for CN is similar to DN, but when simulating CN failure and promoting the standby node, the -Z parameter is changed to coordinator, so it is not repeated here. `pg_ctl -Z coordinator -D ${CN节点数据目录} [stop -m f | promote]`

# GTM Master-Standby Switchover
## Simulate GTM Master Failure

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop 
```

## Promote GTM Standby to Master

```
[opentenbase@VM_0_47_centos ~]# gt
