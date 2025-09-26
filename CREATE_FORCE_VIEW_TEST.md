# `CREATE FORCE VIEW` 功能测试计划与数据

## 1. 测试概述

本文档提供了用于完整验证 OpenTenBase `CREATE FORCE VIEW` 功能的最终验收测试计划。该计划包含了所有必要的测试用例、指令、测试数据以及精确的、与在最终代码版本下运行完全一致的预期输出。

### 1.1. 测试目的

本测试计划旨在全面验证 `CREATE FORCE VIEW` 功能的正确性与健壮性，具体包括：

*   **核心功能:** 验证 `CREATE FORCE VIEW` 可以在依赖对象不存在时创建视图，并在依赖满足后自动变为可用。

*   **视图转换:** 验证由 `CREATE FORCE VIEW` 创建的视图，可以被 `CREATE OR REPLACE VIEW` 正确地转换为一个标准的、不再具有 `FORCE` 属性的正常视图。

*   **依赖管理:** 验证 `CREATE FORCE VIEW` 的依赖关系生命周期，确保其在被 `CREATE OR REPLACE VIEW` 命令“最终化”后，能够被 `DROP` (RESTRICT/CASCADE) 等命令正确地管理。

*   **边界情况:** 验证 `CREATE FORCE VIEW` 对 `SELECT *` 等不明确定义的健壮性处理，以及在 `REPLACE` 过程中对原生列定义（类型、名称）兼容性规则的遵守。

### 1.2. 测试环境

*   **数据库:** 已编译并安装了包含 `CREATE FORCE VIEW` 所有最终补丁的 OpenTenBase 版本。
*   **集群状态:** 一个干净的、已启动的 OpenTenBase 集群。
*   **工具:** `psql` 命令行客户端。
*   **运行平台:** 所有编译、调试和测试工作均在一个 **Docker 容器**中完成。
*   **执行用户:** 所有测试指令均由一个专门为此项目创建的、名为 `opentenbase` 的**非 root 普通用户**执行，以符合数据库的安全运行规范。

---

## 2. 独立测试用例 (Test Cases)

以下所有测试用例均被设计为完全独立的、自包含的。每一个测试用例都以清理环境的 `DROP` 语句开始，可以在任何时候独立运行，并预期得到与下面完全一致的输出。

### Part 1: 核心功能与生命周期

#### Test Case 1.1: 核心功能 - 创建、运行时失败、激活

*   **目的:** (覆盖目标 1.1) 验证 `CREATE FORCE VIEW` 的基本流程：成功创建，运行时因依赖缺失而失败，依赖满足后自动激活并成功查询。
*   **测试指令与数据:**
    ```sql
    DROP VIEW IF EXISTS core_view;
    DROP TABLE IF EXISTS base_table_1;
    CREATE FORCE VIEW core_view AS SELECT col1 FROM base_table_1;
    SELECT * FROM core_view;
    CREATE TABLE base_table_1 (col1 TEXT, col2 INT) DISTRIBUTE BY REPLICATION;
    INSERT INTO base_table_1 VALUES ('Core Functionality: Success!', 100);
    SELECT * FROM core_view;
    ```
*   **完整的预期输出:**
    ```
    DROP VIEW
    DROP TABLE
    CREATE VIEW
    ERROR:  node:dn1, backend_pid:..., nodename:dn1,backend_pid:...,message:relation "base_table_1" does not exist
    CREATE TABLE
    INSERT 0 1
               col1               
    ------------------------------
     Core Functionality: Success!
    (1 row)
    ```

---

### Part 2: 与 `CREATE OR REPLACE VIEW` 的交互

#### Test Case 2.1: 替换视图 - 类型不匹配 (预期失败)

*   **目的:** (覆盖目标 1.2 & 1.3 的限制) 验证 `CREATE OR REPLACE VIEW` 在列类型不匹配时，会如原生 PostgreSQL 一样报错，即使使用了 `FORCE` 关键字。
*   **测试指令与数据:**
    ```sql
    DROP VIEW IF EXISTS replace_type_view;
    DROP TABLE IF EXISTS replace_type_table;
    CREATE FORCE VIEW replace_type_view AS SELECT user_id FROM replace_type_table;
    CREATE TABLE replace_type_table (user_id INT) DISTRIBUTE BY REPLICATION;
    CREATE OR REPLACE FORCE VIEW replace_type_view AS SELECT user_id FROM replace_type_table;
    ```
*   **完整的预期输出:**
    ```
    DROP VIEW
    DROP TABLE
    CREATE VIEW
    CREATE TABLE
    ERROR:  cannot change data type of view column "user_id" from text to integer
    ```

#### Test Case 2.2: 替换视图 - 名称不匹配 (预期失败)

*   **目的:** (覆盖目标 1.2 & 1.3 的限制) 验证 `CREATE OR REPLACE VIEW` 在列名不匹配时，会如原生 PostgreSQL 一样报错，即使使用了 `FORCE` 关键字。
*   **测试指令与数据:**
    ```sql
    DROP VIEW IF EXISTS replace_name_view;
    DROP TABLE IF EXISTS replace_name_table;
    CREATE FORCE VIEW replace_name_view AS SELECT user_id FROM replace_name_table;
    CREATE TABLE replace_name_table (user_id_new INT) DISTRIBUTE BY REPLICATION;
    CREATE OR REPLACE FORCE VIEW replace_name_view AS SELECT user_id_new FROM replace_name_table;
    ```
*   **完整的预期输出:**
    ```
    DROP VIEW
    DROP TABLE
    CREATE VIEW
    CREATE TABLE
    ERROR:  cannot change name of view column "user_id" to "user_id_new"
    ```

#### Test Case 2.3: 正确的 `REPLACE` 工作流程 (转换与 `FORCE` 属性移除)

*   **目的:** (覆盖目标 1.2 & 1.3) 验证 `FORCE VIEW` 转换为 `NORMAL VIEW` 的正确工作流程，并验证其 `FORCE` 属性已被移除。
*   **测试指令与数据:**
    ```sql
    DROP VIEW IF EXISTS correct_replace_view;
    DROP TABLE IF EXISTS base_table_correct, non_existent_table;
    CREATE FORCE VIEW correct_replace_view AS SELECT user_id FROM base_table_correct;
    CREATE TABLE base_table_correct (user_id TEXT) DISTRIBUTE BY REPLICATION;
    INSERT INTO base_table_correct VALUES ('user_abc');
    CREATE OR REPLACE VIEW correct_replace_view AS SELECT user_id FROM base_table_correct;
    SELECT * FROM correct_replace_view;
    DROP TABLE base_table_correct CASCADE;
    CREATE OR REPLACE VIEW correct_replace_view AS SELECT user_id FROM non_existent_table;
    ```
*   **完整的预期输出:**
    ```
    DROP VIEW
    DROP TABLE
    CREATE VIEW
    CREATE TABLE
    INSERT 0 1
    CREATE VIEW
     user_id
    ----------
     user_abc
    (1 row)
    NOTICE:  drop cascades to view correct_replace_view
    DROP TABLE
    ERROR:  relation "non_existent_table" does not exist
    ```

---

### Part 3: 依赖管理与边界情况

#### Test Case 3.1: 依赖关系与 `DROP` (最终化工作流)

*   **目的:** (覆盖目标 1.4) 验证视图依赖关系的完整生命周期：只有在被 `REPLACE` 命令最终化之后，依赖关系才被正式建立。
*   **测试指令与数据:**
    ```sql
    DROP VIEW IF EXISTS dependency_view;
    DROP TABLE IF EXISTS base_table_depend;
    CREATE FORCE VIEW dependency_view AS SELECT val FROM base_table_depend;
    CREATE TABLE base_table_depend (val TEXT) DISTRIBUTE BY REPLICATION;
    DROP TABLE base_table_depend;
    CREATE TABLE base_table_depend (val TEXT) DISTRIBUTE BY REPLICATION;
    CREATE OR REPLACE VIEW dependency_view AS SELECT val FROM base_table_depend;
    DROP TABLE base_table_depend;
    DROP TABLE base_table_depend CASCADE;
    SELECT * FROM dependency_view;
    ```
*   **完整的预期输出:**
    ```
    DROP VIEW
    DROP TABLE
    CREATE VIEW
    CREATE TABLE
    DROP TABLE
    CREATE TABLE
    CREATE VIEW
    ERROR:  cannot drop table base_table_depend because other objects depend on it
    DETAIL:  view dependency_view depends on table base_table_depend
    HINT:  Use DROP ... CASCADE to drop the dependent objects too.
    NOTICE:  drop cascades to view dependency_view
    DROP TABLE
    ERROR:  relation "dependency_view" does not exist
    ```

#### Test Case 3.2: `SELECT *` 边界情况

*   **目的:** 验证为 `SELECT *` 添加的健壮性检查，确保在创建时就拒绝此类不明确的 `FORCE VIEW`。
*   **测试指令与数据:**
    ```sql
    DROP VIEW IF EXISTS star_test_view;
    CREATE FORCE VIEW star_test_view AS SELECT * FROM non_existent_star_table;
    ```
*   **完整的预期输出:**
    ```
    DROP VIEW
    ERROR:  CREATE FORCE VIEW does not support "*" for relations that do not exist
    HINT:  Please explicitly list the column names in the SELECT statement.
    ```