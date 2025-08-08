# User Management 

## Create User

### Create Regular User

Using the administrator "opentenbase" to connect to a specific "cn" node, the following operations are the same:

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# create role user1 with login password 'user1@123';
CREATE ROLE
```

Explanation:

- The above command creates a user named `user1` with specified attributes using the `with` clause.
- `login` specifies that the user can log in.
- password 'user1@123' specifies the user's password.

### Create an administrator user

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (Postgr
eSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# create role opentenbaseadmin with login password 'opentenbaseadmin @123' superuser;
CREATE ROLE
```

Explanation:

-	`with superuser` specifies that this user is an administrator

### Additional User Attribute Configuration
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# create role user1 with login password 'user1@123' createdb createrole replication CONNECTION LIMIT 100 VALID UNTIL '2023-09-30 23:59:59';
CREATE ROLE
```

Explanation:

-	`createdb` specifies that the user can create databases.
-	`createrole`specifies that the user can create other users.
-	`replication`specifies that the user can be used for data synchronization replication.
-	`CONNECTION LIMIT 100`indicates that the user's maximum connection limit is 100. Note that connections between opentenbase dn nodes will also connect to each other; `-1` (default) indicates no limit.
-	`VALID UNTIL '2023-09-30 23:59:59'` indicates the expiration time for the user's password. Use `VALID UNTIL 'infinity'` to make a password valid indefinitely.

## Modify User Attributes
### Disallow User Login 
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter role user1 with nologin ;
ALTER ROLE

postgres=# alter role user1 with login ;
ALTER ROLE
```

### Set User as Administrator and Non-Administrator
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#  alter role user1 with superuser ;
ALTER ROLE

postgres=#  alter role user1 with nosuperuser ;
ALTER ROLE
```

### User Connection Limit
```
[opentenbase@VM_0_29_centos  ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter role user1 with CONNECTION LIMIT 100;
ALTER ROLE

postgres=# alter role user1 with CONNECTION LIMIT -1; 
ALTER ROLE
```

Explanation:

-	`CONNECTION LIMIT 100` indicates that the user's maximum connection limit is 100. Note that connections between opentenbase dn nodes will also connect to each other; `-1` (default) indicates no limit.

### Set User Password Expiry Time
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter role user1 with VALID UNTIL '2023-09-30 23:59:59';
ALTER ROLE

postgres=# alter role user1 with VALID UNTIL 'infinity'; 
ALTER ROLE
```

Explanation:

-	`VALID UNTIL '2023-09-30 23:59:59'` indicates the expiration time for the user's password. Use `VALID UNTIL 'infinity'` to make a password valid indefinitely.

### Change User Password
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

--Password modification method one
postgres=# role user1 with password 'user1@123' ;
ALTER ROLE


--Password modification method two
postgres=# \password user1
Enter new password: 
Enter it again: 
postgres=#  
```

Enter the new password twice. Changing the password using `\password` is more secure because the password information is not recorded in the log file. 

### Additional User Attribute Configuration
```
[opentenbase@VM_0_29_centos  ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter role user1 with createdb createrole replication;
CREATE ROLE

postgres=# alter role user1 with nocreatedb nocreaterole noreplication ;
CREATE ROLE
```

Explanation:

-	`createdb/nocreatedb` specifies whether the user can create databases.
-	`createrole/nocreaterole` specifies whether the user can create other users.
-	`replication/nocreaterole` specifies whether the user can be used for data synchronization replication.

## Query User 
### psql Shortcut Commands for Querying 
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

Explanation:

-	`Attributes` displayed the user's attributes

### Query User System Table
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

## Drop User
```
[opentenbase@VM_0_29_centos  ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# drop role user1 ;
DROP ROLE
```

Explanation:

- If the user has existing tables, the removal may be restricted. To prevent user logins without completely removing the user, consider using `nologin` to disable user login.

## User and Resource Search Path Management

The default resource search path in OpenTenBase is:

```
postgres=# show search_path ;
   search_path   
-----------------
 "$user", public
(1 row)
```

When accessing resources such as tables and views, the system first searches for objects in a schema with a name matching the user's name. If no matching schema is found, the system then searches in the public schema.

### Configuring User's Default Search Path

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
Explanation:

-	Configures the search path for the user `user1` to include the schemas `opentenbase`, `user1`, and `public`.
-	Setting the search path for `user1` to `DEFAULT` restores the search mode to the system's default value.

### Adding a Schema to a User

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# create schema user1 AUTHORIZATION user1;

```
Explanation:  

-	The command creates a schema named `user1` with `user1` as its owner.

# Permission Management
## Schema Permission Management
### Granting User Access to a Schema

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# grant usage on SCHEMA mysch to user1;
GRANT
postgres=#
```

Explanation:

-	By default, regular users cannot access schemas without proper authorization. Therefore, granting usage permission on a schema (mysch in this case) is necessary for a user to access tables within that schema
-	If there is no permission for schema access, an error will occur: `ERROR: permission denied for schema mysch`

### Revoking User Access to a Schema

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# revoke usage on SCHEMA mysch from user1;
REVOKE
```

### Modifying the Owner of a Schema
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter schema mysch owner to user1;
ALTER SCHEMA
```

## Table Permission Management
### Granting User Permissions to Insert, Delete, Update, and Select Records in a Table
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
Explanation:

-	`ALL` permission includes the ability to insert, delete, update, and select records.
-	If granting specific permissions, ALL can be replaced with INSERT, DELETE, UPDATE, or SELECT accordingly.

### Revoking User Access Permissions
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# revoke ALL on mysch.t2 from user1; 
REVOKE

postgres=# revoke select on mysch.t2 from user1;   
REVOKE
```

### Granting Permissions for a Table with a Serial Column and Its Sequence 
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

-- Authorization must be done like this
postgres=# grant all on mysch.t3 to user1 ;
GRANT

postgres=# grant all on SEQUENCE mysch.t3_f1_seq to user1;             
GRANT

```

Explanation:

-	If permissions are not granted, it will result in an error indicating insufficient sequence access permissions (`permission denied for sequence t3_f1_seq`).

### Grant access to all tables in a schema to a specific user 
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#  grant ALL ON ALL TABLES IN SCHEMA  mysch  TO user1;
GRANT
```

### Revoke access to all tables in a schema from a specific user
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# revoke ALL ON ALL TABLES IN SCHEMA  mysch  FROM user1;       
REVOKE
```

# Conclusion
OpenTenBase is an enterprise-level distributed HTAP database management system. It provides high-consistency distributed database services and high-performance data warehouse services for customers through a single database cluster, forming a comprehensive enterprise solution. Feel free to leave us a message if you encounter any related issues in the field of databases.