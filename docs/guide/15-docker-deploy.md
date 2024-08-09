# 使用docker构建一个1C2D的OpenTenbase集群

在这个例子中，我们尝试使用 Docker 技术构建一个包含`1`个协调节点和`2`个数据节点的集群。我们的目标是为用户提供一个使用 Docker 构建 OpenTenbase 分布式集群的基本示例。这将方便用户快速部署，并允许进一步的定制和开发。

## 1. 构建docker镜像

```shell
export SOURCECODE_PATH=/path/to/your/otb/source/code
cd ${SOURCECODE_PATH}/docker
./buildImage.sh
```

上述指令会构建`opentenbasebase`和 `opentenbase`两个镜像。

## 2.启动 example 服务，进入 opentenbaseCN 容器
```shell
cd ${SOURCECODE_PATH}/example/1c_2d_cluster
docker-compose up -d
docker-compose exec opentenbaseCN /bin/bash

```

## 3.SSH 互信配置
```shell
su opentenbase
copy-ssh-keys
```

输入 "yes"，然后回车。然后输入密码 "qwerty"。

## 4. 部署和初始化
复制配置文件到指定目录:

```shell

mkdir ~/pgxc_ctl
cp ~/pgxc_conf/pgxc_ctl.conf ~/pgxc_ctl
```
使用 `pgxc_ctl`  进行部署，使用`pgxc_ctl`之后，不要敲 `ls` ,`echo` 这种命令。
```shell
pgxc_ctl                                # 这一步会进入 --home 位置，默认是/home/$USER/pgxc_ctl, 使用exit退出，或者ctrl + D
deploy all                              # 会使用/home/$USER/pgxc_ctl/pgxc.conf 这个配置文件
init all

exit
```


## 5.使用psql连接OpenTenbase

```shell
psql -h 172.16.200.10 -p 30004 -d postgres -U opentenbase
```

这一段sql语句在[Quick Start](https://docs.opentenbase.org/guide/01-quickstart/#_3)有详细的解释:
```sql
-- 使用 dn001, dn002 存储节点组成默认存储组
create default node group default_group  with (dn001,dn002); 
create sharding group to group default_group;      -- 设置 shard 类型的表使用的存储组
create database test;                              -- 创建 test 数据库
create user test with password 'test';             -- 创建一个 test 用户密码为 test
alter database test owner to test;                 -- 修改 test 数据库 owner 为 test 用户
\c test test                                       -- 切换到 test 数据库
-- 创建一个 shard 表 foo, 使用 id 作为分布键
create table foo(id bigint, str text) distribute by shard(id);
insert into foo values(1, 'tencent'), (2, 'shenzhen');
select * from foo;
```

部署成功后, 用户可以继续阅读官方文档的其他的内容。