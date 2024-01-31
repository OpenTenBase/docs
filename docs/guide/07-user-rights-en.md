# User Rights Management

## Create user

### Create common user

User Administrator `opentenbase` connect to a `cn` node, the following operations are the same.

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# create role user1 with login password 'user1@123';
CREATE ROLE
```

Instructions:

- Above we created user `user1`, `with` is some properties that specify the user.
- `login` means that the user can log in.
- `user1@123` is the user's password.

### Create administrator user

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (Postgr
eSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# create role opentenbaseadmin with login password 'opentenbaseadmin @123' superuser;
CREATE ROLE
```

Instructions:

- `with superuser` specifies that the user is an administrator.  

### More properties of users

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# create role user1 with login password 'user1@123' createdb createrole replication CONNECTION LIMIT 100 VALID UNTIL '2023-09-30 23:59:59';
CREATE ROLE
```

Instructions:

- `createdb` means the user can create a database.
- `createrole` means the user can create a user.
- `replication` means the user can be used for data synchronization and replication configuration.
- `CONNECTION LIMIT 100` means the maximum number of connections for the user is 100. Note that the `dn` nodes of `opentenbase` will also connect to each other. `-1` (default) means no limit.
- `VALID UNTIL '2023-09-30 23:59:59'` means the user's password expires timestamp. `VALID UNTIL 'infinity'` makes the password never expired.

## Modify properties of users
### No access for user login

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter role user1 with nologin ;
ALTER ROLE

postgres=# alter role user1 with login ;
ALTER ROLE
```

### Set user as administrator and non-administrator

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#  alter role user1 with superuser ;
ALTER ROLE

postgres=#  alter role user1 with nosuperuser ;
ALTER ROLE
```

### Limit of user connections

```
[opentenbase@VM_0_29_centos  ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter role user1 with CONNECTION LIMIT 100;
ALTER ROLE

postgres=# alter role user1 with CONNECTION LIMIT -1; 
ALTER ROLE
```

Instructions:

- `CONNECTION LIMIT 100` means the maximum number of connections for the user is 100. Note that the `dn` nodes of `opentenbase` will also connect to each other. `-1` (default) means no limit.

### Set user password expire time

``` 
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter role user1 with VALID UNTIL '2023-09-30 23:59:59';
ALTER ROLE

postgres=# alter role user1 with VALID UNTIL 'infinity'; 
ALTER ROLE
```

Instructions:

-	`VALID UNTIL '2023-09-30 23:59:59'` means the user's password expires timestamp. `VALID UNTIL 'infinity'` makes the password never expired.

### Change user password

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

--Method1
postgres=# role user1 with password 'user1@123' ;
ALTER ROLE


--Method2
postgres=# \password user1
Enter new password: 
Enter it again: 
postgres=#  
```
Input the password twice continuously. It is safer to modify the password using the `\password username` method, because the password information is not recorded in the log file.

### More properties of users

```
[opentenbase@VM_0_29_centos  ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter role user1 with createdb createrole replication;
CREATE ROLE

postgres=# alter role user1 with nocreatedb nocreaterole noreplication ;
CREATE ROLE
```

Instructions:

- `createdb/nocreatedb` means users can create database or not.
- `createrole/nocreaterole` means users can create user or not.
- `replication/nocreaterole` means users can be used for data synchronization and replication configuration or not.

## Query user
### psql query user

```
[opentenbase@VM_0_29_centos  ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# \du
                                      List of roles
   Role name    |                         Attributes                         | Member of 
----------------+------------------------------------------------------------+-----------
 audit_admin    | No inheritance                                             | {}
 mls_admin      | No inheritance                                             | {}
 opentenbase          | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
 opentenbase_01_admin | Superuser                                                  | {}
 opentenbaseadmin     | Superuser, Create role, Create DB                          | {}
 user1          | Password valid until infinity                              | {}
```

Instructions:

- `Attributes` shows the user's properties.

### Query user system table

```
[opentenbase@VM_0_29_centos  ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# select * from pg_roles where rolname='opentenbase';
-[ RECORD 1 ]--+---------
rolname        | opentenbase
rolsuper       | t
rolinherit     | t
rolcreaterole  | t
rolcreatedb    | t
rolcanlogin    | t
rolreplication | t
rolconnlimit   | -1
rolpassword    | ********
rolvaliduntil  | 
rolbypassrls   | t
rolconfig      | 
oid            | 10
```

## Delete user

```
[opentenbase@VM_0_29_centos  ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# drop role user1 ;
DROP ROLE
```

Instructions:

- If the user already has a table, it cannot be deleted. If the user is not allowed to use, you can use `nologin` to disable the user login.

## User&Resource Management

The default resource search path for `opentenbase` is:

```
postgres=# show search_path ;
   search_path   
-----------------
 "$user", public
(1 row)
```

access resource (such as table, view, etc.) The first search mode is the same as the user name, and the second is the public path.

### Configure the user's default search mode

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter role user1 set search_path to opentenbase,"$user", public;
ALTER ROLE

postgres=#  alter role user1 set search_path to DEFAULT ;
ALTER ROLE
postgres=# 

```

Instructions:

- Set the `user1`'s search path to `opentenbase`, `user1`, `public`.
- to `Default` sets the user's search mode to the system default value.

### Add a schema to a user

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# create schema user1 AUTHORIZATION user1;

```

Instructions:  

- `AUTHORIZATION user1` specifies that the schema belongs to the user `user1`.

# Authorization Management
## Authorization Mode Management
### Authorize user to access schema

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# grant usage on SCHEMA mysch to user1;
GRANT
postgres=#
```

Instructions:  

- By Default, common users cannot access unauthorized schema. If the user needs to access some table, you need authorize the table's schema to user.
- If schema access is not controlled, Hint `ERROR:  permission denied for schema mysch`.

### Withdraw user access to schema

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# revoke usage on SCHEMA mysch from user1;
REVOKE
```

### Change schema owner

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter schema mysch owner to user1;
ALTER SCHEMA
```

## Table Authorization Management
### Authorize user can add, delete, modify, and query a table

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# grant ALL on mysch.t2 to user1;
GRANT

postgres=# grant SELECT on mysch.t2 to user1;
GRANT
postgres=# 
```

Instructions:

- Add, delete, modify, and query correspond to `INSERT`, `DELETE`, `UPDATE`, and `SELECT`.
- If need all permissions, use `ALL` instead.

### Remove user permission

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# revoke ALL on mysch.t2 from user1; 
REVOKE

postgres=# revoke select on mysch.t2 from user1;   
REVOKE
```

### Table sequences with sequences also need to be authorized

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# create table mysch.t3(f1 serial,f2 int);
CREATE TABLE
postgres=# \d+  mysch.t3
                                                   Table "mysch.t3"
 Column |  Type   | Collation | Nullable |               Default                | Storage | Stats target | Description 
--------+---------+-----------+----------+--------------------------------------+---------+--------------+-------------
 f1     | integer |           | not null | nextval('mysch.t3_f1_seq'::regclass) | plain   |              | 
 f2     | integer |           |          |                                      | plain   |              | 
Distribute By: SHARD(f1)
Location Nodes: ALL DATANODES

postgres=# 

-- Authorize need this
postgres=# grant all on mysch.t3 to user1 ;
GRANT

postgres=# grant all on SEQUENCE mysch.t3_f1_seq to user1;             
GRANT

```

Instructions:

- If no permission, Hint `ERROR: permission denied for relation t3_f1_seq`.

### Assign all tables in a schema to a user

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#  grant ALL ON ALL TABLES IN SCHEMA  mysch  TO user1;
GRANT
```

### Revoke all table access permissions in a schema

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# revoke ALL ON ALL TABLES IN SCHEMA  mysch  FROM user1;       
REVOKE
```

# Epilogue

`OpenTenBase` is an Enterprise-class distributed HTAP database management system. It provides high-consistency distributed database services and high-performance data warehouse services for customers through a single database cluster, forming a set of integrated enterprise solutions. If you have any questions in the database field, please feel free to leave us a message.