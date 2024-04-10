# Primary Standby Switch

>In the [Quick Start](01-quickstart.md) article, we introduced the architecture of OpenTenBase, source code compilation and installation, cluster running status, startup and shutdown procedures, and more.
>
>In [Application Access](02-access.md), we covered how applications connect to the OpenTenBase database for tasks such as creating databases, tables, importing data, querying, and more.
>
>In [Basic Usage](03-basic-use.md), we discussed the creation of shard tables, cold-hot partition tables, replication tables unique to OpenTenBase, and basic DML operations.
>
>In [Advanced Usage](04-advanced-use.md), we delved into advanced operations in OpenTenBase, including various window functions, Json/Jsonb, cursors, transactions, locks, and more.
>
>In [Component Installation and Management](05-component.md), we delved into the internals of various components of OpenTenBase, providing detailed individual introductions on component initialization, parameter configuration, startup and shutdown, viewing running status, and configuring effective routing.
>
>In this article, we will provide a detailed introduction to the primary-standby switch of various components within OpenTenBase.

## Environment Setup  

- Number of Servers

  2, with IPs: 172.16.0.29, 172.16.0.47

- Hardware Configuration

  CPU: 4 cores  
  Memory: 8GB  
  System Disk: 50GB  
  Data Disk: 200GB  

- Operating System Requirements

  CentOS 7.3  

## Creating OS User

- Create an operating system user  

```
[root@VM_0_29_centos ~]# adduser -d /data/opentenbase opentenbase
```

- Set the password for the operating system user  

```
[root@VM_0_29_centos pgxztmp]# passwd opentenbase
```

- Create the opentenbase application runtime directory  

```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/install/pgxz
```

- Create the opentenbase data directory  

```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/data/pgxz
```

- Upload the pgxz application to the directory /data/opentenbase/install/pgxz, with the following directory structure  

```
[opentenbase@VM_0_29_centos pgxz]$ ll /data/opentenbase/install/pgxz
total 4
drwxrwxr-x 2 pgxz pgxz 4096 Nov 10 04:33 bin
drwxrwxr-x 4 pgxz pgxz  189 Nov 10 04:33 include
drwxrwxr-x 4 pgxz pgxz  172 Nov 10 04:33 lib
drwxrwxr-x 3 pgxz pgxz   24 Oct  1 14:54 share
[opentenbase@VM_0_29_centos pgxz]$ 
```

- Configure the environment variables for the pgxz user

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

## Installation and Configuration of Topology Structure

| Node Name    |     IP      | Directory                        |
| ------------ | :---------: | -------------------------------- |
| GTM Master   | 172.16.0.29 | /data/opentenbase/data/pgxz/gtm  |
| GTM Standby  | 172.16.0.47 | /data/opentenbase/data/pgxz/gtm  |
| CN01         | 172.16.0.29 | /data/opentenbase/data/pgxz/cn01 |
| CN02         | 172.16.0.47 | /data/opentenbase/data/pgxz/cn02 |
| DN01 Master  | 172.16.0.29 | /data/opentenbase/data/pgxz/dn01 |
| DN01 Standby | 172.16.0.47 | /data/opentenbase/data/pgxz/dn01 |
| DN02 Master  | 172.16.0.47 | /data/opentenbase/data/pgxz/dn02 |
| DN02 Standby | 172.16.0.29 | /data/opentenbase/data/pgxz/dn02 |


# DN Primary Standby Switch

## Simulate DN01 Master Failure

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f  
```

## Promote DN01 Standby to Master

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 promote 
```

## Change Routing on CN01 Master

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

## Change Routing on CN02 Master  

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#

 alter node dn01 with (host='172.16.0.47',port=23001);
```

## Change Routing on DN01 Master

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

**Note: Connect to the new master here**

## Change Routing on DN02 Master

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

Explanation: The primary-standby switch for CN is similar to DN, except that when simulating CN failures and promoting standby nodes, the -Z parameter is changed to coordinator. Therefore, it is not reiterated here.  
pg_ctl -Z coordinator -D ${CN node data directory} [stop -m f | promote]

# GTM Primary Standby Switch

## Simulate GTM Master Failure

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop 
```

## Promote GTM Standby to Master

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm promote 
```

## Change Routing on CN01 Master

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```

## Change Routing on CN02 Master

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```

## Change Routing on DN01 Master

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```

**Note: Connect to the new master here**

## Change Routing on DN02 Master

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```