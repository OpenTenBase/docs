# 应用接入指南

>在[快速入门](01-quickstart.md)文章中我们介绍了 OpenTenBase 的架构、源码编译安装、集群运行状态、启动停止等内容。
>
>本篇将介绍应用程序如何连接OpenTenBase数据库进行建库、建表、数据导入、查询等操作。

OpenTenBase兼容所有支持Postgres协议的客户端连接，这里将详细介绍JAVA、C语音、shell语言、Python、PHP、Golang 这6种最常用的开发语言连接OpenTenBase的操作方法。

## 1、JAVA开发  
### 1.1、创建数据表  

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

说明：

* 这里连接的节点为任意CN主节点，后面所有操作，没特别说明，都是连接到CN主节点进行操作。



### 1.2、使用普通协议插入数据  
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
### 1.3、使用扩展协议插入数据  
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
         //插入数据
         String sql = "INSERT INTO opentenbase (id,nickname) VALUES (?,?)";         
         stmt = c.prepareStatement(sql);
         stmt.setInt(1, 9999);
         stmt.setString(2, "opentenbase_prepared");
         stmt.executeUpdate();
         
         //插入更新
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
### 1.4、copy from 加载文件到表  
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
### 1.5、copy to 导出数据到文件  
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
### 1.6、jdbc包下载地址  
```
https://jdbc.postgresql.org/download.html
```

## 2、C程序开发  
### 2.1、连接数据库  
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
        fprintf(stderr, "连接数据库失败: %s",PQerrorMessage(conn));              
    }else{
        printf("连接数据库成功！\n");
    }
    PQfinish(conn);
    return 0;
}
```  

编译    

```
gcc -c -I /usr/local/install/opentenbase_pgxz/include/ conn.c  
gcc -o conn conn.o -L /usr/local/install/opentenbase_pgxz/lib/ -lpq  
```   

运行  
  
``` 
./conn "host=172.16.0.3 dbname=postgres port=11000"  
连接数据库成功！
```  
  
```
./conn "host=172.16.0.3 dbname=postgres port=15432 user=opentenbase"   
连接数据库成功！ 
```   
 
### 2.2、建立数据表
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
        fprintf(stderr, "连接数据库失败: %s",PQerrorMessage(conn));              
    }else{
        printf("连接数据库成功！\n");
    }
    res = PQexec(conn,sql);
    if(PQresultStatus(res) != PGRES_COMMAND_OK){
        fprintf(stderr, "建立数据表失败: %s",PQresultErrorMessage(res)); 
    }else{
        printf("建立数据表成功！\n");
    }
    PQclear(res);
    PQfinish(conn);
    return 0;
}
``` 
编译  

``` 
gcc -c -I /usr/local/install/opentenbase_pgxz/include/ createtable.c  
gcc -o createtable createtable.o -L /usr/local/install/opentenbase_pgxz/lib/ -lpq  
```   
运行  

```
./createtable "port=11000 dbname=postgres"
连接数据库成功！  
建立数据表成功！ 
```  


### 2.3、插入数据
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
        fprintf(stderr, "连接数据库失败: %s",PQerrorMessage(conn));              
    }else{
        printf("连接数据库成功！\n");
    }
    res = PQexec(conn,sql);
    if(PQresultStatus(res) != PGRES_COMMAND_OK){
        fprintf(stderr, "插入数据失败: %s",PQresultErrorMessage(res)); 
    }else{
        printf("插入数据成功！\n");
    }
    PQclear(res);
    PQfinish(conn);
    return 0;
}
``` 
编译  

``` 
gcc -c -I /usr/local/install/opentenbase_pgxz/include/ insert.c
gcc -o insert insert.o -L /usr/local/install/opentenbase_pgxz/lib/ -lpq
```   
运行  

```
./insert "dbname=postgres port=15432"
```  
  

### 2.4、查询数据
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
        fprintf(stderr, "连接数据库失败: %s",PQerrorMessage(conn));              
    }else{    
        printf("连接数据库成功！\n");
    }                                
    res = PQexec(conn,sql);
    if(PQresultStatus(res) != PGRES_TUPLES_OK){
        fprintf(stderr, "插入数据失败: %s",PQresultErrorMessage(res)); 
    }else{
        printf("查询数据成功！\n");    
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
 
编译  

``` 
gcc -std=c99 -c -I /usr/local/install/opentenbase_pgxz/include/ select.c  
gcc -o select select.o -L /usr/local/install/opentenbase_pgxz/lib/ -lpq
```     
运行 
 
``` 
./select "dbname=postgres port=15432"
连接数据库成功！  
查询数据成功！    
id      nickname  
1       opentenbase  
2       pgxz  

```

### 2.5、流数据COPY入表
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
        fprintf(stderr, "连接数据库失败: %s",PQerrorMessage(conn));              
    }else{
        printf("连接数据库成功！\n");
    }
    res=PQexec(conn,"COPY opentenbase FROM STDIN DELIMITER ',';");
    if(PQresultStatus(res) != PGRES_COPY_IN){
        fprintf(stderr, "copy数据出错1: %s",PQresultErrorMessage(res));
    }else{
        int len = strlen(buffer);
        if(PQputCopyData(conn,buffer,len) == 1){
             if(PQputCopyEnd(conn,NULL) == 1){
                res = PQgetResult(conn);
                if(PQresultStatus(res) == PGRES_COMMAND_OK){
                    printf("copy数据成功！\n");         
                }else{
                    fprintf(stderr, "copy数据出错2: %s",PQerrorMessage(conn));    
                }
             }else{
                fprintf(stderr, "copy数据出错3: %s",PQerrorMessage(conn));   
             }
        }else{
            fprintf(stderr, "copy数据出错4: %s",PQerrorMessage(conn));              
        }
    }
    PQclear(res);
    PQfinish(conn);
    return 0;
}
```
 
编译  

``` 
gcc -c -I /usr/local/install/opentenbase_pgxz/include/ copy.c
gcc -o copy copy.o -L /usr/local/install/opentenbase_pgxz/lib/ -lpq
```
 
执行  

``` 
./copy "dbname=postgres port=15432"
连接数据库成功！  
copy数据成功！
```  



### 3、shell脚本开发
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

## 4、python程序开发  
### 4.1、安装psycopg2模块
```
[root@VM_0_29_centos ~]# yum install python-psycopg2
```  

### 4.2、连接数据库
```
#coding=utf-8
#!/usr/bin/python
import psycopg2
try:
    conn = psycopg2.connect(database="postgres", user="opentenbase", password="", host="172.16.0.29", port="15432")
    print "连接数据库成功"
    conn.close()
except psycopg2.Error,msg:
    print "连接数据库出错，错误详细信息： %s" %(msg.args[0])
```
 
运行  

``` 
[opentenbase@VM_0_29_centos python]$ python conn.py 
连接数据库成功   
```


### 4.3、创建数据表
```
#coding=utf-8
#!/usr/bin/python
import psycopg2
try:
    conn = psycopg2.connect(database="postgres", user="opentenbase", password="", host="172.16.0.29", port="15432")
    print "连接数据库成功"    
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
    print "建立数据表成功"    
    conn.close()
except psycopg2.Error,msg:
    print "OpenTenBase Error %s" %(msg.args[0])
``` 
运行  

``` 
[opentenbase@VM_0_29_centos python]$ python createtable.py   
连接数据库成功
建立数据表成功
```
### 4.4、插入数据
```
#coding=utf-8
#!/usr/bin/python
import psycopg2
try:
    conn = psycopg2.connect(database="postgres", user="opentenbase", password="", host="172.16.0.29", port="15432")
    print "连接数据库成功"    
    cur = conn.cursor()
    sql = "insert into opentenbase values(1,'opentenbase'),(2,'opentenbase');"
    cur.execute(sql)
    sql = "insert into opentenbase values(%s,%s)"   
    cur.execute(sql,(3,'pg'))
    conn.commit()
    print "插入数据成功"    
    conn.close()
except psycopg2.Error,msg:
    print "操作数据库出库 %s" %(msg.args[0])
``` 
运行  

``` 
[opentenbase@VM_0_29_centos python]$ python insert.py   
连接数据库成功  
插入数据成功  
```

### 4.5、查询数据
```
#coding=utf-8
#!/usr/bin/python
import psycopg2
try:
    conn = psycopg2.connect(database="postgres", user="opentenbase", password="", host="172.16.0.29", port="15432")
    print "连接数据库成功"    
    cur = conn.cursor()
    sql = "select * from opentenbase"
    cur.execute(sql)
    rows = cur.fetchall()
    for row in rows:
        print "ID = ", row[0]
        print "NICKNAME = ", row[1],"\n"
    conn.close()
except psycopg2.Error,msg:
    print "操作数据库出库 %s" %(msg.args[0])
```
 
运行  

``` 
[opentenbase@VM_0_29_centos python]$ python select.py   
连接数据库成功
ID =  1
NICKNAME =  opentenbase 
 
ID =  2
NICKNAME =  pgxz 
 
ID =  3
NICKNAME =  pg
```  
 
### 4.6、copy from 加载文件到表
```
#coding=utf-8
#!/usr/bin/python
import psycopg2
try:
    conn = psycopg2.connect(database="postgres", user="opentenbase", password="", host="172.16.0.29", port="15432")
    print "连接数据库成功"    
    cur = conn.cursor()
    filename = "/data/opentenbase/opentenbase.txt"
    cols = ('id','nickname')
    tablename="public.opentenbase"
    cur.copy_from(file=open(filename),table=tablename,columns=cols,sep=',')
    conn.commit()
    print "导入数据成功"
    conn.close()
except psycopg2.Error,msg:
    print "操作数据库出库 %s" %(msg.args[0])
```  
 
执行

``` 
[opentenbase@VM_0_29_centos python]$ python copy_from.py 
连接数据库成功
导入数据成功
``` 

## 5、PHP程序开发
### 5.1、连接数据库
```
<?php     
$host="172.16.0.29";
$port="15432";
$dbname="postgres";
$user="opentenbase" ;
$password="";  
 
//连接数据库
$conn=@pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");      
if (!$conn){
    $error_msg=@pg_errormessage($conn); 
    echo "连接数据库出错，详情：".$error_msg."\n<BR>"; ;
    exit;
}else{
    echo "连接数据库成功"."\n<BR>";      
} 
//关闭连接
pg_close($conn);
?>
``` 
 
执行  

``` 
[root@VM_0_47_centos test]# curl http://127.0.0.1:8080/dbsta/test/conn.php
连接数据库成功
```  

### 5.2、创建数据表
```
<?php     
$host="172.16.0.29";
$port="15432";
$dbname="postgres";
$user="opentenbase" ;
$password="";  
 
//连接数据库
$conn=@pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");      
if (!$conn){
    $error_msg=@pg_errormessage($conn); 
    echo "连接数据库出错，详情：".$error_msg."\n"; ;
    exit;
}else{
    echo "连接数据库成功"."\n";      
} 
 
//建立数据表
$sql="create table public.opentenbase(id integer,nickname varchar(100)) distribute by shard(id) to group default_group;";
$result = @pg_exec($conn,$sql) ;
if (!$result){
    $error_msg=@pg_errormessage($conn); 
    echo "创建数据表出错，详情：".$error_msg."\n"; ;
    exit;
}else{
    echo "创建数据表成功"."\n";       
}
//关闭连接
pg_close($conn);
?>
```  

执行

``` 
[root@VM_0_47_centos test]# curl http://127.0.0.1:8080/dbsta/test/createtable.php
连接数据库成功
创建数据表成功
```

### 5.3、插入数据
```
<?php     
$host="172.16.0.29";
$port="15432";
$dbname="postgres";
$user="opentenbase" ;
$password="";  
 
//连接数据库
$conn=@pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");      
if (!$conn){
    $error_msg=@pg_errormessage($conn); 
    echo "连接数据库出错，详情：".$error_msg."\n"; ;
    exit;
}else{
    echo "连接数据库成功"."\n";      
} 
 
//插入数据
$sql="insert into public.opentenbase values(1,'opentenbase'),(2,'pgxz');";    
$result = @pg_exec($conn,$sql) ;
if (!$result){
    $error_msg=@pg_errormessage($conn); 
    echo "插入数据出错，详情：".$error_msg."\n";
    exit;
}else{
    echo "插入数据成功"."\n";       
}
 
//关闭连接
pg_close($conn);
 
?>
```  
 
执行

``` 
[opentenbase@VM_0_47_centos test]$ curl http://127.0.0.1:8080/dbsta/test/insert.php
连接数据库成功
插入数据成功
```

### 5.4、查询数据
```
<?php     
$host="172.16.0.29";
$port="15432";
$dbname="postgres";
$user="opentenbase" ;
$password="";  
 
//连接数据库
$conn=@pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");      
if (!$conn){
    $error_msg=@pg_errormessage($conn); 
    echo "连接数据库出错，详情：".$error_msg."\n"; ;
    exit;
}else{
    echo "连接数据库成功"."\n";      
} 
 
//查询数据 
$sql="select id,nickname from public.opentenbase";    
$result = @pg_exec($conn,$sql) ;
if (!$result){
    $error_msg=@pg_errormessage($conn); 
    echo "查询数据出错，详情：".$error_msg."\n";
    exit;
}else{
    echo "插入数据成功"."\n";      
}
$record_num = pg_numrows($result);  
echo "返回记录数".$record_num."\n"; 
$rec=pg_fetch_all($result); 
for($i=0;$i<$record_num;$i++){
    echo "记录数#".strval($i+1)."\n";
    echo "id：".$rec[$i]["id"]."\n";
    echo "nickname：".$rec[$i]["nickname"]."\n\n";
}
//关闭连接
pg_close($conn);
?>
``` 
调用方法  

``` 
[root@VM_0_47_centos ~]# curl http://127.0.0.1:8080/dbsta/test/select.php
连接数据库成功
插入数据成功
返回记录数2
记录数#1
id：1
nickname：opentenbase
 
记录数#2
id：2
nickname：pgxz
```  

### 5.5、流数据copy 入表
```
<?php 
 
$host="172.16.0.29";
$port="15432";
$dbname="postgres";
$user="opentenbase" ;
$password="";  
 
//连接数据库
$conn=@pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");      
if (!$conn){
    $error_msg=@pg_errormessage($conn); 
    echo "连接数据库出错，详情：".$error_msg."\n"; ;
    exit;
}else{
    echo "连接数据库成功"."\n";      
}                                     
$row=ARRAY("1,opentenbase","2,pgxz");   
$flag=pg_copy_from($conn,"public.opentenbase",$row,",");
 
if (!$flag){
    $error_msg=@pg_errormessage($conn); 
    echo "copy出错，详情：".$error_msg."\n";
}else{
    echo "copy成功"."\n";          
}
 
//关闭连接
pg_close($conn);
        
?>
```  
 
调用方法

``` 
curl http://127.0.0.1/dbsta/cron/php_copy_from.php
连接数据库成功
copy成功
```  

### 5.6、copy to导出数据到一个数组中
```
<?php 
 
$host="172.16.0.29";
$port="15432";
$dbname="postgres";
$user="opentenbase" ;
$password="";  
 
//连接数据库
$conn=@pg_connect("host=$host port=$port dbname=$dbname user=$user password=$password");      
if (!$conn){
    $error_msg=@pg_errormessage($conn); 
    echo "连接数据库出错，详情：".$error_msg."\n"; ;
    exit;
}else{
    echo "连接数据库成功"."\n";      
}                                     
 
$row=pg_copy_to($conn,"public.opentenbase",",");  
if (!$row){
    $error_msg=@pg_errormessage($conn); 
    echo "copy出错，详情：".$error_msg."\n";
}else{
    print_r($row);
}  
//关闭连接 
pg_close($conn);              
?>
``` 
 
调用方法  

```
curl http://127.0.0.1/dbsta/cron/php_copy_to.php  
连接数据库成功
Array
(
    [0] => 1,opentenbase
 
    [1] => 2,pgxz
 
)
```  

## 6、golang程序开发  
### 6.1、连接数据库  
```
package main
 
import (
    "fmt"
    "time"
 
    "github.com/jackc/pgx"
)
 
func main() {
    var error_msg string
 
    //连接数据库
    conn, err := db_connect()
    if err != nil {
        error_msg = "连接数据库失败，详情：" + err.Error()
        write_log("Error", error_msg)
        return
    }
    //程序运行结束时关闭连接
    defer conn.Close()
    write_log("Log", "连接数据库成功")
 
}
 
/*
功能描述：写入日志处理
 
参数说明：
log_level -- 日志级别，只能是是Error或Log
error_msg -- 日志内容
 
返回值说明：无
*/
 
func write_log(log_level string, error_msg string) {
    //打印错误信息
    fmt.Println("访问时间：", time.Now().Format("2006-01-02 15:04:05"))
    fmt.Println("日志级别：", log_level)
    fmt.Println("详细信息：", error_msg)
}
 
/*
功能描述：连接数据库
 
参数说明：无
 
返回值说明：
conn *pgx.Conn -- 连接信息
err error --错误信息
 
*/
 
func db_connect() (conn *pgx.Conn, err error) {
    var config pgx.ConnConfig
    config.Host = "127.0.0.1"    //数据库主机host或ip
    config.User = "opentenbase"         //连接用户
    config.Password = "pgsql"    //用户密码
    config.Database = "postgres" //连接数据库名
    config.Port = 15432          //端口号
    conn, err = pgx.Connect(config)
    return conn, err
}
```
  
```  
[root@VM_0_29_centos opentenbase]# go run conn.go 
访问时间： 2018-04-03 20:40:28
日志级别： Log
详细信息： 连接数据库成功
```  
 
编译后运行  

```
[root@VM_0_29_centos opentenbase]# go build conn.go 
[root@VM_0_29_centos opentenbase]# ./conn 
访问时间： 2018-04-03 20:40:48
日志级别： Log
详细信息： 连接数据库成功
```  

### 6.2、创建数据表  
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
 
    //连接数据库
    conn, err := db_connect()
    if err != nil {
        error_msg = "连接数据库失败，详情：" + err.Error()
        write_log("Error", error_msg)
        return
    }
    //程序运行结束时关闭连接
    defer conn.Close()
    write_log("Log", "连接数据库成功")
 
    //建立数据表
    sql = "create table public.opentenbase(id varchar(20),nickname varchar(100)) distribute by shard(id) to group  default_group;"
    _, err = conn.Exec(sql)
    if err != nil {
        error_msg = "创建数据表失败,详情：" + err.Error()
        write_log("Error", error_msg)
        return
    } else {
        write_log("Log", "创建数据表成功")
    }
}
 
/*
功能描述：写入日志处理
 
参数说明：
log_level -- 日志级别，只能是是Error或Log
error_msg -- 日志内容
 
返回值说明：无
*/
 
func write_log(log_level string, error_msg string) {
    //打印错误信息
    fmt.Println("访问时间：", time.Now().Format("2006-01-02 15:04:05"))
    fmt.Println("日志级别：", log_level)
    fmt.Println("详细信息：", error_msg)
}
 
/*
功能描述：连接数据库
 
参数说明：无
 
返回值说明：
conn *pgx.Conn -- 连接信息
err error --错误信息
 
*/
 
func db_connect() (conn *pgx.Conn, err error) {
    var config pgx.ConnConfig
    config.Host = "127.0.0.1"    //数据库主机host或ip
    config.User = "opentenbase"         //连接用户
    config.Password = "pgsql"    //用户密码
    config.Database = "postgres" //连接数据库名
    config.Port = 15432          //端口号
    conn, err = pgx.Connect(config)
    return conn, err
}
```  

``` 
[root@VM_0_29_centos opentenbase]# go run createtable.go 
访问时间： 2018-04-03 20:50:24
日志级别： Log
详细信息： 连接数据库成功
访问时间： 2018-04-03 20:50:24
日志级别： Log
详细信息： 创建数据表成功
```  

### 6.3、插入数据
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
 
    //连接数据库
    conn, err := db_connect()
    if err != nil {
        error_msg = "连接数据库失败，详情：" + err.Error()
        write_log("Error", error_msg)
        return
    }
    //程序运行结束时关闭连接
    defer conn.Close()
    write_log("Log", "连接数据库成功")
 
    //插入数据
    sql = "insert into public.opentenbase values('1','opentenbase'),('2','pgxz');"
    _, err = conn.Exec(sql)
    if err != nil {
        error_msg = "插入数据失败,详情：" + err.Error()
        write_log("Error", error_msg)
        return
    } else {
        write_log("Log", "插入数据成功")
    }
 
    //绑定变量插入数据,不需要做防注入处理
    sql = "insert into public.opentenbase values($1,$2),($1,$3);"
    _, err = conn.Exec(sql, "3", "postgresql", "postgres")
    if err != nil {
        error_msg = "插入数据失败,详情：" + err.Error()
        write_log("Error", error_msg)
        return
    } else {
        write_log("Log", "插入数据成功")
    }
 
    //拼接sql语句插入数据,需要做防注入处理
    nickname = "OpenTenBase is ' good!"
    sql = "insert into public.opentenbase values('1','" + sql_data_encode(nickname) + "')"
    _, err = conn.Exec(sql)
    if err != nil {
        error_msg = "插入数据失败,详情：" + err.Error()
        write_log("Error", error_msg)
        return
    } else {
        write_log("Log", "插入数据成功")
    }
}
 
/*
功能描述：sql查询拼接字符串编码
 
参数说明：
str -- 要编码的字符串
 
返回值说明：
返回编码过的字符串
 
*/
 
func sql_data_encode(str string) string {
    return strings.Replace(str, "'", "''", -1)
}
 
/*
功能描述：写入日志处理
 
参数说明：
log_level -- 日志级别，只能是是Error或Log
error_msg -- 日志内容
 
返回值说明：无
*/
 
func write_log(log_level string, error_msg string) {
    //打印错误信息
    fmt.Println("访问时间：", time.Now().Format("2006-01-02 15:04:05"))
    fmt.Println("日志级别：", log_level)
    fmt.Println("详细信息：", error_msg)
}
 
/*
功能描述：连接数据库
 
参数说明：无
 
返回值说明：
conn *pgx.Conn -- 连接信息
err error --错误信息
 
*/
 
func db_connect() (conn *pgx.Conn, err error) {
    var config pgx.ConnConfig
    config.Host = "127.0.0.1"    //数据库主机host或ip
    config.User = "opentenbase"         //连接用户
    config.Password = "pgsql"    //用户密码
    config.Database = "postgres" //连接数据库名
    config.Port = 15432          //端口号
    conn, err = pgx.Connect(config)
    return conn, err
}
```  

``` 
[root@VM_0_29_centos opentenbase]# go run insert.go 
访问时间： 2018-04-03 21:05:51
日志级别： Log
详细信息： 连接数据库成功
访问时间： 2018-04-03 21:05:51
日志级别： Log
详细信息： 插入数据成功
访问时间： 2018-04-03 21:05:51
日志级别： Log
详细信息： 插入数据成功
访问时间： 2018-04-03 21:05:51
日志级别： Log
详细信息： 插入数据成功
```  

### 6.4、查询数据
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
 
    //连接数据库
    conn, err := db_connect()
    if err != nil {
        error_msg = "连接数据库失败，详情：" + err.Error()
        write_log("Error", error_msg)
        return
    }
    //程序运行结束时关闭连接
    defer conn.Close()
    write_log("Log", "连接数据库成功")
 
    sql = "SELECT id,nickname FROM public.opentenbase LIMIT 2"
    rows, err := conn.Query(sql)
    if err != nil {
        error_msg = "查询数据失败,详情：" + err.Error()
        write_log("Error", error_msg)
        return
    } else {
        write_log("Log", "查询数据成功")
    }
 
    var nickname string
    var id string
 
    for rows.Next() {
        err = rows.Scan(&id, &nickname)
        if err != nil {
            error_msg = "执行查询失败，详情：" + err.Error()
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
        error_msg = "查询数据失败,详情：" + err.Error()
        write_log("Error", error_msg)
        return
    } else {
        write_log("Log", "查询数据成功")
    }
    defer rows.Close()
 
    for rows.Next() {
        err = rows.Scan(&id, &nickname)
        if err != nil {
            error_msg = "执行查询失败，详情：" + err.Error()
            write_log("Error", error_msg)
            return
        }
        error_msg = fmt.Sprintf("id：%s nickname：%s", id, nickname)
        write_log("Log", error_msg)
    }
}
 
/*
功能描述：sql查询拼接字符串编码
 
参数说明：
str -- 要编码的字符串
 
返回值说明：
返回编码过的字符串
 
*/
 
func sql_data_encode(str string) string {
    return strings.Replace(str, "'", "''", -1)
}
 
/*
功能描述：写入日志处理
 
参数说明：
log_level -- 日志级别，只能是是Error或Log
error_msg -- 日志内容
 
返回值说明：无
*/
 
func write_log(log_level string, error_msg string) {
    //打印错误信息
    fmt.Println("访问时间：", time.Now().Format("2006-01-02 15:04:05"))
    fmt.Println("日志级别：", log_level)
    fmt.Println("详细信息：", error_msg)
}
 
/*
功能描述：连接数据库
 
参数说明：无
 
返回值说明：
conn *pgx.Conn -- 连接信息
err error --错误信息
 
*/
 
func db_connect() (conn *pgx.Conn, err error) {
    var config pgx.ConnConfig
    config.Host = "127.0.0.1"    //数据库主机host或ip
    config.User = "opentenbase"         //连接用户
    config.Password = "pgsql"    //用户密码
    config.Database = "postgres" //连接数据库名
    config.Port = 15432          //端口号
    conn, err = pgx.Connect(config)
    return conn, err
}
```  
``` 
[root@VM_0_29_centos opentenbase]# go run select.go
访问时间： 2018-04-09 10:35:50
日志级别： Log
详细信息： 连接数据库成功
访问时间： 2018-04-09 10:35:50
日志级别： Log
详细信息： 查询数据成功
访问时间： 2018-04-09 10:35:50
日志级别： Log
详细信息： id：2 nickname：opentenbase
访问时间： 2018-04-09 10:35:50
日志级别： Log
详细信息： id：3 nickname：postgresql
访问时间： 2018-04-09 10:35:50
日志级别： Log
详细信息： 查询数据成功
访问时间： 2018-04-09 10:35:50
日志级别： Log
详细信息： id：1 nickname：opentenbase
```  

### 6.5、流数据copy from入表 
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
 
    //连接数据库
    conn, err := db_connect()
    if err != nil {
        error_msg = "连接数据库失败，详情：" + err.Error()
        write_log("Error", error_msg)
        return
    }
    //程序运行结束时关闭连接
    defer conn.Close()
    write_log("Log", "连接数据库成功")
 
    //构造5000行数据
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
        error_msg = "执行copyFrom失败,详情：" + err.Error()
        write_log("Error", error_msg)
        return
    }
    if copyCount != len(inputRows) {
        error_msg = fmt.Sprintf("执行copyFrom失败，copy行数：%d 返回行数为：%d", len(inputRows), copyCount)
        write_log("Error", error_msg)
        return
    } else {
        error_msg = "Copy 记录成功"
        write_log("Log", error_msg)
    }
 
}
 
/*
功能描述：写入日志处理
 
参数说明：
log_level -- 日志级别，只能是是Error或Log
error_msg -- 日志内容
 
返回值说明：无
*/
 
func write_log(log_level string, error_msg string) {
    //打印错误信息
    fmt.Println("访问时间：", time.Now().Format("2006-01-02 15:04:05"))
    fmt.Println("日志级别：", log_level)
    fmt.Println("详细信息：", error_msg)
}
 
/*
功能描述：连接数据库
 
参数说明：无
 
返回值说明：
conn *pgx.Conn -- 连接信息
err error --错误信息
 
*/
 
func db_connect() (conn *pgx.Conn, err error) {
    var config pgx.ConnConfig
    config.Host = "127.0.0.1"    //数据库主机host或ip
    config.User = "opentenbase"         //连接用户
    config.Password = "pgsql"    //用户密码
    config.Database = "postgres" //连接数据库名
    config.Port = 15432          //端口号
    conn, err = pgx.Connect(config)
    return conn, err
}
``` 
``` 
[root@VM_0_29_centos opentenbase]# go run copy_from.go 
访问时间： 2018-04-09 10:36:40
日志级别： Log
详细信息： 连接数据库成功
访问时间： 2018-04-09 10:36:40
日志级别： Log
详细信息： Copy 记录成功
```

### 6.6、golang相关资源包
需要git的资源包:  
https://github.com/jackc/pgx  
https://github.com/pkg/errors  