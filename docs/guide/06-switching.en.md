# Active/Standby Switch

>In the [quickstart](01-quickstart.en.md) article, we introduced the architecture of OpenTenBase, source code compilation and installation, cluster running status, start and stop, etc.
>
>In [access](02-access.en.md) we introduced the application to connect to the OpenTenBase database for operations such as database creation, table creation, data import, and query.
>
>In [basic-use](03-basic-use.en.md) we introduce the creation of unique shard tables, replicated tables, and basic DML operations in OpenTenBase.
>
>In [advanced-use](04-advanced-use.md) we introduce the advanced usage operations of OpenTenBase, which includes the use of various window functions, Json/Jsonb, cursors, transactions, locks, etc.
>
>In [component](05-component.md), we go deep into the various components of OpenTenBase and provide a detailed introduction to the initialization, parameter configuration, start and stop, running status viewing, routing effective configuration, etc. of various components.
>
>In this article, we will introduce in detail how to switch the active and backup roles of various components within OpenTenBase.

## Environment deployment
- Number of servers

   2 units, the IPs are: 172.16.0.29, 172.16.0.47

- Hardware Configuration

   CPU: 4 cores
   Memory: 8G
   System disk: 50G
   Data disk: 200G

- Operating system requirements

   centos7.3

## Create OS user
- Create operating system running user

```
[root@VM_0_29_centos ~]# adduser -d /data/opentenbase opentenbase
```

- Configure operating system user password

```
[root@VM_0_29_centos pgxztmp]# passwd opentenbase
```

- Create the opentenbase application running directory

```
[root@VM_0_29_centos pgxz]# su opentenbase
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/install/pgxz
```

- Create opentenbase data directory

```
[root@VM_0_29_centos pgxz]# su opentenbase
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/data/pgxz
```

- Upload the pgxz application to the directory /data/opentenbase/install/pgxz. The structure of the directory is

```
[opentenbase@VM_0_29_centos pgxz]$ ll /data/opentenbase/install/pgxz
total 4
drwxrwxr-x 2 pgxz pgxz 4096 Nov 10 04:33 bin
drwxrwxr-x 4 pgxz pgxz 189 Nov 10 04:33 include
drwxrwxr-x 4 pgxz pgxz 172 Nov 10 04:33 lib
drwxrwxr-x 3 pgxz pgxz 24 Oct 1 14:54 share
[opentenbase@VM_0_29_centos pgxz]$
```

- Configure environment variables for the pgxz user

```
[opentenbase@VM_0_29_centos ~]$ vim /data/opentenbase/.bashrc
# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
         ./etc/bashrc
fi

export OPENTENBSE_HOME=/data/opentenbase/install/pgxz
export PATH=$OPENTENBase_HOME/bin:$PATH
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

## Installation configuration topology structure description

Node Name | IP | Directory
-------|:-----------:|--------------------------
gtm master | 172.16.0.29 | /data/opentenbase/data/pgxz/gtm
gtm preparation | 172.16.0.47 | /data/opentenbase/data/pgxz/gtm
cn01 | 172.16.0.29 | /data/opentenbase/data/pgxz/cn01
cn02 | 172.16.0.47 | /data/opentenbase/data/pgxz/cn02
dn01master | 172.16.0.29 | /data/opentenbase/data/pgxz/dn01
dn01备172.16.0.47 | /data/opentenbase/data/pgxz/dn01
dn02master | 172.16.0.47 | /data/opentenbase/data/pgxz/dn02
dn02备172.16.0.29 | /data/opentenbase/data/pgxz/dn02


# DN active/standby switchover
## Simulate DN01 main fault

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f
```

## Promote DN01 backup to master

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 promote
```

## CN01 main route change

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

## CN02 main route change

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

## DN01 main route change

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```

**Note that you need to connect to the new master here**

## DN02 main route change

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter node dn01 with (host='172.16.0.47',port=23001);
```
Note: CN's active-standby switching is similar to DN, except that the -Z parameter is changed to coordinator when simulating CN failure and promoting the standby node, so I won't go into details.
pg_ctl -Z coordinator -D ${CN node data directory} [stop -m f | promote]

#GTM active/standby switchover
## Simulate GTM main fault

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop
```
## Promote GTM backup to primary

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm promote
```
## CN01 main route change

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```
## CN02 main route change

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```
## DN01 main route change

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23001 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```

**Note that you need to connect to the new master here**
## DN02 main route change

```

[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.47 -p 23002 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter gtm node gtm_1 with (host='172.16.0.47',port=21000);
```
