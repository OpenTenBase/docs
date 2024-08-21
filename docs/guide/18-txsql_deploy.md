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
# yum install -y git ncurses-devel bison cmake3 libaio-devel openssl openssl-devel cyrus-sasl-devel openldap-devel gtest libtirpc-devel 

### gcc
# yum install centos-release-scl -y
# yum install devtoolset-7-gcc devtoolset-7-gcc-c++ devtoolset-7-binutils -y
```

## 编译流程

选择tdsql-develop-8.0.18分支

```bash
# cd tdsql/

### -t 可选择debug和release模式
# bash make.sh -t release -r 1
```

编译生成的TXSQL二进制包，是存在代码库tdsql/mysql_install目录下

## 安装和卸载TXSQL

### 安装TXSQL

TXSQL在mysql-server-8.0.18的install目录下，有封装的install_mysql_innodb.sh脚本可以用于快速安装

```bash
# cd ./install
# export change_ip_before_use=$ip;bash ./install_mysql_innodb.sh default mysql $port $bpsize $datadir $logdir "character_set_server=utf8&collation_server=utf8_general_ci&lower_case_table_names=1"
```

- $ip：部署所在的本机物理ip，如：192.168.1.1
- $port：指定TCP/IP连接监听的端口号，如：4001
- $bpsize：innodb_buffer_pool_size配置，如：96000M
- $datadir：存储数据路径，如：/data2/tdsql/data
- $logdir：存储日志路径，如：/data2/tdsql/log

执行脚本后，有如下信息返回，则表示安装成功
```bash
...
+---------------------+
| now()               |
+---------------------+
| xxxx-xx-xx xx:xx:xx |
+---------------------+
+----------------------------------+
| version()                        |
+----------------------------------+
| 8.0.xx-v18-txsql-xx.x.x-xxxxxxxx |
+----------------------------------+
START SUCCESS.
[xxxx-xx-xx xx:xx:xx] installing finished:xxxx!
```
### 卸载TXSQL

卸载会清理该节点的所有binlog和数据，谨慎执行

```bash
# cd ./install
# ./uninstall_mysql.sh $port
```

- $port：安装TXSQL时指定的监听端口号，如：4001
