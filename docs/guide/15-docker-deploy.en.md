# Intro for Build Cluster(1C2D) using docker

In this example, we try to build a cluster which includes 1 Coordinator Node and 2 Data Node using docker techniques. We aim to provide users with a basic example of building a distributed cluster using Docker for OpenTenbase. This will facilitate quick deployment for users and allow for further customization and development.

## 1.Build docker images

```shell
export SOURCECODE_PATH=/path/to/your/otb/source/code
cd ${SOURCECODE_PATH}/docker
./buildImage.sh
```

Commands above will build `opentenbasebase` and `opentenbase` images.

Replace `SOURCECODE_PATH` with the path of your local clone of this repository, for example `/data/opentenbase/OpenTenBase`.

## 2.Start the example service and enter the CN contaioner

> **Note**: the directory `${SOURCECODE_PATH}/example/1c_2d_cluster` no longer exists on the current `master` branch, so the commands below cannot be run as written.
> Its `docker-compose.yaml`, `README` and `pgxc_conf/` were removed together with the whole `example/` tree, by commit
> [`aca7e2c`](https://github.com/OpenTenBase/OpenTenBase/commit/aca7e2c34a25e1480548a20dc7462612fb8a17f7) ("Update basecode version from 2.6.0 to 5.0.0") in the OpenTenBase repository.
> The only part still present in that repository is the image build path used in step 1 (`docker/buildImage.sh`).
>
> The cluster configuration template used by this example is still published in this repository:
> <https://github.com/OpenTenBase/docs/blob/main/docs/guide/pgxc_ctl_double.conf>.
> If you need the removed `docker-compose.yaml`, it can be retrieved from the revision just before the deletion:
> <https://github.com/OpenTenBase/OpenTenBase/tree/efc01b0c079f73900ab2a199c90ff04fe3ad6435/example/1c_2d_cluster> (historical file, no longer maintained).

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
deploy all                              # This will use /home/$USER/pgxc_ctl/pgxc_ctl.conf for deployment
init all

exit
```

The configuration file name read by `pgxc_ctl` is fixed to `pgxc_ctl.conf`, located in the directory given by `--home`
(`$HOME/pgxc_ctl` by default); see `contrib/pgxc_ctl/pgxc_ctl.h` (`DEFAULT_CONF_FILE_NAME`) and
`contrib/pgxc_ctl/pgxc_ctl.c` (`build_configuration_path()`) in the OpenTenBase repository.
The file copied in step 4 therefore **must not be renamed**; `pgxc.conf` is the configuration file of a different,
unrelated tool, `pgxc_ddl`.

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