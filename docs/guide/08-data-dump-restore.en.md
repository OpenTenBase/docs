# Data import and export

## pg_dump data export tool

### pg_dump is introduced

pg\_dump is a tool for backing up a single OpenTenBase database. It creates a consistent backup even if the database is being used concurrently. pg\_dump does not block other users from accessing the database (reading or writing).

The backup data can be in script or archive file format. The script contents contain plain text data for SQL commands, and they can be used to rebuild the database to the state it was in when it was backed up. To restore one such script, you need to use the psql client tool. The script file can also be used to reconstruct the database on another machine. With some modifications, you can also refactor your database on other SQL database products. Another optional archive file format must be used in conjunction with pg\_restore to rebuild the database. pg\_dump provides a flexible archiving and transfer mechanism. pg\_dump can be used to back up the entire database, and pg\_restore can then be used to examine the archive and/or select which parts of the database are to be restored. pg\_restore supports parallel recovery and is compressed by default.

### Introduction to database connection parameters
-d dbname --dbname=dbname Specifies the name of the database to connect to, otherwise it is taken from the PGDATABASE environment variable (if set).

-h host --host=host Specifies the hostname or ip address of the machine to connect to. When not specified, it is assumed to be obtained from the PGHOST environment variable (if set).

-p port --port=port Specifies the TCP port on which the server should listen; if not specified, the default is the PGPORT environment variable (if set); otherwise, the default value compiled from the application is used.

-U username --username=username Specifies the username to connect to the service.If not specified, it defaults to the PGUSER environment variable (if set), otherwise it defaults to the current operating system username.

-w --no-password Never emits a password prompt. If the server asks for password authentication and has no other way to provide the password (for example, a.pgpass file), then the connection attempt will fail. This option is useful for batch jobs and scripts where there is no user to enter a password.

-W --password forces pg\_dump to prompt for a password before connecting to a database.

### Introduction to Use
#### Whole library backup
-	Back up to text format


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 >/data/opentenbase/opentenbase.sql
```

-	Back up to archive format


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -Fc>/data/opentenbase/opentenbase.sql  
```

#### Only objects in the specified mode are backed up
Back up opentenbase objects


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -n opentenbase>/data/opentenbase/opentenbase.sql
```

Back up objects in opentenbase and pgxz mode, using multiple -n groups for multiple modes


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -n opentenbase -n pgxz>/data/opentenbase/opentenbase.sql
```

#### Objects in the specified mode are not backed up

opentenbase objects are not backed up


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -N opentenbase>/data/opentenbase/opentenbase.sql
```

Objects in opentenbase and pgxz mode are not backed up. Multiple -N groups are used for multiple modes


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -N opentenbase -N pgxz>/data/opentenbase/opentenbase.sql
```

#### Back up only certain tables

Backup data table opentenbase.t


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -t 'opentenbase.t' >/data/opentenbase/opentenbase.sql
```

Backup data tables opentenbase.t, pgxz.t


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -t 'opentenbase.t' -t 'pgxz.t1'>/data/opentenbase/opentenbase.sql
```

Back up all tables starting with t in opentenbase mode


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -t 'opentenbase.t*' >/data/opentenbase/opentenbase.sql
```

#### Not backing up some tables

Do not back up the table opentenbase.t


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -T 'opentenbase.t' >/data/opentenbase/opentenbase.sql
```

Do not back up data tables opentenbase.t, pgxz.t1


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -T 'opentenbase.t' -T 'pgxz.t1'>/data/opentenbase/opentenbase.sql
```

Do not back up all tables starting with t in opentenbase mode


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -T 'opentenbase.t*' >/data/opentenbase/opentenbase.sql
```

#### Only object definitions are backed up


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -s >/data/opentenbase/opentenbase.sql
```

#### Back up only the data


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 -a >/data/opentenbase/opentenbase.sql
```

#### The backup data format is insert values(xxx).


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 --inserts >/data/opentenbase/opentenbase.sql
```

#### The format of the backup data is insert(xxx) values(xxx)


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 --column-inserts >/data/opentenbase/opentenbase.sql
```

#### Backup tape group information


```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 --include-nodes >/data/opentenbase/opentenbase.sql
```

#### Do not back up data with non-log tables

```
pg_dump -h 127.0.0.1 -U opentenbase -d postgres -p 15432 --no-unlogged-table-data >/data/opentenbase/opentenbase.sql
```

## pg_dumpall data export tool
### pg_dumpall

pg\_dumpall is the tool used to back up all databases in OpenTenBase, so you can't specify a database when using pg\_dumpall. It creates a consistent backup even if the database is being used concurrently. pg\_dumpall does not block other users from accessing the database (reading or writing). The difference from pg\_dump is that pg\_dumpall can be used to back up OpenTenBase global objects, such as users and tablespace definitions. There is no way for pg\_dumpall to specify the format of the backup data when backing up, that is, there is no way to use arguments like -Fc.

### Introduction to database connection parameters

-h host --host=host Specifies the hostname or ip address of the machine to connect to. When not specified, it is assumed to be obtained from the PGHOST environment variable (if set).

-p port --port=port Specifies the TCP port on which the server should listen; if not specified, the default is the PGPORT environment variable (if set); otherwise, the default value compiled from the application is used.

-U username --username=username Specifies the username to connect to the service.If not specified, it defaults to the PGUSER environment variable (if set), otherwise it defaults to the current operating system username.

-w --no-password Never emits a password prompt. If the server asks for password authentication and has no other way to provide the password (for example, a.pgpass file), then the connection attempt will fail. This option is useful for batch jobs and scripts where there is no user to enter a password.

-W --password forces pg\_dump to prompt for a password before connecting to a database.

-l dbname --database=dbname specifies which database to connect to to backup the global object and discover which other databases to backup. If not specified, the postgres database will be used, or template1 will be used if postgres does not exist.

### Introduction to Use
#### Only global objects are backed up


```
pg_dumpall -h 127.0.0.1 -U opentenbase -p 15432 -g >/data/opentenbase/opentenbase.sql
```

#### Only user roles are backed up


```
pg_dumpall -h 127.0.0.1 -U opentenbase -p 15432 -r >/data/opentenbase/opentenbase.sql
```

#### Back up only table Spaces


```
pg_dumpall -h 127.0.0.1 -U opentenbase -p 15432 -t>/data/opentenbase/opentenbase.sql
```

## pg_restore data import tool

### pg_restore

pg\_restore is a tool for restoring PostgreSQL databases from non-text archives created by pg\_dump. These archives also allow pg\_restore to choose what content to restore. pg\_restore can operate in two modes. If you specify a database name, pg\_restore connects to that database and restores the archive content directly to it. Otherwise, a script containing the necessary SQL commands to rebuild the database is created and written to a file or standard output. This script outputs the plaintext output equivalent to pg\_dump. Therefore, some of the options for controlling the output are similar to those for pg\_dump.

### Introduction to Connection Parameters

-d dbname --dbname=dbname Specifies the name of the database to connect to.

-h host --host=host Specifies the hostname or ip address of the machine to connect to. When not specified, it is assumed to be obtained from the PGHOST environment variable (if set).

-p port --port=port Specifies the TCP port on which the server should listen; if not specified, the default is the PGPORT environment variable (if set); otherwise, the default value compiled from the application is used.

-U username --username=username Specifies the username to connect to the service.If not specified, it defaults to the PGUSER environment variable (if set), otherwise it defaults to the current operating system username.

-w --no-password Never emits a password prompt. If the server asks for password authentication and has no other way to provide the password (for example, a.pgpass file), then the connection attempt will fail. This option is useful for batch jobs and scripts where there is no user to enter a password.

-W --password forces pg\_restore to prompt for a password before connecting to a database.

### Introduction to Use

#### The output is in plain text format equivalent to pg_dump


```
pg_restore opentenbase.dump
```

Do not use the -d dbname argument, and the pg\_restore output is equivalent to the plain text output of pg\_dump.

#### The output text is redirected to a file


```
pg_restore opentenbase.dump -f  opentenbase.sql 
```
Or get


```
pg_restore opentenbase.dump > opentenbase.sql  
```

Redirect the output text to the opentenbase.sql file.

#### The database is created before recovery


```
pg_dump -h 127.0.0.1 -p 15432 -U opentenbase -d opentenbase -Fc > opentenbase.dump
dropdb -h 127.0.0.1 -p 15432 -U opentenbase opentenbase   
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -C -d postgres opentenbase.dump 
```

When using this option, the DATABASE mentioned by -d is only used to issue the initial DROP DATABASE and CREATE DATABASE commands. All data to be restored to that database name appears in the archive

#### Only the ddl is restored


```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -d opentenbase -s opentenbase.dump
```

#### Recovering data only


```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -d opentenbase -a opentenbase.dump
```

#### Clear database objects before recreating them

```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -d opentenbase -c opentenbase.dump
```

#### Restores only certain modes


```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -n 'public' -d opentenbase opentenbase.dump
```

#### Restore only certain tables

Restore t_txt tables in all modes


```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -t 't_txt' -d opentenbase opentenbase.dump
```

Restore t_txt table and t table in all modes


```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -t 't_txt' -t 't' opentenbase.dump
```

Restore t_txt in public mode


```
pg_restore -h 127.0.0.1 -U opentenbase -p 15432 -n 'public' -t 't_txt' -d opentenbase opentenbase.dump
```

## psql data import tool
### Introduction to psql
 
psql is a terminal-based OpenTenBase client-side tool similar to Oracle's command-line sqlplus, but much more powerful. It allows you to interactively type queries, send them to OpenTenBase, and view the results. Alternatively, the input can come from a file or command-line argument. In addition, psql provides several meta-commands and a variety of shell-like features to facilitate scripting and automating a variety of tasks. psql also supports command completion and history command rollback.

### Introduction to database connection parameters

-d dbname --dbname=dbname Specifies the name of the database to connect to, otherwise it is taken from the PGDATABASE environment variable (if set).

-h host --host=host Specifies the hostname or ip address of the machine to connect to. When not specified, it is assumed to be obtained from the PGHOST environment variable (if set).

-p port --port=port Specifies the TCP port on which the server should listen; if not specified, the default is the PGPORT environment variable (if set); otherwise, the default value compiled from the application is used.

-U username --username=username Specifies the username to connect to the service.If not specified, it defaults to the PGUSER environment variable (if set), otherwise it defaults to the current operating system username.

-w --no-password Never emits a password prompt. If the server asks for password authentication and has no other way to provide the password (for example, a.pgpass file), then the connection attempt will fail. This option is useful for batch jobs and scripts where there is no user to enter a password.

-W --password forces pg\_dump to prompt for a password before connecting to a database.

### Introduction to Use
#### psql executes all commands in an sql file

-	Executing externally


```
[pgxz@VM_0_3_centos ~]$ cat /data/opentenbase/opentenbase.sql 
set search_path = public;
insert into opentenbase values(1,2);
select count(1) from opentenbase;
```


```
[pgxz@VM_0_3_centos ~]$ psql -h 172.16.0.29 -p 15432 -U opentenbase -d postgres -f /data/opentenbase/opentenbase.sql 
SET
INSERT 0 1
 count 
-------
 10001
(1 row)
```

- Execute internally


```
[pgxz@VM_0_3_centos ~]$ psql -h 172.16.0.29 -p 15432 -U opentenbase -d postgres 
psql (PostgreSQL 10 (opentenbase 2.01))
Type "help" for help.

postgres=# \i  /data/opentenbase/opentenbase.sql 
SET
INSERT 0 1
 count 
-------
 10002
(1 row)

```

## Conclusion
OpenTenBase is an enterprise-class distributed HTAP database management system. Through a single database cluster, Opentenbase provides customers with high consistency distributed database services and high performance data warehouse services at the same time, forming a complete set of integrated enterprise-level solutions. Please feel free to leave a message when you encounter any related problems in the field of database.