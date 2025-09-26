### **CREATE FORCE VIEW 功能详细设计文档**

#### 1. 引言

本设计的核心目标是在 OpenTenBase 中实现 CREATE FORCE VIEW 功能，以对齐 Oracle 数据库在该领域的行为。标准 CREATE VIEW 命令在解析阶段对所有依赖对象（表、函数等）进行严格的存在性校验，这在某些开发和部署场景下（如解耦的模块化部署、先部署应用逻辑后部署底层表）会造成不便。

CREATE FORCE VIEW 功能旨在解决此问题，允许在视图的依赖对象尚不存在时，也能成功创建视图的定义。

为实现此目标，我们确立了**“运行时延迟校验” (Run-Time Deferred Validation)** 的核心设计哲学。

此哲学将标准的**“编译时强校验” (Compile-Time Strong Validation)** 策略，转变为将存在性、权限和语义的最终校验，从 CREATE 命令的解析阶段，完全推迟到用户第一次 SELECT 该视图的**运行时（Run-Time）**。

#### 2. 核心实现机制

为在 OpenTenBase 复杂的内核中实现“延迟校验”，我们采取了一系列精确、协同且风险可控的修改。

- **文件:** src/backend/parser/gram.y, src/include/nodes/parsenodes.h
- **实现:**
  1. 在 SQL 语法文件 gram.y 中，为 CreateViewStmt 规则增加了可选的 FORCE 关键字。
  2. 在 ViewStmt 解析树节点结构体中，增加了一个 bool force 成员，用于在内核中传递 FORCE 模式的语义。

我们实现延迟校验的核心技巧，是在解析阶段创建一个**“占位符范围表条目 (Placeholder Range Table Entry - RTE)”**。

- **文件:** src/backend/parser/analyze.c, src/backend/parser/parse_relation.c
- **实现:**
  1. **会话级标志:** 引入一个安全的、有明确生命周期管理的全局标志 creating_force_view，用于在解析期间广播“宽容模式”。
  2. **修改 scanRTEForColumn**: 这是最关键的修改。在 creating_force_view 上下文中，当此函数遇到一个不存在的关系时，其行为被修改为：
     - **不报错**: 不再抛出 relation does not exist 错误。
     - **创建占位符**: 为该关系创建一个 relid 为 InvalidOid (0) 的 RTE。
     - **记录元数据**: 动态地将用户请求的列名记录到 rte->eref->colnames 列表中，并向并行的 rte->coltypes, rte->coltypmods, rte->colcollations 列表中，分别追加 UNKNOWNOID, -1, 和 InvalidOid。

一个 relid=0 的“占位符 RTE”无法被内核的下游模块正确处理。我们通过 lldb 调试，定位了所有因此而失败的关键函数，并为它们增加了相同的、精确的“豁免”补丁。

- **核心补丁逻辑:** if (!OidIsValid(rte->relid)) continue; 或类似逻辑。
- **被修复的模块与文件:**
  - **查询重写器 (src/backend/rewrite/rewriteHandler.c)**:
    - AcquireRewriteLocks: 避免了对 relid=0 的关系进行加锁。
    - fireRIRrules: 避免了在应用视图规则时打开 relid=0 的关系。
  - **分布式计划器 (PGXC)**:
    - pgxc_FQS_datanodes_for_rtr (src/backend/optimizer/util/pgxcship.c): 避免了在分析查询可下推性时，查询 relid=0 关系的元数据。
    - contains_temp_tables (src/backend/pgxc/plan/planner.c): 避免了在检查临时表时，打开 relid=0 的关系。
  - **查询反解析器 (src/backend/utils/adt/ruleutils.c)**:
    - set_relation_column_names: 避免了在获取列别名时，打开 relid=0 的关系。
    - get_from_clause_item: 避免了在将查询树转回 SQL 文本时，尝试为 relid=0 的关系生成其 catalog 名称。

#### 3. 关键设计决策与权衡

在开发和调试过程中，我们遇到了两个深层次的设计问题。在对 Oracle 实现进行研究并深入评估了多种方案的风险和复杂度后，我们做出了以下关键的工程决策。

- **问题描述:** 我们发现，解析器在处理未知列时，会将其类型**默认推断为 TEXT**，并且这个 TEXT 类型会被**永久地**写入 pg_attribute 系统目录。这导致后续 CREATE OR REPLACE VIEW 在面对底层表真实的、非 TEXT 类型（如 INTEGER）时，会因类型不匹配而失败。
- **方案权衡:**
  - **理想方案 (高风险):** 效仿 Oracle，引入通用的对象状态模型（VALID/INVALID）和自动重新编译机制。此方案需要对 pg_class, pg_attribute 等核心目录进行修改，并重构查询重写器的核心逻辑，开发成本和系统性风险极高。
  - **最终方案 (低风险):** **接受**此行为，并将其作为功能的一个明确约定。我们不修改 CREATE OR REPLACE VIEW 的核心类型保护机制，而是将类型兼容的责任交给用户。
- **最终理由:** 保证功能的稳定性和可预测性，优于追求一个可能引入巨大风险的“完美”方案。这是一个负责任的工程决策。
- **问题描述:** 我们通过 pg_depend 诊断发现，CREATE FORCE VIEW 命令本身**不会**创建依赖记录。这导致在视图被“最终化”之前，底层表可以被 DROP，造成数据不一致的风险。
- **方案权衡:**
  - **理想方案 (高风险):** 在查询重写器中，当第一次成功访问视图时，动态地、自动地“回填”依赖记录。此方案需要在性能敏感的核心模块中增加修改系统目录的操作，面临复杂的事务和并发挑战。
  - **最终方案 (零风险):** **依赖关系的建立，必须由用户通过一次后续的 CREATE OR REPLACE VIEW 命令来显式地“最终化”。**
- **最终理由:** 此方案完美地重用了 PostgreSQL 内核现有的、经过千锤百炼的 REPLACE 机制来管理依赖。它没有向内核引入任何新的、高风险的修改，并为用户提供了一个清晰、明确、且 100% 可靠的“视图激活”工作流程。

#### 4. 边界情况处理

- **文件:** src/backend/parser/parse_relation.c (expandRelAttrs)
- **实现:** 在 CREATE FORCE VIEW 命令的解析阶段，增加了对 SELECT * 的检查。如果 * 所引用的关系是一个不存在的“占位符 RTE”，命令将立即失败，并提示用户必须明确列出所有列名。
- **理由:** 当底层表的结构未知时，* 的含义是不明确的。在创建时就拒绝这种模棱两可的定义，是保证功能健壮性的必要措施。

#### 5. 总结

本设计成功地在 OpenTenBase 中实现了一个功能完备、行为健壮的 CREATE FORCE VIEW 功能。最终的实现方案，是在深入理解内核、充分评估风险后，在功能、成本和稳定性之间取得平衡的务实成果。它通过一个巧妙的“占位符 RTE”机制和一系列精准的“豁免”补丁，成功地实现了“运行时延迟校验”的核心哲学，并通过明确的设计边界和用户约定，保证了与系统其他部分的和谐共存。