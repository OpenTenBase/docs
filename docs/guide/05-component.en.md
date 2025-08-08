# Component Installation and Management

>In [Quick Start](01-quickstart.en.md) article, we introduced opentenbase architecture, source code compilation and installation, cluster running status, startup and stop, etc.
>
>In [Access](02-access.md) article, we introduced the application program to connect opentenbase for database creation, table creation, data import, query and other operations.
>
>In [Basic Use](03-basic-use.md) article, we introduced the creation of shard table, cold and hot partition table, replication table in opentenbase, and basic DML operations.
>
>In [Advanced Use](04-advanced-use.md) article, we introduced the advanced use of opentenbase, including the use of various window functions, Json/Jsonb, cursors, transactions, locks, etc.
>
>In this article, we dive into the internal of various components of opentenbase, and introduced the initialization, parameter configuration, startup and stop, running status viewing, routing effective configuration of various components separately.

## Hardware Requirements

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

- Create operating system running user

```
[root@VM_0_29_centos ~]# adduser -d /data/opentenbase opentenbase
```

-	Configure the operating system user password

```
[root@VM_0_29_centos pgxztmp]# passwd opentenbase
```

-	Create opentenbase application program running directory

```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/install/pgxz
```

-	Create opentenbase data directory

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


# GTM master management

## Initialization

```
[opentenbase@VM_0_29_centos ~]# mkdir -p /data/opentenbase/data/pgxz
[opentenbase@VM_0_29_centos ~]# initgtm -Z gtm -D /data/opentenbase/data/pgxz/gtm
```

## Parameter configuration

```
#Configuration gtm node name
nodename = gtm_1 

#Allow service listening range, `*` means allow listening to all IP addresses
listen_addresses = '*' 

#Listening port number
port = 21000

#GTM master node running
startup = ACT
```

## Service management

-	Start service

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm start
```

-	Stop service

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop
```

-	Status query

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm status -H 127.0.0.1 -P 21000
```

# GTM standby management

## Initialization

```
[opentenbase@VM_0_47_centos ~]# mkdir -p /data/opentenbase/data/pgxz
[opentenbase@VM_0_47_centos ~]# initgtm -Z gtm -D /data/opentenbase/data/pgxz/gtm
```

## Parameter configuration

```
[opentenbase@VM_0_47_centos ~]# vim /data/opentenbase/data/pgxz/gtm/gtm.conf
#Configuration gtm node name
nodename = gtm_1

#Allow service listening range, `*` means allow listening to all IP addresses
listen_addresses = '*' 

#Listening port number
port = 21000

#GTM standby node running
startup = STANDBY 

#Configuration GTM master node IP and port
active_host = '172.16.0.29' 
active_port = 21000
```

## Service Management

-	Start service

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm start
```

-	Stop service

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop
```

-	Status query

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm status -H 127.0.0.1 -P 21000
```

# CN01 management

## Initialization

```
[opentenbase@VM_0_29_centos ~]# initdb --locale=zh_CN.UTF-8 -U opentenbase -E utf8 -D /data/opentenbase/data/pgxz/cn01 --nodename=cn01 --nodetype=coordinator --master_gtm_nodename gtm_1 --master_gtm_ip 172.16.0.29 --master_gtm_port 21000
```

## Parameter configuration

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

## Service management

-	Start service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 start
```

-	Stop service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 stop -m f #quick stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 stop -m i #force stop
```

-	Reload parameter

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn01 reload
```

-	Status query

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn01 status
```

# CN02 management

## Initialization

```
[opentenbase@VM_0_47_centos ~]# initdb --locale=zh_CN.UTF-8 -U opentenbase -E utf8 -D /data/opentenbase/data/pgxz/cn02 --nodename=cn02 --nodetype=coordinator --master_gtm_nodename gtm_1 --master_gtm_ip 172.16.0.29 --master_gtm_port 21000
```

## Parameter configuration

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

## Service management

-	Start service

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 start
```

-	Stop service
  
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 stop -m f #quick stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 stop -m i #force stop
```

-	Reload parameter
  
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn02 reload
```

-	Status query
 
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn02 status
```

# DN01 master management

## Initialization

```
[opentenbase@VM_0_29_centos ~]# initdb --locale=zh_CN.UTF-8 -U opentenbase -E utf8 -D /data/opentenbase/data/pgxz/dn01 --nodename=dn01 --nodetype=datanode --master_gtm_nodename gtm_1 --master_gtm_ip 172.16.0.29 --master_gtm_port 21000
```

## Parameter configuration

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

## Service management

- Start service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 start
```

- Stop service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f #quick stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m i #force stop
```

- Reload parameter

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 reload
```

- Status query

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 status
```

# DN02 master management

## Initialization

```
[opentenbase@VM_0_47_centos ~]# initdb --locale=zh_CN.UTF-8 -U opentenbase -E utf8 -D /data/opentenbase/data/pgxz/dn02 --nodename=dn02 --nodetype=datanode --master_gtm_nodename gtm_1 --master_gtm_ip 172.16.0.29 --master_gtm_port 21000
```

## Parameter configuration

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

## Service management

- Start service

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 start
```

- Stop service

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m f #quick stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m i #force stop
```

- Reload parameter

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 reload
```

- Status query

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 status
```

# DN01 standby management

## Initialize standby node

```
[opentenbase@VM_0_47_centos ~]# pg_basebackup -p 23001 -h 172.16.0.29 -U opentenbase -D /data/opentenbase/data/pgxz/dn01 -X f -P -v
```

## Parameter configuration

```
[opentenbase@VM_0_47_centos ~]# vim /data/opentenbase/data/pgxz/dn01/recovery.conf

standby_mode = on 
primary_conninfo = 'host = 172.16.0.29 port = 23001 user = opentenbase application_name = s1'
```

## Service management

- Start service

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 start
```

- Stop service

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f #quick stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m i #force stop
```

- Reload parameter

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 reload
```

- Status query

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 status
```

# DN02 standby management

## Initialize standby node

```
[opentenbase@VM_0_29_centos ~]# pg_basebackup -p 23002 -h 172.16.0.47 -U opentenbase -D /data/opentenbase/data/pgxz/dn02 -X f -P -v
```

## Parameter configuration

```
[opentenbase@VM_0_29_centos ~]# vim /data/opentenbase/data/pgxz/dn02/recovery.conf

standby_mode = on 
primary_conninfo = 'host = 172.16.0.47 port = 23002 user = opentenbase application_name = s1'
```

## Service management

- Start service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 start
```

- Stop service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m f #quick stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m i #force stop
```

- Reload parameter

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 reload
```

- Status query

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 status
```

# Route configuration
## CN01

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

## CN02

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

## DN01

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

## DN02

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

## Route information 

All nodes route information configuration is completed as follows

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

# GROUP Configuration

## Create default GROUP  

- Create default GROUP

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#
create default node group default_group with(dn01, dn02);
create sharding group to group default_group;
clean sharding;
```

Now, OpenTenBae can be used like a single node database.

## Query existing GROUP

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase

select * from pgxc_group;

```
