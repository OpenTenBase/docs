# Component Installation and Management

>In [Quick Start](01-quickstart.md), we introduce the architecture of OpenTenBase, source code compilation and installation, cluster running status, startup and stop, etc.
>
>In [Application Access](02-access.md), we describe how applications can connect to OpenTenBase databases for database creation, table creation, data import, and query.
>
>In [Basic Usage](03-basic-use.md), we introduce the creation of shard tables, hot and cold partition tables, and replication tables in OpenTenBase, as well as basic DML operations.
>
>In [Advanced Usage](04-advanced-use.md), we introduce the advanced usage of OpenTenBase, which includes the use of various window functions, Json/Jsonb, cursors, transactions, locks, etc.
>
>In this article, we will delve into the various components of OpenTenBase and introduce the initialization, parameter configuration, start-stop, running status viewing, and route effective configuration of each component in detail.

## Machine preparation

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


# GTM Master Management
## initialize

```
[opentenbase@VM_0_29_centos ~]# mkdir -p /data/opentenbase/data/pgxz
[opentenbase@VM_0_29_centos ~]# initgtm -Z gtm -D /data/opentenbase/data/pgxz/gtm
```

## Parameter Configuration

```
#Configure the gtm node name
nodename = gtm_1 

#Allowed service listening range, * Allowed to listen to all IP addresses  
listen_addresses = '*' 

#Listen on the port number
port = 21000

#Provide services as a GTM masternode
startup = ACT
```

## Service management
-	Start the service

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm start
```

-	Turn off the service

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop
```

-	Query status

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm status -H 127.0.0.1 -P 21000
```

# GTM standby management
## initialize

```
[opentenbase@VM_0_47_centos ~]# mkdir -p /data/opentenbase/data/pgxz
[opentenbase@VM_0_47_centos ~]# initgtm -Z gtm -D /data/opentenbase/data/pgxz/gtm
```
## Parameter configuration

```
[opentenbase@VM_0_47_centos ~]# vim /data/opentenbase/data/pgxz/gtm/gtm.conf
#Configure the name of the gtm node
nodename = gtm_1

#Allow service listening range,* Allow listening to all IP addresses
listen_addresses = '*' 

#Listen on the port number
port = 21000

#Provided as a standby node for GTM
startup = STANDBY 

#Configure the GTM master node information
active_host = '172.16.0.29' 
active_port = 21000
```

## Service management
-	Start the service

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm start
```

-	Turn off the service

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop
```

-	Query status

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm status -H 127.0.0.1 -P 21000
```

# CN01 management
## initialize

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
-	Start the service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 start
```

-	Turn off the service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 stop -m f #Quick shutdown
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 stop -m i #Force shutdown
```

-	Overload parameters

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn01 reload
```

-	Query status

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn01 status
```

# CN02 management
## initialize
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

-	Start the service 
 
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 start
```

-	Turn off the service
  
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 stop -m f #Quick shutdown
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 stop -m i #Force shutdown
```

-	Overload parameters
  
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn02 reload
```

-	Query status 
 
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn02 status
```

# DN01 master management
## initialize

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

-	Start the service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 start
```

-	Turn off the service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f #Quick shutdown
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m i #Force shutdown
```

-	Overload parameters

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 reload
```

-	Query status

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 status
```

# DN02 master management
## initialize

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

-	Start the service

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 start
```

-	Turn off the service

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m f #Quick shutdown
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m i #Force shutdown
```

-	Overload parameters

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 reload
```

-	Query status

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 status
```

# DN01 slave management
## generat slave node

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

-	Start the service

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 start
```

-	Turn off the service

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f #Quick shutdown
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m i #Force shutdown
```

-	Overload parameters

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 reload
```

-	Query status

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 status
```

# DN02 slave management
## generat slave node

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

- Start the service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 start
```

- Turn off the service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m f #Quick shutdown
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m i #Force shutdown
```

- Overload parameters

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 reload
```

- Query status

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 status
```

# Route configuration
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

## Route table information  

The following table shows the routing information of all nodes

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

# GROUP (storage group) configuration
## Create a default GROUP  

Create a default GROUP

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#
create default node group default_group with(dn01, dn02);
create sharding group to group default_group;
clean sharding;
```

At this point, OpenTenBase can be used like a stand-alone database.

## QUERY THE CREATED GROUP

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase

select * from pgxc_group;

```
