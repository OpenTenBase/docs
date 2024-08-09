# OpenTenBase KubeBlocks 插件

此文件夹包含两个 Helm 图表，用于在 Kubernetes 集群上部署 OpenTenBase KubeBlocks 插件。使用此插件，您可以在 Kubernetes 上部署和管理 OpenTenBase 集群。

目前，已经支持操作系统架构 `amd64` 和 `arm64`。您可以按照以下步骤在您的笔记本电脑（包括 Mac M1）上部署 OpenTenBase 集群。这显著降低了用户体验 OpenTenBase 的门槛和难度。

## 什么是 KubeBlocks？

[KubeBlocks](https://github.com/apecloud/kubeblocks) 是一个开源的控制平面软件，运行并管理数据库、消息队列和其他数据基础设施在 K8s 上。KubeBlocks 的名字灵感来自 Kubernetes 和 LEGO 积木，意味着在 K8s 上运行和管理数据基础设施可以像玩 LEGO 积木一样标准化和高效。

关于 KubeBlocks 的更多信息可以在 [KubeBlocks GitHub repository](https://github.com/apecloud/kubeblocks) 和 [KubeBlocks website](https://kubeblocks.io/) 中找到。您可以在 [KubeBlocks Add-ons GitHub repository](https://github.com/apecloud/kubeblocks-addons) 中找到所有支持的插件。

## 前提条件

在您部署 OpenTenBase KubeBlocks 插件之前，您需要具备以下前提条件：

* 一个 Kubernetes 集群，您可以使用 [minikube](https://minikube.sigs.k8s.io/docs/) 创建一个本地集群进行测试
* 在本地机器上安装 `kubectl` 命令行工具
* 在本地机器上安装 `helm` 命令行工具
* 安装 `kbcli` 命令行工具以安装 KubeBlocks 控制平面

## 安装 KubeBlocks

请参考 [KubeBlocks installation guide](https://kubeblocks.io/docs/release-0.8/user_docs/installation/install-with-kbcli/install-kbcli) 在您的 Kubernetes 集群上安装 `kbcli` 和 KubeBlocks 控制平面。

## 部署 OpenTenBase 插件

要在您的 Kubernetes 集群上部署 OpenTenBase 插件，请按照以下步骤操作：

```bash
$ helm install opentenbase ./opentenbase
```

检查 ClusterDefinition 和 ClusterVersion：

```bash
$ kubectl get cd opentenbase
NAME          MAIN-COMPONENT-NAME   STATUS      AGE
opentenbase   gtm                   Available   11m

$ kubectl get cv |grep opentenbase
opentenbase-2.5.0     opentenbase          Available   12m
```

## 创建一个 OpenTenBase 集群
运行下列指令创建一个 OpenTenBase 集群:

```bash
$ helm install otb ./opentenbase-cluster
```

此命令将创建一个包含一个 GTM、一个 Coordinator 和两个 Datanode 的 OpenTenBase 集群。运行以下命令检查 OpenTenBase 集群的状态：

```bash
$ kubectl get cluster otb
NAME   CLUSTER-DEFINITION   VERSION              TERMINATION-POLICY   STATUS     AGE
otb    opentenbase          opentenbase-2.5.0   Delete               Creating   12s
```

检查 OpenTenBase 集群的 pods：

```bash
$ kubectl get pods -l app.kubernetes.io/instance=otb
NAME         READY   STATUS    RESTARTS   AGE
otb-cn-0-0   1/1     Running   0          2m39s
otb-dn-0-0   2/2     Running   0          2m39s
otb-dn-1-0   2/2     Running   0          2m39s
otb-gtm-0    1/1     Running   0          2m39s
```

检查所有组件的状态：

```bash
$ kbcli cluster describe otb
Name: otb        Created Time: Apr 07,2024 15:28 UTC+0800
NAMESPACE   CLUSTER-DEFINITION   VERSION              STATUS     TERMINATION-POLICY   
default     opentenbase          opentenbase-2.5.0   Updating   Delete               

Endpoints:
COMPONENT   MODE        INTERNAL                                  EXTERNAL   
gtm         ReadWrite   otb-gtm.default.svc.cluster.local:50001   <none>     
dn-0        ReadWrite   otb-dn-0.default.svc.cluster.local:5432   <none>     
dn-1        ReadWrite   otb-dn-1.default.svc.cluster.local:5432   <none>     
cn-0        ReadWrite   otb-cn-0.default.svc.cluster.local:5432   <none>     

Topology:
COMPONENT   INSTANCE     ROLE     STATUS    AZ       NODE                            CREATED-TIME                 
cn-0        otb-cn-0-0   <none>   Running   <none>   kind-control-plane/172.18.0.2   Apr 07,2024 15:28 UTC+0800   
dn-0        otb-dn-0-0   <none>   Running   <none>   kind-control-plane/172.18.0.2   Apr 07,2024 15:28 UTC+0800   
dn-1        otb-dn-1-0   <none>   Running   <none>   kind-control-plane/172.18.0.2   Apr 07,2024 15:28 UTC+0800   
gtm         otb-gtm-0    <none>   Running   <none>   kind-control-plane/172.18.0.2   Apr 07,2024 15:28 UTC+0800   

Resources Allocation:
COMPONENT   DEDICATED   CPU(REQUEST/LIMIT)   MEMORY(REQUEST/LIMIT)   STORAGE-SIZE   STORAGE-CLASS   
gtm         false       1 / 1                1Gi / 1Gi               data:20Gi      standard        
dn-0        false       1 / 1                1Gi / 1Gi               data:20Gi      standard        
dn-1        false       1 / 1                1Gi / 1Gi               data:20Gi      standard        
cn-0        false       1 / 1                1Gi / 1Gi               data:20Gi      standard        

Images:
COMPONENT   TYPE   IMAGE                                    
gtm         gtm    docker.io/domainlau/opentenbase:v2.5.0   
dn-0        dn     docker.io/domainlau/opentenbase:v2.5.0   
dn-1        dn     docker.io/domainlau/opentenbase:v2.5.0   
cn-0        cn     docker.io/domainlau/opentenbase:v2.5.0   

Show cluster events: kbcli cluster list-events -n default otb
```

## 连接到 OpenTenBase 集群
运行以下命令连接到 OpenTenBase 集群：

```bash
$ kubectl exec -it otb-cn-0-0 -- bash

opentenbase@otb-cn-0-0:~$ psql postgres
psql (PostgreSQL 10.0 OpenTenBase V2)
Type "help" for help.

postgres=# select * from pgxc_node;
 node_name | node_type | node_port |     node_host     | nodeis_primary | nodeis_preferred |   node_id   |  node_cluster_name  
-----------+-----------+-----------+-------------------+----------------+------------------+-------------+---------------------
 a_one     | G         |     50001 | otb-gtm           | t              | f                | -1343982441 | opentenbase_cluster
 dn_0      | D         |      5432 | otb-dn-0          | f              | f                |  1485981022 | opentenbase_cluster
 dn_1      | D         |      5432 | otb-dn-1          | f              | f                | -1300059100 | opentenbase_cluster
 cn_0      | C         |      5432 | otb-cn-0          | f              | f                | -1541982360 | opentenbase_cluster
(4 rows)

postgres=# create default node group default_group with(dn_0, dn_1);
CREATE NODE GROUP
postgres=# create sharding group to group default_group;
CREATE SHARDING GROUP
postgres=# clean sharding;
CLEAN SHARDING
postgres=# select * from pgxc_group;
  group_name   | default_group | group_members 
---------------+---------------+---------------
 default_group |             1 | 16384 16385
(1 row)
postgres=# create table public.t1_pt(
f1 int not null,
f2 timestamp not null,
f3 varchar(20),
primary key(f1)) 
partition by range (f2) 
begin (timestamp without time zone '2019-01-01 0:0:0') 
step (interval '1 month') partitions (3) 
distribute by shard(f1) 
to group default_group;
CREATE TABLE
postgres=# \d+ public.t1_pt
                                             Table "public.t1_pt"
 Column |            Type             | Collation | Nullable | Default | Storage  | Stats target | Description 
--------+-----------------------------+-----------+----------+---------+----------+--------------+-------------
 f1     | integer                     |           | not null |         | plain    |              | 
 f2     | timestamp without time zone |           | not null |         | plain    |              | 
 f3     | character varying(20)       |           |          |         | extended |              | 
Indexes:
    "t1_pt_pkey" PRIMARY KEY, btree (f1)
Distribute By: SHARD(f1)
Location Nodes: ALL DATANODES
Partition By: RANGE(f2)
     Partitions number: 3
     Start With: 2019-01-01
     Interval Of Partition: 1 MONTH
```

或者，您可以使用 `kubectl port-forward` 从本地机器连接到 OpenTenBase 集群：

```bash
$ kubectl port-forward svc/otb-cn-0 5432:5432
```

然后，您可以说使用 `psql` 连接到OpenTenBase 集群：

```bash
$ psql -h 127.0.0.1 -p 5432 -U opentenbase postgres
```

## 删除 OpenTenBase 集群

运行以下命令删除 OpenTenBase 集群：

```bash
$ helm uninstall otb
```
