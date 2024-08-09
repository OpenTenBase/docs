# Intro for Build Cluster(1C2D) using docker

In this example, we try to build a cluster which includes 1 Coordinator Node and 2 Data Node using docker techniques. We aim to provide users with a basic example of building a distributed cluster using Docker for OpenTenbase. This will facilitate quick deployment for users and allow for further customization and development.

## 1.Build docker images

```shell
export SOURCECODE_PATH=/path/to/your/otb/source/code
cd ${SOURCECODE_PATH}/docker
./buildImage.sh
```

Commands above will build `opentenbasebase` and `opentenbase` images.

## 2.Start the example service and enter the CN contaioner
```shell
cd ${SOURCECODE_PATH}/example/1c_2d_cluster
docker-compose up -d
docker-compose exec opentenbaseCN /bin/bash

```

## 3.SSH trust configuration
```shell
su opentenbase
copy-ssh-keys
```

Enter "yes", then press Enter. Then enter the password "qwerty".

## 4.Deployment and initialization
Copy the configuration file to the specified directory:

```shell

mkdir ~/pgxc_ctl
cp ~/pgxc_conf/pgxc_ctl.conf ~/pgxc_ctl
```
Use `pgxc_ctl` for deployment. Avoid using commands like `ls` or `echo` after entering `pgxc_ctl`.
```shell
pgxc_ctl                                # This step will enter --home location, which is by default /home/$USER/pgxc_ctl. Type exit to exit or Ctrl + D
deploy all                              # This will use pgxc.conf located in /home/$USER/pgxc_ctl/pgxc.conf for deployment
init all

exit
```


## 5.Connect OpenTenbase using psql

```shell
psql -h 172.16.200.10 -p 30004 -d postgres -U opentenbase
```

The following SQL commands are explained in detail in the [Quick Start](https://docs.opentenbase.org/guide/01-quickstart/#_3) section of the documentation:
```sql
-- Using dn001 and dn002 as storage nodes to form the default storage group
create default node group default_group  with (dn001,dn002); 
create sharding group to group default_group;      -- Setting up the storage group for tables of shard type
create database test;                              -- Creating the test database
create user test with password 'test';             -- Creating a user test with password test
alter database test owner to test;                 -- Changing the owner of the test database to the user test
\c test test                                       -- Switching to the test database
-- Creating a shard table foo, using id as the distribution key
create table foo(id bigint, str text) distribute by shard(id);
insert into foo values(1, 'tencent'), (2, 'shenzhen');
select * from foo;
```

After successful deployment, you can continue to explore other content in the official documentation.