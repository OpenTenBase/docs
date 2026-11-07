# SQL 伴读来源一致性校验

这个目录里只有一个工具，用处很窄：检查 `docs/guide/first-three-sql.md` 中引用的三条 SQL，是否仍与 `docs/guide/01-quickstart.md` 里的原文逐字一致。

## 为什么需要它

伴读手册的三条语句是从快速入门里逐字复制的。只要原文改了、伴读没跟上，读者就会看到一份“看起来对、实际上是旧版本”的解释。人工复查容易漏，这个工具把这件事变成一条命令。

它只回答“引用有没有走样”，不回答“解释对不对”，也不回答“SQL 能不能跑通”。

## 用法

在仓库根目录执行：

```bash
python3 tools/sql_guide/check.py --root .
```

输出示例：

```
sql-guide source consistency check
  manifest: tools/sql_guide/examples.json
  source:   docs/guide/01-quickstart.md
  guide:    docs/guide/first-three-sql.md

PASS  create-foo-table       guide:40 <- source:312
PASS  insert-foo-rows        guide:77 <- source:314
PASS  select-foo-all         guide:113 <- source:316

summary: 3 examples, 3 passed, 0 failed
```

机器可读输出：

```bash
python3 tools/sql_guide/check.py --root . --format json
```

JSON 包含 `schema_version`、`summary`、`files`、`results`、`issues`。出现不一致时，`results[].expected` 与 `results[].actual` 会给出原文与伴读两侧的语句（超过 160 字符截断）。报告不包含任何其他文件内容，也不包含口令。

## 退出码

| 退出码 | 含义 |
|---|---|
| `0` | 配置合法，三个示例全部与来源一致 |
| `1` | 文档缺失、定位失败、示例重复，或语句与来源不一致 |
| `2` | 命令行参数错误，或 `examples.json` 缺失／不是合法 JSON／结构不合法 |

`1` 与 `2` 的区分很重要：`1` 说明文档需要修，`2` 说明工具配置本身需要修。

## 定位方式

工具不依赖行号，因为行号会随文档编辑漂移。它依赖三件事：

1. **来源侧**：`examples.json` 指定来源文件和每条语句的开头（`statement_prefix`）。工具只扫描代码围栏内部、以 `postgres=#` 或 `test=>` 提示符开头的行，提示符之后的部分才是语句。围栏内的命令行、元命令和执行输出都不会被当成语句。
2. **伴读侧**：每条语句上方有一个 HTML 注释标记，标记与紧邻的 `sql` 围栏绑定：

   ````markdown
   <!-- sql-guide-example: create-foo-table -->
   ```sql
   create table foo(id bigint, str text) distribute by shard(id);
   ```
   ````

   标记与围栏之间只允许空行。
3. **唯一性**：每个 ID 在伴读里必须恰好出现一次，在来源里必须恰好匹配一条语句。匹配到两条以上时，工具报“歧义”并失败，不会自己挑一条。

## 比对规则

只做两件事：去掉已声明的提示符，去掉行首行尾空白。此外一律逐字比较：

- 不折叠字符串内部的空格（`'shenzhen'` 与 `'shen zhen'` 视为不同）；
- 不忽略大小写；
- 不做标点归一化，不替换全角／半角。

宁可误报，也不做模糊匹配——模糊匹配会让“已经改坏了但看起来差不多”的情况通过。

## 已知限制

- 只支持本项目约定的三个单行示例，不是通用 Markdown 解析器，也不是 SQL 解析器。
- 只识别 `postgres=#` 与 `test=>` 两种提示符，且必须在代码围栏内。
- 只比较语句文本。语句的**技术解释**是否正确、能否在某个环境执行、性能如何，都不在检查范围内。
- 不联网、不连接数据库、不执行任何 SQL、不修改仓库文件。
- 通过检查不代表文档整体正确，只代表这三条引用没有漂移。

## 测试

```bash
python3 -m unittest discover -s tools/sql_guide/tests -v
```

测试覆盖：正常通过、字符串字面量被改、内部空格差异、分号缺失、来源文件缺失、来源语句缺失、来源出现两条相同候选、伴读标记缺失／重复／后接非 SQL 围栏／多行代码块、清单非法 JSON／缺键／多键／版本不支持、JSON 报告可解析且计数一致、`--help` 返回 0，以及对本仓库真实文档的端到端检查。

## 新增一个示例

1. 在 `examples.json` 的 `examples` 里加一项：唯一 `id`，以及来源语句的开头 `statement_prefix`（要足够独特，避免匹配到多条）。
2. 在伴读文档中，把语句放进以 `sql` 标注的代码围栏，并在围栏上一行加 `<!-- sql-guide-example: <id> -->`。
3. 运行 `python3 tools/sql_guide/check.py --root .`，确认新示例为 `PASS`。
