# Deploy a 1C2D Cluster with Docker

The OpenTenBase 1C2D Docker example is maintained on the
`example-distributed` branch of the
[OpenTenBase-DevEnv](https://github.com/OpenTenBase/OpenTenBase-DevEnv)
repository. It deploys four containers with a `1 GTM + 1 CN + 2 DN`
topology and is intended for local evaluation and functional testing.

## Prerequisites

- Install Git.
- Install Docker Engine with Docker Compose V2 (`docker compose`).
- This example currently requires x86_64. Its OpenTenBase package targets
  x86_64 and cannot run natively on an ARM64 host.
- The idle four-node cluster uses about 5.2 GiB of memory. Make at least
  5.2 GiB available.

## Get the example

Clone the repository and check out the maintained branch in this order:

```shell
git clone https://github.com/OpenTenBase/OpenTenBase-DevEnv.git
cd OpenTenBase-DevEnv
git checkout example-distributed
```

## Build and start the cluster

Build the four node images, and then start the cluster:

```shell
./otb-dev.sh build
./otb-dev.sh up
```

The build takes several minutes. After startup, inspect the four containers:

```shell
./otb-dev.sh status
```

## Connect to the database and enter containers

No database client is required on the host. Enter the coordinator first, and
then connect to `172.20.0.3:11000` from inside the container:

```shell
./otb-dev.sh enter cn
psql -h 172.20.0.3 -p 11000 -U opentenbase postgres
```

The coordinator's port `11000` is also published to the host. If `psql` is installed on the host,
you can connect directly through `127.0.0.1:11000`:

```shell
psql -h 127.0.0.1 -p 11000 -U opentenbase postgres
```

Without a node argument, `enter` opens the GTM container. You can also select
a datanode:

```shell
./otb-dev.sh enter
./otb-dev.sh enter dn01
./otb-dev.sh enter dn02
```

Inside a container, the working directory is `/data/opentenbase`. Use
`opentenbase_ctl` to inspect or manage the cluster:

```shell
./opentenbase_ctl status
./opentenbase_ctl stop
./opentenbase_ctl start
```

## Topology and configuration

The example defines its distributed topology in `config.ini`:

| Node | Address | Role |
| --- | --- | --- |
| GTM | `172.20.0.2` | Global transaction manager |
| CN | `172.20.0.3:11000` | Coordinator, with its port published to the host |
| DN01 | `172.20.0.4` | Datanode 1 |
| DN02 | `172.20.0.5` | Datanode 2 |

The build runs `opentenbase_ctl install -c config.ini` to install the cluster.
At runtime, each node container also uses `opentenbase_ctl` to start its
instance. Before changing the topology, read the
[example branch documentation](https://github.com/OpenTenBase/OpenTenBase-DevEnv/tree/example-distributed).

## Common lifecycle commands

```shell
# Stop or restart existing containers
./otb-dev.sh stop
./otb-dev.sh start

# Follow all logs, or only the coordinator logs
./otb-dev.sh logs
./otb-dev.sh logs cn

# Stop and remove the containers
./otb-dev.sh down
```

After the cluster starts, continue with the [Quick Start](01-quickstart.en.md#usage) to create a database and a sharded table.
The example branch documentation also covers the build process, image
import/export, and troubleshooting.

## Legacy configuration filename

The removed 2.x Docker example used `pgxc_ctl`, whose default configuration
filename is `pgxc_ctl.conf`. The old guide's reference to `pgxc.conf` was a
typo; no rename was required. The maintained example uses neither legacy
filename: it uses `opentenbase_ctl` with `config.ini`.
