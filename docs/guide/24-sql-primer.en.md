# SQL Primer: Three Statements From Table to Query

This page is for readers who have never used OpenTenBase before. It picks three basic SQL examples from the existing documentation, explains them line by line in the order "create a table, insert data, query data", and points out the parts that usually confuse newcomers.

> **How this page was verified**
>
> Every example is quoted from the OpenTenBase documentation, with its source given inline. All outputs are **expected results** derived from the documentation; the author did not execute these statements against a live cluster. To verify them on a real instance, see [Quick Start](01-quickstart.en.md).

## 1、Reading order

| Step | Statement | Question it answers | Example |
| --- | --- | --- | --- |
| 1 | `CREATE TABLE` | Where does the data live and how is it distributed? | Example 1 |
| 2 | `INSERT` | How do I write data into it? | Example 2 |
| 3 | `SELECT` | How do I read data back, and which nodes are touched? | Example 3 |

The order matters because OpenTenBase is a distributed database: the distribution strategy is decided when the table is created, and it affects the performance of every later read and write.

## 2、Example 1: create a replication table

**Source**: [`docs/guide/03-basic-use.md`](https://github.com/OpenTenBase/docs/blob/main/docs/guide/03-basic-use.md), section "1.3、Create repilication table"; rendered page: [Basic Usage](https://docs.opentenbase.org/en/guide/03-basic-use/).

```sql
create table public.t1_rep
(
    f1 int not null,
    f2 varchar(20),
    primary key(f1)
)
distribute by replication
to group default_group;
```

Line by line:

| Code | What it does |
| --- | --- |
| `create table public.t1_rep` | Create table `t1_rep` in schema `public` |
| `f1 int not null` | Integer column, must not be null |
| `f2 varchar(20)` | Variable-length string, up to 20 characters |
| `primary key(f1)` | Primary key on `f1`, which also creates a primary key index |
| `distribute by replication` | Replication table: every DataNode keeps a full copy |
| `to group default_group` | Place it in the default storage group, that is, all DataNodes |

**Expected result**: `CREATE TABLE`.

**When to use it**: the same section says replication tables suit small tables that are frequently joined across nodes. It also lists two constraints: every node stores the full data set, so it does not suit large tables, and update performance is lower.

## 3、Example 2: insert two rows at once

**Source**: the same page, section "2.1、INSERT".

```sql
CREATE TABLE public.t1_insert_mul
(
    f1 int not null,
    f2 varchar(20),
    primary key(f1)
) distribute by shard(f1) to group default_group;

INSERT INTO t1_insert_mul VALUES (1,'opentenbase'),(2,'pg');
```

Line by line:

| Code | What it does |
| --- | --- |
| `distribute by shard(f1)` | Shard table: the value of `f1` decides which DataNode holds the row |
| `to group default_group` | Use the default storage group, which contains several DataNodes |
| `INSERT INTO ... VALUES (...),(...)` | Insert two rows in one statement, with value groups separated by commas |
| `(1,'opentenbase')`、`(2,'pg')` | The two rows, in the column order given at creation time |

**Expected result**: `INSERT 0 2` (output quoted from the documentation, an expected result).

**A common misunderstanding**: because the table is sharded on `f1`, the row with `f1 = 1` and the row with `f1 = 2` may well land on different nodes. That is expected behaviour, not a half-finished insert.

## 4、Example 3: query by the distribution key

**Source**: the same page, section "2.4、SELECT".

```sql
explain select * from t1_select where f1=1;
```

Line by line:

| Code | What it does |
| --- | --- |
| `explain` | Show the plan only, without returning rows |
| `select *` | Select all columns |
| `from t1_select` | Read from the shard table created earlier |
| `where f1=1` | The condition hits the distribution key, so a single DataNode can be used |

**Expected result**: the plan contains `Node/s: dn001` and an `Index Scan` on that node (output quoted from the documentation, an expected result).

**Takeaway**: the same section states that queries on the distribution key have the best performance and scalability; conditions that do not hit it are sent to all nodes and then aggregated on the Coordinator.

## 5、The sentence that is hardest to read

The original documentation explains the syntax in two sentences:

> `distribute by shard(x)` specifies the distribution key: the value of this field decides which node holds the data.
>
> `to group xxx` specifies the storage group (each storage group may contain several nodes).

After reading that, newcomers still mix up three things: the distribution key, the storage group, and the primary key. The improved explanation:

| Concept | One-line explanation | In the example |
| --- | --- | --- |
| Distribution key | The column whose value decides which DataNode stores a row | `f1` in `shard(f1)` |
| Storage group | A set of DataNodes the table may use | `default_group` |
| Primary key | Guarantees row uniqueness; unrelated to distribution | `primary key(f1)` |

> **Do not mistake an analogy for a technical fact**
>
> You can picture it as "split students by the last digit of their ID (distribution key) and only use these buildings (storage group)", but the analogy only builds intuition. The real sharding rule is a hash computation; refer to the documentation and source code for exact behaviour.

## 6、Exercises

1. Rewrite Example 1 as a shard table on `f1`. What should the `distribute by` line become?
   Check: `distribute by shard(f1)`, everything else unchanged.
2. After the insert in Example 2, what is the expected result of `select count(*) from t1_insert_mul;`?
   Check: two rows were inserted, so the expected value is 2.
3. What happens with `update t1_insert_mul set f1 = 3 where f1 = 1;`?
   Check: `f1` is the distribution key and cannot be updated. The documentation shows `ERROR: Distributed column or partition column "f1" can't be updated in current version`.

## 7、Source cross-check

| Explanation | Basis | Result |
| --- | --- | --- |
| Replication tables store full data on every node, suit small tables, and update slowly | 03-basic-use.md, section 1.3 | Consistent |
| `distribute by shard(f1)` distributes by the field value | 03-basic-use.md, section 1.1 | Consistent |
| Creating a replication table outputs `CREATE TABLE` | 03-basic-use.md, section 1.3 code block | Consistent |
| Multi-row insert outputs `INSERT 0 2` | 03-basic-use.md, section 2.1 code block | Consistent |
| A query on the distribution key touches one DataNode | 03-basic-use.md, section 2.4 EXPLAIN output | Consistent |
| The distribution key cannot be updated | 03-basic-use.md, section 2.2 error example | Consistent |

## 8、References

- [Basic Usage (source)](https://github.com/OpenTenBase/docs/blob/main/docs/guide/03-basic-use.en.md)
- [Basic Usage (rendered)](https://docs.opentenbase.org/en/guide/03-basic-use/)
- [Quick Start](01-quickstart.en.md)
- [Application Access](02-access.en.md)
