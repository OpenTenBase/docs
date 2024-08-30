# TXSQL 安装指南

## 部署方案介绍

本文档适用于基于TXSQL分别在基于x86（64）芯片、基于ARM（鲲鹏920）系列芯片上的CentOS7.8、7.9，TencentOS Server，银河麒麟操作系统V10，如下表。

|CPU	| 操作系统 |
| ----- | ------- |
| X86_64	| CentOS 7.8、7.9（含补丁），TencentOS Server| 
|ARM（aarch64）鲲鹏920系列 | 银河麒麟V10（含补丁）|

## 编译TXSQL

### 安装依赖

```bash
yum install -y git ncurses-devel bison cmake3 libaio-devel openssl openssl-devel cyrus-sasl-devel openldap-devel gtest libtirpc-devel 

### gcc
yum install centos-release-scl -y
yum install devtoolset-7-gcc devtoolset-7-gcc-c++ devtoolset-7-binutils -y
```

## 编译流程

选择8.0分支

```bash
### -t 可选择debug和release模式
mkdir /tmp/txsql_extra && curl -o /txsql_extra/boost_1_70_0.tar.gz https://archives.boost.io/release/1.70.0/source/boost_1_70_0.tar.gz 
tar xzf /tmp/txsql_extra/boost_1_70_0.tar.gz -C /txsql_extra
./build.sh -b /tmp/txsql_extra/boost_1_70_0 -t release
```

编译生成的TXSQL二进制包，是存在代码库tdsql/mysql_install目录下

## 体验TXSQL
通过 mtr 拉起 mysqld 测试，在 mysql-test 目录下，执行 ./mtr --start 即可

```bash
cd bld-release/mysql-test
./mtr --start
```

待数据初始化好后，连接数据库
```shell
mysql -uroot -S bld-release/mysql-test/var/tmp/mysqld.1.sock
```

执行脚本后，有如下信息返回，则表示安装成功
```sql
# Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 8
Server version: 8.0.22-txsql-v18-txsql-22.3.0-20240830 Source distribution

Copyright (c) 2000, 2021, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mtr                |
| mysql              |
| performance_schema |
| sys                |
| test               |
+--------------------+
6 rows in set (0.00 sec)
```