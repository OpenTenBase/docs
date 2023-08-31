# 用户管理 

## 创建用户 

### 创建普通用户 

使用管理员opentenbase连接到某个cn节点，下面操作相同

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# create role user1 with login password 'user1@123';
CREATE ROLE
```

说明：

-  上面创建了用户user1，with是指定该用户的一些属性
- 	login指定该用户可以登录
-  	password  'user1@123' 指定用户的密码 

### 创建管理员用户 

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (Postgr
eSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# create role opentenbaseadmin with login password 'opentenbaseadmin @123' superuser;
CREATE ROLE
```

说明：

-	with superuser 指定该用户为管理员  

### 更多用户属性配置 
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# create role user1 with login password 'user1@123' createdb createrole replication CONNECTION LIMIT 100 VALID UNTIL '2023-09-30 23:59:59';
CREATE ROLE
```

说明：

-	createdb 指定该用户能创建数据库
-	createrole指定该用户能创建用户
-	replication批定该用户可以用于数据同步复制配置
-	CONNECTION LIMIT 100表示该用户最大连接数为100，注意，opentenbase的dn节点之间也会互相连接，-1（默认值）表示无限制。
-	VALID UNTIL '2023-09-30 23:59:59'表示用户密码到期时间截，VALID UNTIL 'infinity'，让一个口令永远有效

## 修改用户属性 
### 禁止准许用户登录 
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter role user1 with nologin ;
ALTER ROLE

postgres=# alter role user1 with login ;
ALTER ROLE
```

### 设置用户为管理员和非管理员 
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#  alter role user1 with superuser ;
ALTER ROLE

postgres=#  alter role user1 with nosuperuser ;
ALTER ROLE
```

### 用户连接数限制 
```
[opentenbase@VM_0_29_centos  ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter role user1 with CONNECTION LIMIT 100;
ALTER ROLE

postgres=# alter role user1 with CONNECTION LIMIT -1; 
ALTER ROLE
```

说明：

-	CONNECTION LIMIT 100表示该用户最大连接数为100，注意，opentenbase的dn节点之间也会互相连接，-1（默认值）表示无限制。

### 设置用户密码过时时间截 
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter role user1 with VALID UNTIL '2023-09-30 23:59:59';
ALTER ROLE

postgres=# alter role user1 with VALID UNTIL 'infinity'; 
ALTER ROLE
```
说明：

-	VALID UNTIL '2023-09-30 23:59:59'表示用户密码到期时间截，VALID UNTIL 'infinity'，让一个口令永远有效

### 修改用户密码 
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

--修改密码方法一
postgres=# role user1 with password 'user1@123' ;
ALTER ROLE


--修改密码方法二
postgres=# \password user1
Enter new password: 
Enter it again: 
postgres=#  
```
连续输入两次密码，使用\password 用户名方式修改密码更安全，因为密码信息没有记录在log日志文件中。  

### 更多的用户属性配置 
```
[opentenbase@VM_0_29_centos  ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter role user1 with createdb createrole replication;
CREATE ROLE

postgres=# alter role user1 with nocreatedb nocreaterole noreplication ;
CREATE ROLE
```

说明：

-	createdb/nocreatedb 指定该用户能否创建数据库
-	createrole/nocreaterole指定该用户能否创建用户
-	replication/nocreaterole批定该用户是否可用于数据同步复制

## 查询用户 
### psql快捷命令查询 
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

说明：

-	Attributes 显示了该用户的属性  

### 查询用户系统表 
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

## 删除用户 
```
[opentenbase@VM_0_29_centos  ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# drop role user1 ;
DROP ROLE
```

说明：

- 如果该用户已经有表存在就无法删除，如果不准许该用户使用，可以使用nologin禁用用户登录。

## 用户与资源搜索路径管理 

opentenbase默认的资源搜索路径为

```
postgres=# show search_path ;
   search_path   
-----------------
 "$user", public
(1 row)
```

即访问的资源（如表，视图。。。）第一搜索的模式就是自己用户名相同的模式，第二个才是public模式

### 配置用户的默认搜索模式 

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
说明：  

-	配置用户user1的搜索路径为opentenbase,user1,public 
-	to DEFAULT配置用户user1的搜索模式为系统默认值 

### 给用户添加一个模式 

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# create schema user1 AUTHORIZATION user1;

```
说明：  

-	AUTHORIZATION user1指定模式user1的所属用户为users

# 权限管理 
## 模式权限管理 
### 授权用户可以访问某个模式 

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# grant usage on SCHEMA mysch to user1;
GRANT
postgres=#
``` 

说明：

-	默认情况下，普通用户是无法访问没授权的schema，所以要授权用户访问某个表的访问权限，则需要将表所在的schema使用权分配给用户先。
-	如果模式访问无控权，则提示 ERROR:  permission denied for schema mysch  

### 收回用户访问某个模式要权限 

```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# revoke usage on SCHEMA mysch from user1;
REVOKE
```

### 修改模式所属用户 
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# alter schema mysch owner to user1;
ALTER SCHEMA
```

## 表权限管理 
### 授权用户可以增删改查某个表记录 
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
说明：

-	增，删，改，查分别对应INSERT/DELETE/UPDATE/SELECT。
-	如果需要全部权限，则可以这样写成all

### 移除用户的访问权限 
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# revoke ALL on mysch.t2 from user1; 
REVOKE

postgres=# revoke select on mysch.t2 from user1;   
REVOKE
```

### 带序列的表序列也要授权 
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

-- 授权必需这样
postgres=# grant all on mysch.t3 to user1 ;
GRANT

postgres=# grant all on SEQUENCE mysch.t3_f1_seq to user1;             
GRANT

```

说明：

-	如果没有授权，会提示无序列访问权限permission denied for sequence t3_f1_seq。

### 将某个模式下所有表访问权限分配给某个用户 
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=#  grant ALL ON ALL TABLES IN SCHEMA  mysch  TO user1;
GRANT
```

### 取消某个模式下所有表访问权限 
```
[opentenbase@VM_0_29_centos ~]$ psql -h 172.16.0.29 -U opentenbase -d postgres -p 15432
psql (PostgreSQL 10.0 opentenbase V2)
Type "help" for help.

postgres=# revoke ALL ON ALL TABLES IN SCHEMA  mysch  FROM user1;       
REVOKE
```

# 结语 
OpenTenBase 是企业级分布式HTAP数据库管理系统。通过单一数据库集群同时为客户提供高一致性的分布式数据库服务和高性能的数据仓库服务，形成一套融合完整的企业级解决方案。大家在数据库领域遇到相关问题时，欢迎随时留言我们。