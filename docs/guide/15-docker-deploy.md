# 使用 Docker 部署 1C2D 集群

OpenTenBase 的 1C2D Docker 示例由
[OpenTenBase-DevEnv](https://github.com/OpenTenBase/OpenTenBase-DevEnv)
仓库的 `example-distributed` 分支持续维护。该示例会部署
`1 GTM + 1 CN + 2 DN` 共四个容器，适合本地体验和功能验证。

## 前置条件

- 已安装 Git。
- 已安装 Docker Engine，并可使用 Docker Compose V2（`docker compose`）。
- 此示例当前仅支持 x86_64；其 OpenTenBase 安装包为 x86_64 架构，
  不能在 ARM64 主机上原生运行。
- 空载四节点集群约占用 5.2 GiB 内存，请至少预留 5.2 GiB 可用内存。

## 获取示例

按照下面的顺序克隆仓库并切换到维护分支：

```shell
git clone https://github.com/OpenTenBase/OpenTenBase-DevEnv.git
cd OpenTenBase-DevEnv
git checkout example-distributed
```

## 构建并启动集群

构建四个节点镜像，然后启动集群：

```shell
./otb-dev.sh build
./otb-dev.sh up
```

构建需要几分钟。启动后可查看四个容器的状态：

```shell
./otb-dev.sh status
```

## 连接数据库和进入容器

无需在宿主机安装数据库客户端。先进入 CN，再从容器内连接
`172.20.0.3:11000`：

```shell
./otb-dev.sh enter cn
psql -h 172.20.0.3 -p 11000 -U opentenbase postgres
```

CN 的 `11000` 端口也映射到宿主机。如果宿主机已安装 `psql` 客户端，
也可以通过 `127.0.0.1:11000` 直接连接：

```shell
psql -h 127.0.0.1 -p 11000 -U opentenbase postgres
```

`enter` 不带节点参数时默认进入 GTM，也可以指定某个 DN：

```shell
./otb-dev.sh enter
./otb-dev.sh enter dn01
./otb-dev.sh enter dn02
```

进入容器后，当前目录为 `/data/opentenbase`，可用
`opentenbase_ctl` 查看或管理集群：

```shell
./opentenbase_ctl status
./opentenbase_ctl stop
./opentenbase_ctl start
```

## 拓扑和配置

示例使用 `config.ini` 描述分布式拓扑：

| 节点 | 地址 | 说明 |
| --- | --- | --- |
| GTM | `172.20.0.2` | 全局事务管理器 |
| CN | `172.20.0.3:11000` | 协调节点，端口映射到宿主机 |
| DN01 | `172.20.0.4` | 数据节点 1 |
| DN02 | `172.20.0.5` | 数据节点 2 |

构建阶段通过 `opentenbase_ctl install -c config.ini` 安装集群；运行时，
各节点容器也通过 `opentenbase_ctl` 启动对应实例。修改拓扑前，请先阅读
[示例分支说明](https://github.com/OpenTenBase/OpenTenBase-DevEnv/tree/example-distributed)。

## 常用生命周期命令

```shell
# 停止或重新启动现有容器
./otb-dev.sh stop
./otb-dev.sh start

# 持续查看全部日志，或只查看 CN 日志
./otb-dev.sh logs
./otb-dev.sh logs cn

# 停止并删除容器
./otb-dev.sh down
```

集群启动后，可继续参考[快速入门](01-quickstart.md#_9)创建数据库和分片表。
更完整的构建说明、镜像导入导出和故障排查步骤见上述示例分支说明。

## 旧版配置文件名说明

旧版 2.x Docker 示例使用的是 `pgxc_ctl`，其默认配置文件名为
`pgxc_ctl.conf`。旧文档中提到的 `pgxc.conf` 是笔误，实际文件无需重命名。
当前维护的示例不使用这两个旧版文件名，而是使用 `opentenbase_ctl` 和
`config.ini`。
