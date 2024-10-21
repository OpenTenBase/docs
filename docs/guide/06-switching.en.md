# Master and Slave switching

>In [Quick Start](01-quickstart.md), we introduce the architecture of OpenTenBase, source code compilation and installation, cluster running status, startup and stop, etc.
>
>In [Application Access](02-access.md), we describe how applications can connect to OpenTenBase databases for database creation, table creation, data import, and query.
>
>In [Basic Usage](03-basic-use.md), we introduce the creation of shard tables, hot and cold partition tables, and replication tables in OpenTenBase, as well as basic DML operations.
>
>In [Advanced Usage](04-advanced-use.md), we introduce the advanced usage of OpenTenBase, which includes the use of various window functions, Json/Jsonb, cursors, transactions, locks, etc.
>
>IN [Component Installation and Management](05-component.md), We delve into the various components of OpenTenBase and give a detailed introduction to the initialization, parameter configuration, start and stop, running status viewing, and route effective configuration of each component.
>
>In this article, we will introduce in detail how to switch the primary/standby roles of various components within OpenTenBase.

## Environment deployment  
- Number of servers

  2 units, IP respectively： 172.16.0.29，172.16.0.47

- Hardware configuration

  CPU：4C  
  Memory：8G  
  System disk：50G  
  Data disk：200G  

- Operating system requirements

  centos7.3  

## Creating OS Users

-	Create an operating system running user  

```
[root@VM_0_29_centos ~]# adduser -d /data/opentenbase opentenbase
```

-	Configure the operating system user password  

```
[root@VM_0_29_centos pgxztmp]# passwd opentenbase
```

-	Create a directory for the OpenTenbase application to run  

```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/install/pgxz
```

-	Create an OpenTenbase data directory  

```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/data/pgxz
```

-	Upload the pgxz application to the directory /data/opentenbase/install/pgxz, and the structure of the directory is as follows:  

```
[opentenbase@VM_0_29_centos pgxz]$ ll /data/opentenbase/install/pgxz
total 4
drwxrwxr-x 2 pgxz pgxz 4096 Nov 10 04:33 bin
drwxrwxr-x 4 pgxz pgxz  189 Nov 10 04:33 include
drwxrwxr-x 4 pgxz pgxz  172 Nov 10 04:33 lib
drwxrwxr-x 3 pgxz pgxz   24 Oct  1 14:54 share
[opentenbase@VM_0_29_centos pgxz]$ 
```

- Configure environment variables for PGXZ users

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

## Configuring public parameters

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


Node Name |     IP	    |  Directory
-------|:-----------:|-------------------------
gtm-master  | 172.16.0.29 | /data/opentenbase/data/pgxz/gtm
gtm-slave	| 172.16.0.47	 | /data/opentenbase/data/pgxz/gtm
cn01	| 172.16.0.29	 | /data/opentenbase/data/pgxz/cn01
cn02	| 172.16.0.47	 | /data/opentenbase/data/pgxz/cn02
dn01-master	| 172.16.0.29	 | /data/opentenbase/data/pgxz/dn01
dn01-slave	| 172.16.0.47	 | /data/opentenbase/data/pgxz/dn01
dn02-master	| 172.16.0.47	 | /data/opentenbase/data/pgxz/dn02
dn02slave	| 172.16.0.29	 | /data/opentenbase/data/pgxz/dn02


# DN Master/Slave switchover
## Similar to DN01 primary fault

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f  
```

## Promote DN01 Slave to Master

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 promote 
```

## CN01 Primary route changes

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

## CN02 Primary route changes  

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

## DN01 Primary route changes

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

**Note: This is to be connected to the new master**

## DN02 Primary route changes

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```
Note: The Master/Slave switchover of a CN is similar to that of a DN, except that the -Z parameter is changed to coordinator when simulating a CN fault and promoting a standby node  
pg_ctl -Z coordinator -D ${CN node data directory} [stop -m f | promote]

# GTM Master/Slave switchover
## Similar to a GTM Master fault

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop 
```
## Promote GTM slave to primary

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm promote 
```
## CN01 Primary route changes

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```
## CN02 Primary route changes

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```
## DN01 Primary route changes

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```

**Note: This is to be connected to the new master**
## DN02 Primary route changes

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```

