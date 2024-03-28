# Component Install & Manager

>In the [Quick Start](01-quickstart.en.md) article, we introduced the architecture, source code compilation and installation, cluster operation status, startup and shutdown procedures of OpenTenBase.
>
> In [Application Access](02-access.en.md), we covered how to connect applications to the OpenTenBase database for tasks like creating databases, tables, importing data, and querying.
>
>In [Basic Usage](03-basic-use.en.md), we introduced the creation of shard tables,hot and cold partition tables, and replicated tables unique to OpenTenBase, along with basic DML operations.
>
>In [Advanced Usage](04-advanced-use.en.md), we delve into advanced operations in OpenTenBase, including various window functions, Json/Jsonb, cursors, transactions, locks, and more.
>
>In this article, we will delve into the internals of various components of OpenTenBase, providing detailed explanations of their initialization, parameter configuration, startup and shutdown procedures, viewing running statuses, and route configuration.

## Machine Preparation

- Number of Servers  
  2 Unit, IP address: 172.16.0.29, 172.16.0.47

- Hardware Configuration  

  CPU   : 4C   
  Memory: 8G   
  System Disk: 50G  
  Data   Disk: 200G  

- Operating System Requirement  

  centos7.3  

## Creating OS User

-   Creating an operating system user:

```
[root@VM_0_29_centos ~]# adduser -d /data/opentenbase opentenbase
```

-	Configuration the operating system user password:

```
[root@VM_0_29_centos pgxztmp]# passwd opentenbase
```

-	Creating the OpenTenBase application running directory:  

```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/install/pgxz
```

-	Creating the OpenTenBase data directory:

```
[root@VM_0_29_centos pgxz]# su opentenbase  
[opentenbase@VM_0_29_centos install]$ mkdir -p /data/opentenbase/data/pgxz
```

-	Uploading the OpenTenBase application to the directory /data/opentenbase/install/pgxz, with the following structure:  

```
[opentenbase@VM_0_29_centos pgxz]$ ll /data/opentenbase/install/pgxz
total 4
drwxrwxr-x 2 pgxz pgxz 4096 Nov 10 04:33 bin
drwxrwxr-x 4 pgxz pgxz  189 Nov 10 04:33 include
drwxrwxr-x 4 pgxz pgxz  172 Nov 10 04:33 lib
drwxrwxr-x 3 pgxz pgxz   24 Oct  1 14:54 share
[opentenbase@VM_0_29_centos pgxz]$ 
```

- Configuration the environment variables for the pgxz User:

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

## Configuration Global Parameters

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

## Installing And Configuring Topology


Node Name|     IP	    |  Directory
-------|:-----------:|-------------------------
gtm Master      | 172.16.0.29    | /data/opentenbase/data/pgxz/gtm
gtm Standby	    | 172.16.0.47	 | /data/opentenbase/data/pgxz/gtm
cn01	        | 172.16.0.29	 | /data/opentenbase/data/pgxz/cn01
cn02        	| 172.16.0.47	 | /data/opentenbase/data/pgxz/cn02
dn01 Master     | 172.16.0.29	 | /data/opentenbase/data/pgxz/dn01
dn01 Standby	| 172.16.0.47	 | /data/opentenbase/data/pgxz/dn01
dn02 Master  	| 172.16.0.47	 | /data/opentenbase/data/pgxz/dn02
dn02 Standby	| 172.16.0.29	 | /data/opentenbase/data/pgxz/dn02


# GTM Master Management
## Initialiaztion

```
[opentenbase@VM_0_29_centos ~]# mkdir -p /data/opentenbase/data/pgxz
[opentenbase@VM_0_29_centos ~]# initgtm -Z gtm -D /data/opentenbase/data/pgxz/gtm
```

## Parameters Configuration

```
# Configure GTM node name
nodename = gtm_1 

# Allow service monitoring range, *Allow monitoring of all IP addresses

listen_addresses = '*' 

# Port number to listen on
port = 21000

# Serve as the primary GTM node
startup = ACT
```

## Service Management
-	Start Service

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm start
```

-	Stop Service

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop
```

-	Check Status

```
[opentenbase@VM_0_29_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm status -H 127.0.0.1 -P 21000
```

# GTM Standby Management
## Initialiaztion

```
[opentenbase@VM_0_47_centos ~]# mkdir -p /data/opentenbase/data/pgxz
[opentenbase@VM_0_47_centos ~]# initgtm -Z gtm -D /data/opentenbase/data/pgxz/gtm
```
## Parameters Configuration

```
[opentenbase@VM_0_47_centos ~]# vim /data/opentenbase/data/pgxz/gtm/gtm.conf
# Configuration GTM node name
nodename = gtm_1

# Allow service monitoring range, *Allow monitoring of all IP addresses
listen_addresses = '*' 

# Port number listen on
port = 21000

# Serve as standby GTM node 
startup = STANDBY 

# Configure GTM master node information
active_host = '172.16.0.29' 
active_port = 21000
```

## Service Management
-	Start Service

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm start
```

-	Stop Service

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm stop
```

-	Check Status

```
[opentenbase@VM_0_47_centos ~]# gtm_ctl -Z gtm -D /data/opentenbase/data/pgxz/gtm status -H 127.0.0.1 -P 21000
```

# cn01 Management
## Initialiaztion

```
[opentenbase@VM_0_29_centos ~]# initdb --locale=zh_CN.UTF-8 -U opentenbase -E utf8 -D /data/opentenbase/data/pgxz/cn01 --nodename=cn01 --nodetype=coordinator --master_gtm_nodename gtm_1 --master_gtm_ip 172.16.0.29 --master_gtm_port 21000
```

## Parameters Configuration

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

## Service Management
-	Start Service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 start
```

-	Stop Service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 stop -m f #quick close
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn01 stop -m i #force close
```

-	Overriede

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn01 reload
```

-	Check Status

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn01 status
```

# cn02 Management
## Initialiaztion
```
[opentenbase@VM_0_47_centos ~]# initdb --locale=zh_CN.UTF-8 -U opentenbase -E utf8 -D /data/opentenbase/data/pgxz/cn02 --nodename=cn02 --nodetype=coordinator --master_gtm_nodename gtm_1 --master_gtm_ip 172.16.0.29 --master_gtm_port 21000
```

## Parameters Configuration
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

## Service Management

-	Start Service 
 
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 start
```

-	Stop Service
  
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 stop -m f #quick close
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z coordinator -D /data/opentenbase/data/pgxz/cn02 stop -m i #force close
```

-	Overload Parameters
  
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn02 reload
```

-	Check Status
 
```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/cn02 status
```

# dn01 Master Management
## Initialiaztion

```
[opentenbase@VM_0_29_centos ~]# initdb --locale=zh_CN.UTF-8 -U opentenbase -E utf8 -D /data/opentenbase/data/pgxz/dn01 --nodename=dn01 --nodetype=datanode --master_gtm_nodename gtm_1 --master_gtm_ip 172.16.0.29 --master_gtm_port 21000
```

## Parameters Configuration

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

## Service Management

-	Start Service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 start
```

-	Stop Service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f #quick close
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m i #force close
```

-	Overload Parameters

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 reload
```

-	Check Status

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 status
```

# dn02Master Management
## Initialization

```
[opentenbase@VM_0_47_centos ~]# initdb --locale=zh_CN.UTF-8 -U opentenbase -E utf8 -D /data/opentenbase/data/pgxz/dn02 --nodename=dn02 --nodetype=datanode --master_gtm_nodename gtm_1 --master_gtm_ip 172.16.0.29 --master_gtm_port 21000
```

## Parameters Configuration

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
 
## Service Management

-	Start Service

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 start
```

-	Stop Service

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m f #quick close
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m i #force close
```

-	Overload Parameters

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 reload
```

-	Check Status

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 status
```

# dn01Standby Management
## Generate standby node

```
[opentenbase@VM_0_47_centos ~]# pg_basebackup -p 23001 -h 172.16.0.29 -U opentenbase -D /data/opentenbase/data/pgxz/dn01 -X f -P -v
```

## Parameters Configuration

```
[opentenbase@VM_0_47_centos ~]# vim /data/opentenbase/data/pgxz/dn01/recovery.conf

standby_mode = on 
primary_conninfo = 'host = 172.16.0.29 port = 23001 user = opentenbase application_name = s1'
```

## Service Management

-	Start Service

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 start
```

-	Stop Service

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m f #quick close
[opentenbase@VM_0_47_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn01 stop -m i #force close
```

-	Overload Parameters

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 reload
```

-	Check Status

```
[opentenbase@VM_0_47_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn01 status
```

# dn02Standby Management
## Generate standby node

```
[opentenbase@VM_0_29_centos ~]# pg_basebackup -p 23002 -h 172.16.0.47 -U opentenbase -D /data/opentenbase/data/pgxz/dn02 -X f -P -v
```

## Parameters Configuration

```
[opentenbase@VM_0_29_centos ~]# vim /data/opentenbase/data/pgxz/dn02/recovery.conf

standby_mode = on 
primary_conninfo = 'host = 172.16.0.47 port = 23002 user = opentenbase application_name = s1'
```

## Service Management

- Start Service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 start
```

- Stop Service

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m f #quick close
[opentenbase@VM_0_29_centos ~]# pg_ctl -Z datanode -D /data/opentenbase/data/pgxz/dn02 stop -m i #force close
```

- Overload Parameters

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 reload
```

- Check Status

```
[opentenbase@VM_0_29_centos ~]# pg_ctl -D /data/opentenbase/data/pgxz/dn02 status
```

# Routing Configuration
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

## Routing Table Information

After configuring routing information for all nodes, the routing table looks like this

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

# GROUP（Storage Group）Configuration
## Create Default GROUP  

Create Default GROUP

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#
create default node group default_group with(dn01, dn02);
create sharding group to group default_group;
clean sharding;
```

Now, OpenTenBase can be used just like a single-node database.

## Query the Created GROUP

```
[opentenbase@VM_0_29_centos ~]# psql -h 172.16.0.29 -p 15432 -d postgres -U opentenbase

select * from pgxc_group;

```

