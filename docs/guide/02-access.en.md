# Application Access Guide

>In [Quick Start](01-quickstart.en.md) article, we introduced opentenbase architecture, source code compilation and installation, cluster running status, startup and stop, etc.
>
>This chapter will introduce how to connect to OpenTenBase for create database, table, data import, query and other operations.

OpenTenBase is compatible with all clients that support the Postgres protocol. Now we introduce the commonly used development languages including JAVA, C, shell, python, PHP, golang for connect to OpenTenBase.

## 1、JAVA
### 1.1、Create Table

```
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
 
 
public class createtable {
   public static void main( String args[] )
     {
       Connection c = null;
       Statement stmt = null;
       try {
         Class.forName("org.postgresql.Driver");
         c = DriverManager.getConnection("jdbc:postgresql://127.0.0.1:15432/postgres?currentSchema=public&binaryTransfer=false","opentenbase", "opentenbase");
         System.out.println("Opened database successfully");
         stmt = c.createStatement();
         String sql = "create table opentenbase(id int,nickname text) distribute by shard(id) to group  default_group" ;
         stmt.executeUpdate(sql);
         stmt.close();
         c.close();
       } catch ( Exception e ) {
         System.err.println( e.getClass().getName()+": "+ e.getMessage() );
         System.exit(0);
       }
       System.out.println("Table created successfully");
     }
}
```
Explain： 

* The node in here is an arbitrary CN master node. All subsequent operations, unless otherwise specified, are performed by connecting to the CN master node.



### 1.2、Insert data use general protocol
```
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
 
public class insert {
   public static void main(String args[]) {
      Connection c = null;
      Statement stmt = null;
      try {
         Class.forName("org.postgresql.Driver");
         c = DriverManager.getConnection("jdbc:postgresql://127.0.0.1:15432/postgres?currentSchema=public&binaryTransfer=false","opentenbase", "opentenbase");
         c.setAutoCommit(false);
         System.out.println("Opened database successfully");
 
         stmt = c.createStatement();
         String sql = "INSERT INTO opentenbase (id,nickname) "
               + "VALUES (1,'opentenbase');";
         stmt.executeUpdate(sql);
 
         sql = "INSERT INTO opentenbase (id,nickname) "
               + "VALUES (2, 'pgxz' ),(3,'pgxc');";
         stmt.executeUpdate(sql);
         stmt.close();
         c.commit();
         c.close();
      } catch (Exception e) {
         System.err.println( e.getClass().getName()+": "+ e.getMessage() );
         System.exit(0);
      }
      System.out.println("Records created successfully");
   }
}
```
### 1.3、Insert data use extended protocol
```
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.*;
import java.util.Random;
 
public class insert_prepared {
   public static void main(String args[]) {
      Connection c = null;
      PreparedStatement stmt;
      try {
         Class.forName("org.postgresql.Driver");
         c = DriverManager.getConnection("jdbc:postgresql://127.0.0.1:15432/postgres?currentSchema=public&binaryTransfer=false","opentenbase", "opentenbase");
         c.setAutoCommit(false);
         System.out.println("Opened database successfully");
         //Insert data
         String sql = "INSERT INTO opentenbase (id,nickname) VALUES (?,?)";         
         stmt = c.prepareStatement(sql);
         stmt.setInt(1, 9999);
         stmt.setString(2, "opentenbase_prepared");
         stmt.executeUpdate();
         
         //Insert update
         sql = "INSERT INTO opentenbase (id,nickname) VALUES (?,?) ON CONFLICT(id) DO UPDATE SET nickname=?";
         stmt = c.prepareStatement(sql);
         stmt.setInt(1, 9999);
         stmt.setString(2, "opentenbase_prepared");
         stmt.setString(3, "opentenbase_prepared_update");
         stmt.executeUpdate();
        
         stmt.close();
         c.commit();
         c.close();
      } catch (Exception e) {
         System.err.println( e.getClass().getName()+": "+ e.getMessage() );
         System.exit(0);
      }
      System.out.println("Records created successfully");
   }
}
```
### 1.4、Use `copy from` load file to table 
```
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
import org.postgresql.copy.CopyManager;  
import org.postgresql.core.BaseConnection;  
import java.io.*;
 
public class copyfrom {
   public static void main( String args[] )
     {
       Connection c = null;
       Statement stmt = null;
       FileInputStream fs = null;
       try {
         Class.forName("org.postgresql.Driver");
         c = DriverManager.getConnection("jdbc:postgresql://127.0.0.1:15432/postgres?currentSchema=public&binaryTransfer=false","opentenbase", "opentenbase");
         System.out.println("Opened database successfully");
         CopyManager cm = new CopyManager((BaseConnection) c);
         fs = new FileInputStream("/data/opentenbase/opentenbase.csv");
         String sql = "COPY opentenbase FROM STDIN DELIMITER AS ','";
         cm.copyIn(sql, fs);
         c.close();
         fs.close();
       } catch ( Exception e ) {
         System.err.println( e.getClass().getName()+": "+ e.getMessage() );
         System.exit(0);
       }
       System.out.println("Copy data successfully");
     }
}
```
### 1.5、Use `copy to` export data to file  
```
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
import org.postgresql.copy.CopyManager;  
import org.postgresql.core.BaseConnection;  
import java.io.*;
 
public class copyto {
   public static void main( String args[] )
     {
       Connection c = null;
       Statement stmt = null;
       FileOutputStream fs = null;
       try {
         Class.forName("org.postgresql.Driver");
         c = DriverManager.getConnection("jdbc:postgresql://127.0.0.1:15432/postgres?currentSchema=public&binaryTransfer=false","opentenbase", "opentenbase");
         System.out.println("Opened database successfully");
         CopyManager cm = new CopyManager((BaseConnection) c);
         fs = new FileOutputStream("/data/opentenbase/opentenbase.csv");
         String sql = "COPY opentenbase TO STDOUT DELIMITER AS ','";
         cm.copyOut(sql, fs);
         c.close();
         fs.close();
       } catch ( Exception e ) {
         System.err.println( e.getClass().getName()+": "+ e.getMessage() );
         System.exit(0);
       }
       System.out.println("Copy data successfully");
     }
}
```
### 1.6、Download address for jdbc file
```
https://jdbc.postgresql.org/download.html
```

## 2、C  
### 2.1、Connect to database
```
#include <stdio.h>  
#include <stdlib.h>  
#include "libpq-fe.h"     
int
main(int argc, char **argv){
    const char *conninfo;
    PGconn     *conn;      
    if (argc > 1){
        conninfo = argv[1];
    }else{
        conninfo = "dbname = postgres";  
    }            
    conn = PQconnectdb(conninfo);
    if (PQstatus(conn) != CONNECTION_OK){
        fprintf(stderr, "Failed to connect to the database: %s",PQerrorMessage(conn));              
    }else{
        printf("Connected to database successful！\n");
    }
    PQfinish(conn);
    return 0;
}
```  

Compile    

```
gcc -c -I /usr/local/install/opentenbase_pgxz/include/ conn.c  
gcc -o conn conn.o -L /usr/local/install/opentenbase_pgxz/lib/ -lpq  
```   

Run  
  
``` 
./conn "host=172.16.0.3 dbname=postgres port=11000"  
Connected to database successful！
```  
  
```
./conn "host=172.16.0.3 dbname=postgres port=15432 user=opentenbase"   
Connected to database successful！ 
```   
 
### 2.2、Create table
```
#include <stdio.h>
#include <stdlib.h>
#include "libpq-fe.h"   
int
main(int argc, char **argv){
    const char *conninfo;
    PGconn     *conn;      
    PGresult   *res;
    const char *sql = "create table opentenbase(id int,nickname text) distribute by shard(id) to group  default_group";
    if (argc > 1){
        conninfo = argv[1];
    }else{
        conninfo = "dbname = postgres";           
    }        
    conn = PQconnectdb(conninfo);
    if (PQstatus(conn) != CONNECTION_OK){
        fprintf(stderr, "Failed to connect to the database: %s",PQerrorMessage(conn));              
    }else{
        printf("Connected to database successful！\n");
    }
    res = PQexec(conn,sql);
    if(PQresultStatus(res) != PGRES_COMMAND_OK){
        fprintf(stderr, "Failed to create data table: %s",PQresultErrorMessage(res)); 
    }else{
        printf("Create data table successful！\n");
    }
    PQclear(res);
    PQfinish(conn);
    return 0;
}
``` 
Compile  

``` 
gcc -c -I /usr/local/install/opentenbase_pgxz/include/ createtable.c  
gcc -o createtable createtable.o -L /usr/local/install/opentenbase_pgxz/lib/ -lpq  
```   
Run  

```
./createtable "port=11000 dbname=postgres"
Connected to database successful！  
Create data table successful！ 
```  


### 2.3、Insert data
```
#include <stdio.h>
#include <stdlib.h>
#include "libpq-fe.h"   
int
main(int argc, char **argv){
    const char *conninfo;
    PGconn     *conn;      
    PGresult   *res;
    const char *sql = "INSERT INTO opentenbase (id,nickname) values(1,'opentenbase'),(2,'pgxz')";
    if (argc > 1){
        conninfo = argv[1];
    }else{
        conninfo = "dbname = postgres";           
    }        
    conn = PQconnectdb(conninfo);
    if (PQstatus(conn) != CONNECTION_OK){
        fprintf(stderr, "Failed to connect to the database: %s",PQerrorMessage(conn));              
    }else{
        printf("Create data table successful！\n");
    }
    res = PQexec(conn,sql);
    if(PQresultStatus(res) != PGRES_COMMAND_OK){
        fprintf(stderr, "Insert data failed: %s",PQresultErrorMessage(res)); 
    }else{
        printf("Insert data successful！\n");
    }
    PQclear(res);
    PQfinish(conn);
    return 0;
}
``` 
Compile  

``` 
gcc -c -I /usr/local/install/opentenbase_pgxz/include/ insert.c
gcc -o insert insert.o -L /usr/local/install/opentenbase_pgxz/lib/ -lpq
```   
Run  

```
./insert "dbname=postgres port=15432"
```  
  

### 2.4、Query data
```
#include <stdio.h>
#include <stdlib.h>
#include "libpq-fe.h"   
int
main(int argc, char **argv){
    const char *conninfo;
    PGconn     *conn;      
    PGresult   *res;
    const char *sql = "select * from opentenbase";
    if (argc > 1){
        conninfo = argv[1];
    }else{
        conninfo = "dbname = postgres";           
    }
    conn = PQconnectdb(conninfo);    
    if (PQstatus(conn) != CONNECTION_OK){
        fprintf(stderr, "Failed to connect to the database: %s",PQerrorMessage(conn));              
    }else{    
        printf("Connected to database successful！\n");
    }                                
    res = PQexec(conn,sql);
    if(PQresultStatus(res) != PGRES_TUPLES_OK){
        fprintf(stderr, "Insert data failed: %s",PQresultErrorMessage(res)); 
    }else{
        printf("Query data successful！\n");    
        int rownum = PQntuples(res) ;
        int colnum = PQnfields(res);
        for(int j = 0;j< colnum; ++j){
            printf("%s\t",PQfname(res,j));
        }
        printf("\n");
        for(int i = 0;i< rownum; ++i){
            for(int j = 0;j< colnum; ++j){
                printf("%s\t",PQgetvalue(res,i,j));
            }
            printf("\n");
        }
    }
    PQclear(res);
    PQfinish(conn);
    return 0;
}
```
 
Compile  

``` 
gcc -std=c99 -c -I /usr/local/install/opentenbase_pgxz/include/ select.c  
gcc -o select select.o -L /usr/local/install/opentenbase_pgxz/lib/ -lpq
```     
Run 
 
``` 
./select "dbname=postgres port=15432"
Connected to database successful！  
Query data successful！ 
id      nickname  
1       opentenbase  
2       pgxz  

```

### 2.5、Copy Stream data into table
```
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "libpq-fe.h"   
int 
main(int argc, char **argv){
    const char *conninfo;
    PGconn     *conn;      
    PGresult   *res;
    const char *buffer = "1,opentenbase\n2,pgxz\n3,opentenbase牛";
    if (argc > 1){
        conninfo = argv[1];
    }else{
        conninfo = "dbname = postgres";           
    }
    conn = PQconnectdb(conninfo);
    if (PQstatus(conn) != CONNECTION_OK){
        fprintf(stderr, "Failed to connect to the database: %s",PQerrorMessage(conn));              
    }else{
        printf("Connected to database successful！\n");
    }
    res=PQexec(conn,"COPY opentenbase FROM STDIN DELIMITER ',';");
    if(PQresultStatus(res) != PGRES_COPY_IN){
        fprintf(stderr, "Wrong from copy data 1: %s",PQresultErrorMessage(res));
    }else{
        int len = strlen(buffer);
        if(PQputCopyData(conn,buffer,len) == 1){
             if(PQputCopyEnd(conn,NULL) == 1){
                res = PQgetResult(conn);
                if(PQresultStatus(res) == PGRES_COMMAND_OK){
                    printf("Copy data successful！\n");         
                }else{
                    fprintf(stderr, "Wrong from copy data 2: %s",PQerrorMessage(conn));    
                }
             }else{
                fprintf(stderr, "Wrong from copy data 3: %s",PQerrorMessage(conn));   
             }
        }else{
            fprintf(stderr, "Wrong from copy data 4: %s",PQerrorMessage(conn));              
        }
    }
    PQclear(res);
    PQfinish(conn);
    return 0;
}
```
 
Compile  

``` 
gcc -c -I /usr/local/install/opentenbase_pgxz/include/ copy.c
gcc -o copy copy.o -L /usr/local/install/opentenbase_pgxz/lib/ -lpq
```
 
Run  

``` 
./copy "dbname=postgres port=15432"
Connected to database successful！ 
Copy data successful！
```  



### 3、Shell script
```
#!/bin/sh
 
if [ $# -ne 0 ]
then
    echo "usage: $0 exec_sql"
    exit 1
fi
 
exec_sql=$1
 
masters=`psql -h 172.16.0.29 -d postgres -p 15432 -t -c "select string_agg(node_host, ' ') from (select * from pgxc_node where node_type = 'D' order by node_name) t"`
port_list=`psql -h 172.16.0.29 -d postgres -p 15432 -t -c "select string_agg(node_port::text, ' ') from (select * from pgxc_node where node_type = 'D' order by node_name) t"`
node_cnt=`psql -h 172.16.0.29 -d postgres -p 15432 -t -c "select count(*) from pgxc_node where node_type = 'D'"`
masters=($masters)
ports=($port_list)
 
echo $node_cnt
 
flag=0
 
for((i=0;i<$node_cnt;i++));
do
    seq=$(($i+1))
    master=${masters[$i]}
    port=${ports[$i]}
    echo $master
    echo $port
 
    psql -h $master -p $port  postgres -c "$exec_sql"
done
```

## 4、Python
### 4.1、Install psycopg2
```
[root@VM_0_29_centos ~]# yum install python-psycopg2
```  

### 4.2、Connect database
```
#coding=utf-8
#!/usr/bin/python
import psycopg2
try:
    conn = psycopg2.connect(database="postgres", user="opentenbase", password="", host="172.16.0.29", port="15432")
    print "Connected to database successful！"
    conn.close()
except psycopg2.Error,msg:
    print "Failed to connect database, details： %s" %(msg.args[0])
```
 
Run  

``` 
[opentenbase@VM_0_29_centos python]$ python conn.py 
Connected to database successful！  
```


### 4.3、Create table
```
#coding=utf-8
#!/usr/bin/python
import psycopg2
try:
    conn = psycopg2.connect(database="postgres", user="opentenbase", password="", host="172.16.0.29", port="15432")
    print "Connected to database successful！"
    cur = conn.cursor()
    sql = """
          create table opentenbase 
          (
              id int,
              nickname varchar(100)
          )distribute by shard(id) to group default_group
          """
    cur.execute(sql)
    conn.commit()
    print "Create table successful!"    
    conn.close()
except psycopg2.Error,msg:
    print "OpenTenBase Error %s" %(msg.args[0])
``` 
Run  

``` 
[opentenbase@VM_0_29_centos python]$ python createtable.py   
Connected to database successful！ 
Create table successful!
```
### 4.4、Insert data
```
#coding=utf-8
#!/usr/bin/python
import psycopg2
try:
    conn = psycopg2.connect(database="postgres", user="opentenbase", password="", host="172.16.0.29", port="15432")
    print "Connected to database successful!"    
    cur = conn.cursor()
    sql = "insert into opentenbase values(1,'opentenbase'),(2,'opentenbase');"
    cur.execute(sql)
    sql = "insert into opentenbase values(%s,%s)"   
    cur.execute(sql,(3,'pg'))
    conn.commit()
    print "Insert data successful!"    
    conn.close()
except psycopg2.Error,msg:
    print "OpenTenBase Error %s" %(msg.args[0])
``` 
Run  

``` 
[opentenbase@VM_0_29_centos python]$ python insert.py   
Connected to database successful！  
Insert data successful! 
```

### 4.5、Query data
```
#coding=utf-8
#!/usr/bin/python
import psycopg2
try:
    conn = psycopg2.connect(database="postgres", user="opentenbase", password="", host="172.16.0.29", port="15432")
    print "Connected to database successful!"    
    cur = conn.cursor()
    sql = "select * from opentenbase"
    cur.execute(sql)
    rows = cur.fetchall()
    for row in rows:
        print "ID = ", row[0]
        print "NICKNAME = ", row[1],"\n"
    conn.close()
except psycopg2.Error,msg:
    print "OpenTenBase Error %s" %(msg.args[0])
```
 
Run  

``` 
[opentenbase@VM_0_29_centos python]$ python select.py   
Connected to database successful！
ID =  1
NICKNAME =  opentenbase 
 
ID =  2
NICKNAME =  pgxz 
 
ID =  3
NICKNAME =  pg
```  
 
### 4.6、Use `copy from` load file to table
```
#coding=utf-8
#!/usr/bin/python
import psycopg2
try:
    conn = psycopg2.connect(database="postgres", user="opentenbase", password="", host="172.16.0.29", port="15432")
    print "Connected to database successful！"    
    cur = conn.cursor()
    filename = "/data/opentenbase/opentenbase.txt"
    cols = ('id','nickname')
    tablename="public.opentenbase"
    cur.copy_from(file=open(filename),table=tablename,columns=cols,sep=',')
    conn.commit()
    print "Import data successful!"
    conn.close()
except psycopg2.Error,msg:
    print "OpenTenBase Error %s" %(msg.args[0])
```  
 
Run

``` 
[opentenbase@VM_0_29_centos python]$ python copy_from.py 
Connected to database successful！ 
Import data successful!
``` 

## 5、PHP
### 5.1、Connect database
```
<?php     
$host="172.16.0.29";
$port="15432";
$dbname="postgres";
$user="opentenbase" ;
$password="";  
 
//Connect database
$conn=@pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");      
if (!$conn){
    $error_msg=@pg_errormessage($conn); 
    echo "Failed to connect database，details：".$error_msg."\n<BR>"; ;
    exit;
}else{
    echo "Connected to database successful!"\n<BR>";      
} 
//Close connect
pg_close($conn);
?>
``` 
 
Run  

``` 
[root@VM_0_47_centos test]# curl http://127.0.0.1:8080/dbsta/test/conn.php
Connected to database successful!
```  

### 5.2、Create table
```
<?php     
$host="172.16.0.29";
$port="15432";
$dbname="postgres";
$user="opentenbase" ;
$password="";  
 
//Connect database
$conn=@pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");      
if (!$conn){
    $error_msg=@pg_errormessage($conn); 
    echo "Failed to connect database，details：".$error_msg."\n<BR>"; ;
    exit;
}else{
    echo "Connected to database successful!"\n<BR>";      
} 
 
//Create table
$sql="create table public.opentenbase(id integer,nickname varchar(100)) distribute by shard(id) to group default_group;";
$result = @pg_exec($conn,$sql) ;
if (!$result){
    $error_msg=@pg_errormessage($conn); 
    echo "Failed to create table，details：".$error_msg."\n"; ;
    exit;
}else{
    echo "Creat table successful!"\n";       
}
//Close connect
pg_close($conn);
?>
```  

run

``` 
[root@VM_0_47_centos test]# curl http://127.0.0.1:8080/dbsta/test/createtable.php
Connected to database successful!
Creat table successful!
```

### 5.3、Insert data
```
<?php     
$host="172.16.0.29";
$port="15432";
$dbname="postgres";
$user="opentenbase" ;
$password="";  
 
//Connect database
$conn=@pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");      
if (!$conn){
    $error_msg=@pg_errormessage($conn); 
    echo "Failed to connect database，details：".$error_msg."\n"; ;
    exit;
}else{
    echo "Connected to database successful!"\n";      
} 
 
//Insert data
$sql="insert into public.opentenbase values(1,'opentenbase'),(2,'pgxz');";    
$result = @pg_exec($conn,$sql) ;
if (!$result){
    $error_msg=@pg_errormessage($conn); 
    echo "Failed to insert data, details：".$error_msg."\n";
    exit;
}else{
    echo "Insert data successful!"\n";       
}
 
//Close connect
pg_close($conn);
 
?>
```  
 
Run

``` 
[opentenbase@VM_0_47_centos test]$ curl http://127.0.0.1:8080/dbsta/test/insert.php
Connected to database successful!
Insert data successful!
```

### 5.4、Query data
```
<?php     
$host="172.16.0.29";
$port="15432";
$dbname="postgres";
$user="opentenbase" ;
$password="";  
 
//Connect database
$conn=@pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");      
if (!$conn){
    $error_msg=@pg_errormessage($conn); 
    echo "Failed to connect database，details: ".$error_msg."\n"; ;
    exit;
}else{
    echo "Connected to database successful!"\n";      
} 
 
//Query data
$sql="select id,nickname from public.opentenbase";    
$result = @pg_exec($conn,$sql) ;
if (!$result){
    $error_msg=@pg_errormessage($conn); 
    echo "Failed to query data, details ：".$error_msg."\n";
    exit;
}else{
    echo "Query data successful!"\n";      
}
$record_num = pg_numrows($result);  
echo "Return query number: ".$record_num."\n"; 
$rec=pg_fetch_all($result); 
for($i=0;$i<$record_num;$i++){
    echo "numbers: #".strval($i+1)."\n";
    echo "id：".$rec[$i]["id"]."\n";
    echo "nickname：".$rec[$i]["nickname"]."\n\n";
}
//CLose connect 
pg_close($conn);
?>
``` 
Use method  

``` 
[root@VM_0_47_centos ~]# curl http://127.0.0.1:8080/dbsta/test/select.php
Connected to database successful!
Query data successful!
Return query number: 2
numbers: 1
id：1
nickname：opentenbase
 
numbers: 2
id：2
nickname：pgxz
```  

### 5.5、Copy Stream data into table
```
<?php 
 
$host="172.16.0.29";
$port="15432";
$dbname="postgres";
$user="opentenbase" ;
$password="";  
 
//Connect database
$conn=@pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");      
if (!$conn){
    $error_msg=@pg_errormessage($conn); 
    echo "Failed to connect database，details: ".$error_msg."\n"; ;
    exit;
}else{
    echo "Connected to database successful!"\n";      
}                                     
$row=ARRAY("1,opentenbase","2,pgxz");   
$flag=pg_copy_from($conn,"public.opentenbase",$row,",");
 
if (!$flag){
    $error_msg=@pg_errormessage($conn); 
    echo "copy wrong，details：".$error_msg."\n";
}else{
    echo "copy successful!"\n";          
}
 
//Close connect
pg_close($conn);
        
?>
```  
 
Use method

``` 
curl http://127.0.0.1/dbsta/cron/php_copy_from.php
Connected to database successful!
copy successful!
```  

### 5.6、Export data to List
```
<?php 
 
$host="172.16.0.29";
$port="15432";
$dbname="postgres";
$user="opentenbase" ;
$password="";  
 
//Connect database
$conn=@pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");      
if (!$conn){
    $error_msg=@pg_errormessage($conn); 
    echo "Failed to connect database，details: ".$error_msg."\n"; ;
    exit;
}else{
    echo "Connected to database successful!"\n";      
}                                    
 
$row=pg_copy_to($conn,"public.opentenbase",",");  
if (!$row){
    $error_msg=@pg_errormessage($conn); 
    echo "copy wrong，details：".$error_msg."\n";
}else{
    print_r($row);
}  
//Close connect 
pg_close($conn);              
?>
``` 
 
Use method 

```
curl http://127.0.0.1/dbsta/cron/php_copy_to.php  
Connected to database successful!
Array
(
    [0] => 1,opentenbase
 
    [1] => 2,pgxz
 
)
```  

## 6、golang 
### 6.1、Connect database
```
package main
 
import (
    "fmt"
    "time"
 
    "github.com/jackc/pgx"
)
 
func main() {
    var error_msg string
 
    //Connect database
    conn, err := db_connect()
    if err != nil {
        error_msg = "Failed to connect database, details：" + err.Error()
        write_log("Error", error_msg)
        return
    }
    //Close connect
    defer conn.Close()
    write_log("Log", "Connected to database successful！")
 
}
 
/*
Function：write to log
 
Parameter：
log_level -- level of log，only `Error` or `Log`
error_msg -- content of log
 
Return：none
*/
 
func write_log(log_level string, error_msg string) {
    //print error message
    fmt.Println("Time：", time.Now().Format("2006-01-02 15:04:05"))
    fmt.Println("Log level：", log_level)
    fmt.Println("Details：", error_msg)
}
 
/*
Function：Connect database
 
Parameter：none
 
Return：
conn *pgx.Conn -- connection information
err error -- error message
 
*/
 
func db_connect() (conn *pgx.Conn, err error) {
    var config pgx.ConnConfig
    config.Host = "127.0.0.1"    //localhost or ip
    config.User = "opentenbase"         //username
    config.Password = "pgsql"    //passoword
    config.Database = "postgres" //database name
    config.Port = 15432          //port
    conn, err = pgx.Connect(config)
    return conn, err
}
```
  
```  
[root@VM_0_29_centos opentenbase]# go run conn.go 
Time： 2018-04-03 20:40:28
Log level： Log
Details： Connected to database successful！
```  
 
Compile And Run  

```
[root@VM_0_29_centos opentenbase]# go build conn.go 
[root@VM_0_29_centos opentenbase]# ./conn 
Time： 2018-04-03 20:40:48
Log level： Log
Details： Connected to database successful！
```  

### 6.2、Create table  
```
package main
 
import (
    "fmt"
    "time"
 
    "github.com/jackc/pgx"
)
 
func main() {
    var error_msg string
    var sql string
 
    //Connect database
    conn, err := db_connect()
    if err != nil {
        error_msg = "Failed to connect database，details: " + err.Error()
        write_log("Error", error_msg)
        return
    }
    //Close connection
    defer conn.Close()
    write_log("Log", "Connected to database successful!")
 
    //Create table
    sql = "create table public.opentenbase(id varchar(20),nickname varchar(100)) distribute by shard(id) to group  default_group;"
    _, err = conn.Exec(sql)
    if err != nil {
        error_msg = "Failed to create table: " + err.Error()
        write_log("Error", error_msg)
        return
    } else {
        write_log("Log", "Create table successful!")
    }
}
 
/*
Function：Write log process
 
Parameter：
log_level -- level of log，only `Error` or `Log`
error_msg -- content of log
 
Return：none
*/
 
func write_log(log_level string, error_msg string) {
    //print error message
    fmt.Println("Time：", time.Now().Format("2006-01-02 15:04:05"))
    fmt.Println("Log level：", log_level)
    fmt.Println("Details：", error_msg)
}
 
/*
Function：Connect database
 
Parameter：none
 
Return：
conn *pgx.Conn -- connection information
err error -- error message
 
*/
 
func db_connect() (conn *pgx.Conn, err error) {
    var config pgx.ConnConfig
    config.Host = "127.0.0.1"    //localhost or ip
    config.User = "opentenbase"         //username
    config.Password = "pgsql"    //passoword
    config.Database = "postgres" //database name
    config.Port = 15432          //port
    conn, err = pgx.Connect(config)
    return conn, err
}
```  

``` 
[root@VM_0_29_centos opentenbase]# go run createtable.go 
Time： 2018-04-03 20:50:24
Log level： Log
Details： Connected to database successful！
Time： 2018-04-03 20:50:24
Log level： Log
Details： Create table successful!
```  

### 6.3、Insert data
```
package main
 
import (
    "fmt"
    "strings"
    "time"
 
    "github.com/jackc/pgx"
)
 
func main() {
    var error_msg string
    var sql string
    var nickname string
 
    //Connect database
    conn, err := db_connect()
    if err != nil {
        error_msg = "Failed to connect database，details: " + err.Error()
        write_log("Error", error_msg)
        return
    }
    //Close connection
    defer conn.Close()
    write_log("Log", "Connected to database successful!")
 
    //Insert data
    sql = "insert into public.opentenbase values('1','opentenbase'),('2','pgxz');"
    _, err = conn.Exec(sql)
    if err != nil {
        error_msg = "Failed to insert data, details: " + err.Error()
        write_log("Error", error_msg)
        return
    } else {
        write_log("Log", "Insert data successful!")
    }
 
    //Bind variables to insert data, no need to do anti-injection processing
    sql = "insert into public.opentenbase values($1,$2),($1,$3);"
    _, err = conn.Exec(sql, "3", "postgresql", "postgres")
    if err != nil {
        error_msg = "Failed to insert data, details: " + err.Error()
        write_log("Error", error_msg)
        return
    } else {
        write_log("Log", "Insert data successful!")
    }
 
    //Splice sql statement to insert data, need to do anti-injection processing
    nickname = "OpenTenBase is ' good!"
    sql = "insert into public.opentenbase values('1','" + sql_data_encode(nickname) + "')"
    _, err = conn.Exec(sql)
    if err != nil {
        error_msg = "Failed to insert data, details: " + err.Error()
        write_log("Error", error_msg)
        return
    } else {
        write_log("Log", "Insert data successful!")
    }
}
 
/*
Function：SQL query concatenation string encoding
 
Parameter：
str -- The string to be encode
 
Return：
Return encoded string
 
*/
 
func sql_data_encode(str string) string {
    return strings.Replace(str, "'", "''", -1)
}
 
/*
Function：Write log process
 
Parameter：
log_level -- level of log，only `Error` or `Log`
error_msg -- content of log
 
Return：none
*/
 
func write_log(log_level string, error_msg string) {
    //print error message
    fmt.Println("Time：", time.Now().Format("2006-01-02 15:04:05"))
    fmt.Println("Log level：", log_level)
    fmt.Println("Details：", error_msg)
}
 
/*
Function：Connect database
 
Parameter：none
 
Return：
conn *pgx.Conn -- connection information
err error -- error message
 
*/
 
func db_connect() (conn *pgx.Conn, err error) {
    var config pgx.ConnConfig
    config.Host = "127.0.0.1"    //localhost or ip
    config.User = "opentenbase"         //username
    config.Password = "pgsql"    //passoword
    config.Database = "postgres" //database name
    config.Port = 15432          //port
    conn, err = pgx.Connect(config)
    return conn, err
}
```  

``` 
[root@VM_0_29_centos opentenbase]# go run insert.go 
Time： 2018-04-03 21:05:51
Log level： Log
Details： Connected to database successful！
Time： 2018-04-03 21:05:51
Log level： Log
Details： Insert data successful!
Time： 2018-04-03 21:05:51
Log level： Log
Details： Insert data successful!
Time： 2018-04-03 21:05:51
Log level： Log
Details： Insert data successful!
```  

### 6.4、Query data
```
package main
 
import (
    "fmt"
    "strings"
    "time"
 
    "github.com/jackc/pgx"
)
 
func main() {
    var error_msg string
    var sql string
 
    //Connect database
    conn, err := db_connect()
    if err != nil {
        error_msg = "Failed to connect database，details: " + err.Error()
        write_log("Error", error_msg)
        return
    }
    //Close connection
    defer conn.Close()
    write_log("Log", "Connected to database successful!")
 
    sql = "SELECT id,nickname FROM public.opentenbase LIMIT 2"
    rows, err := conn.Query(sql)
    if err != nil {
        error_msg = "Failed to query data, details: " + err.Error()
        write_log("Error", error_msg)
        return
    } else {
        write_log("Log", "Query data successful!")
    }
 
    var nickname string
    var id string
 
    for rows.Next() {
        err = rows.Scan(&id, &nickname)
        if err != nil {
            error_msg = "Failed to query data, details: " + err.Error()
            write_log("Error", error_msg)
            return
        }
        error_msg = fmt.Sprintf("id：%s nickname：%s", id, nickname)
        write_log("Log", error_msg)
    }
    rows.Close()
 
    nickname = "opentenbase"
 
    sql = "SELECT id,nickname FROM public.opentenbase WHERE nickname ='" + sql_data_encode(nickname) + "' "
    rows, err = conn.Query(sql)
    if err != nil {
        error_msg = "Failed to query data, details: " + err.Error()
        write_log("Error", error_msg)
        return
    } else {
        write_log("Log", "Query data successful!")
    }
    defer rows.Close()
 
    for rows.Next() {
        err = rows.Scan(&id, &nickname)
        if err != nil {
            error_msg = "Failed to query data, details: " + err.Error()
            write_log("Error", error_msg)
            return
        }
        error_msg = fmt.Sprintf("id：%s nickname：%s", id, nickname)
        write_log("Log", error_msg)
    }
}
 
/*
Function：SQL query concatenation string encoding
 
Parameter：
str -- The string to be encode
 
Return：
Return encoded string
 
*/
 
func sql_data_encode(str string) string {
    return strings.Replace(str, "'", "''", -1)
}
 
/*
Function：Write log process
 
Parameter：
log_level -- level of log，only `Error` or `Log`
error_msg -- content of log
 
Return：none
*/
 
func write_log(log_level string, error_msg string) {
    //print error message
    fmt.Println("Time：", time.Now().Format("2006-01-02 15:04:05"))
    fmt.Println("Log level：", log_level)
    fmt.Println("Details：", error_msg)
}
 
/*
Function：Connect database
 
Parameter：none
 
Return：
conn *pgx.Conn -- connection information
err error -- error message
 
*/
 
func db_connect() (conn *pgx.Conn, err error) {
    var config pgx.ConnConfig
    config.Host = "127.0.0.1"    //localhost or ip
    config.User = "opentenbase"         //username
    config.Password = "pgsql"    //passoword
    config.Database = "postgres" //database name
    config.Port = 15432          //port
    conn, err = pgx.Connect(config)
    return conn, err
}
```  
``` 
[root@VM_0_29_centos opentenbase]# go run select.go
Time： 2018-04-09 10:35:50
Log level： Log
Details： Connected to database successful！
Time： 2018-04-09 10:35:50
Log level： Log
Details： Query data successful!
Time： 2018-04-09 10:35:50
Log level： Log
Details： id：2 nickname：opentenbase
Time： 2018-04-09 10:35:50
Log level： Log
Details： id：3 nickname：postgresql
Time： 2018-04-09 10:35:50
Log level： Log
Details： Query data successful!
Time： 2018-04-09 10:35:50
Log level： Log
Details： id：1 nickname：opentenbase
```  

### 6.5、Copy Stream data into table
```
package main
 
import (
    "fmt"
    "math/rand"
    "time"
 
    "github.com/jackc/pgx"
)
 
func main() {
    var error_msg string
 
    //Connect database
    conn, err := db_connect()
    if err != nil {
        error_msg = "Failed to connect database，details: " + err.Error()
        write_log("Error", error_msg)
        return
    }
    //Close connection
    defer conn.Close()
    write_log("Log", "Connected to database successful!")
 
    //create 5000 data
    inputRows := [][]interface{}{}
    var id string
    var nickname string
    for i := 0; i < 5000; i++ {
        id = fmt.Sprintf("%d", rand.Intn(10000))
        nickname = fmt.Sprintf("%d", rand.Intn(10000))
        inputRows = append(inputRows, []interface{}{id, nickname})
    }
    copyCount, err := conn.CopyFrom(pgx.Identifier{"opentenbase"}, []string{"id", "nickname"}, pgx.CopyFromRows(inputRows))
    if err != nil {
        error_msg = "Failed to use copyfrom, details: " + err.Error()
        write_log("Error", error_msg)
        return
    }
    if copyCount != len(inputRows) {
        error_msg = fmt.Sprintf("Failed to use copyfrom，copy lines：%d Return lines：%d", len(inputRows), copyCount)
        write_log("Error", error_msg)
        return
    } else {
        error_msg = "Copy successful!"
        write_log("Log", error_msg)
    }
 
}
 
/*
Function：Write log process
 
Parameter：
log_level -- level of log，only `Error` or `Log`
error_msg -- content of log
 
Return：none
*/
 
func write_log(log_level string, error_msg string) {
    //print error message
    fmt.Println("Time：", time.Now().Format("2006-01-02 15:04:05"))
    fmt.Println("Log level：", log_level)
    fmt.Println("Details：", error_msg)
}
 
/*
Function：Connect database
 
Parameter：none
 
Return：
conn *pgx.Conn -- connection information
err error -- error message
 
*/
 
func db_connect() (conn *pgx.Conn, err error) {
    var config pgx.ConnConfig
    config.Host = "127.0.0.1"    //localhost or ip
    config.User = "opentenbase"         //username
    config.Password = "pgsql"    //passoword
    config.Database = "postgres" //database name
    config.Port = 15432          //port
    conn, err = pgx.Connect(config)
    return conn, err
}
``` 
``` 
[root@VM_0_29_centos opentenbase]# go run copy_from.go 
Time： 2018-04-09 10:36:40
Log level： Log
Details： Connected to database successful！
Time： 2018-04-09 10:36:40
Log level： Log
Details： Copy successful!
```

### 6.6、Packages for golang
Needs to clone from git:  
https://github.com/jackc/pgx  
https://github.com/pkg/errors  
