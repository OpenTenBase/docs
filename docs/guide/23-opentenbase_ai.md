# opentenbase_ai 插件使用文档

## 简介

opentenbase_ai 插件为 PostgreSQL 数据库提供了集成人工智能大语言模型能力的接口，让您能够直接在 SQL 中使用 AI 功能。该插件支持多种 AI 模型提供商（包括 OpenAI、DeepSeek、腾讯混元、阿里通义千问等），提供文本生成、翻译、情感分析、问答提取、文本摘要、嵌入向量生成以及图像分析等功能。

## 安装

### 前提条件

- HTTP 扩展（该插件依赖 HTTP 扩展进行 API 调用）

### 安装步骤

1. 确保您的实例已安装 HTTP 扩展
2. 安装 opentenbase_ai 插件：

```sql
CREATE EXTENSION opentenbase_ai;
```

或者一并安装 pgsql-http 插件
```sql
CREATE EXTENSION opentenbase_ai CASCADE;


## 快速开始（以混元大模型为例）

### 配置混元大模型

1. 获取混元大模型的api token

2. 添加混元大模型的模型定义到模型元数据表中

   ```sql
   SELECT ai.add_completion_model(
       model_name => 'hunyuan_chat',
       uri => 'https://api.hunyuan.cloud.tencent.com/v1/chat/completions',
       default_args => '{"model": "hunyuan-lite"}'::jsonb,
       token => 'your_hunyuan_api_key',
       model_provider => 'tencent'
   );
   ```

3. 配置混元大模型为默认模型

   ```sql
   SET ai.completion_model = 'hunyuan_chat';
   ```

### 大模型问答

配置好混元大模型后就可以开始体验

**文本生成**

```sql
SELECT ai.generate_text('为以下产品写一段吸引人的描述：智能手表');
```

**情感分析**

```sql
SELECT ai.sentiment('这个产品非常好用，我很满意');
```

**文本摘要** 

```sql
SELECT ai.summarize('这里是一段很长的产品说明文本...');
```

**指定返回类型生成**

```sql
SELECT ai.generate('9*9 = ?',NULL::integer);
```



### 模型管理

#### 添加模型

插件提供了多种方式添加 AI 模型：

1. **添加 OpenAI 兼容的补全模型**：

```sql
SELECT ai.add_completion_model(
    model_name => 'gpt-4',
    uri => 'https://api.openai.com/v1/chat/completions',
    default_args => '{"model": "gpt-4", "temperature": 0.7}'::jsonb,
    token => 'your_openai_api_key',
    model_provider => 'openai'
);
```

2. **添加 OpenAI 兼容的嵌入模型**：

```sql
SELECT ai.add_embedding_model(
    model_name => 'text-embedding-ada-002',
    uri => 'https://api.openai.com/v1/embeddings',
    default_args => '{"model": "text-embedding-ada-002"}'::jsonb,
    token => 'your_openai_api_key',
    model_provider => 'openai'
);
```

3. **添加 OpenAI 兼容的图像模型**：

```sql
SELECT ai.add_image_model(
    model_name => 'gpt-4-vision',
    uri => 'https://api.openai.com/v1/chat/completions',
    default_args => '{"model": "gpt-4-vision-preview", "max_tokens": 300}'::jsonb,
    token => 'your_openai_api_key',
    model_provider => 'openai'
);
```

4. **添加国产大模型示例**：

```sql
-- DeepSeek
SELECT ai.add_completion_model(
    model_name => 'deepseek-chat',
    uri => 'https://api.deepseek.com/v1/chat/completions',
    default_args => '{"model": "deepseek-chat", "temperature": 0.7}'::jsonb,
    token => 'your_deepseek_api_key',
    model_provider => 'deepseek'
);

-- 腾讯混元
SELECT ai.add_completion_model(
    model_name => 'hunyuan_chat',
    uri => 'https://api.hunyuan.cloud.tencent.com/v1/chat/completions',
    default_args => '{"model": "hunyuan-lite"}'::jsonb,
    token => 'your_hunyuan_api_key',
    model_provider => 'tencent'
);

SELECT ai.add_completion_model(
    model_name => 'hunyuan_generate',
    uri => 'https://api.hunyuan.cloud.tencent.com/v1/chat/completions',
    default_args => '{
        "model": "hunyuan-lite"
    }'::jsonb,
    model_provider => 'tencent',
    token => 'your_hunyuan_api_key'
);


-- 阿里通义千问
SELECT ai.add_completion_model(
    model_name => 'qwen_chat',
    uri => 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
    default_args => '{"model": "qwen-turbo"}'::jsonb,
    token => 'your_qwen_api_key',
    model_provider => 'aliyun'
);
```

> :bulb: **Tip:** 注意 default_args 中的 model 字段，必须填写。




#### 管理现有模型

```sql
-- 列出所有已配置的模型
SELECT * FROM ai.list_models();

-- 获取特定模型的详细信息
SELECT * FROM ai.get_model_details('model_name');

-- 更新模型配置
SELECT ai.update_model('model_name', 'config_field', 'new_value');

-- 删除模型
SELECT ai.delete_model('model_name');
```

## 配置

### 设置默认模型

您可以通过设置以下 GUC（Grand Unified Configuration）参数来配置默认使用的 AI 模型：

```sql
-- 设置默认的文本补全模型
SET ai.completion_model = 'model_name';

-- 设置默认的嵌入向量模型
SET ai.embedding_model = 'embedding_model_name';

-- 设置默认的图像分析模型
SET ai.image_model = 'image_model_name';

```

您可以在以下级别设置这些参数：

```sql
-- 会话级别设置（仅对当前会话有效）
SET ai.completion_model = 'gpt-4';

-- 用户级别设置（对特定用户的所有会话有效）
ALTER USER username SET ai.completion_model = 'gpt-4';

-- 数据库级别设置（对特定数据库的所有会话有效）
ALTER DATABASE dbname SET ai.completion_model = 'gpt-4';

-- 全局级别设置（需要在 postgresql.conf 中配置）
-- 在 postgresql.conf 中添加：ai.completion_model = 'gpt-4'
```


## 基础功能

### 多态 generate 函数

opentenbase_ai 的核心是其多态 `generate` 函数，它可以根据需要返回不同的数据类型。这个函数是所有类型特定生成函数的基础：

```sql
-- 多态 generate 函数的完整签名
ai.generate(
    prompt text,             -- 提示文本
    dummy anyelement,        -- 用于确定返回类型的占位符
    model_name text = NULL,  -- 可选：使用的模型名称
    config jsonb = '{}'      -- 可选：额外的配置参数
) RETURNS anyelement;        -- 返回与 dummy 参数相同类型的结果
```

使用示例：

```sql
-- 返回文本
SELECT ai.generate('PostgreSQL 的主要特点是什么？', NULL::text);

-- 返回整数
SELECT ai.generate('计算 123 + 456 的结果', NULL::integer);

-- 返回浮点数
SELECT ai.generate('圆周率的值是多少？', NULL::double precision);

-- 返回布尔值
SELECT ai.generate('地球是圆的吗？', NULL::boolean);

-- 指定模型
SELECT ai.generate('什么是人工智能？', NULL::text, 'gpt-4');

-- 指定配置
SELECT ai.generate(
    '讲解量子计算的基本原理',
    NULL::text,
    'gpt-4',
    '{"temperature": 0.2, "max_tokens": 1000}'::jsonb
);
```

多态 generate 函数目前支持设置的返回类型有：
- 文本类型：text
- 整数类型：integer, biting
- 浮点数类型：real, double precision
- 布尔类型：boolean



### 类型特定生成函数

opentenbase_ai 提供了多种类型特定的生成函数，这些函数是对多态 `generate` 函数的封装，可根据您的需求生成不同类型的结果：

#### 文本生成

```sql
-- 基本文本生成
SELECT ai.generate_text('请介绍一下 PostgreSQL 数据库的主要特点');

-- 指定模型
SELECT ai.generate_text('请介绍一下 PostgreSQL 数据库的主要特点', 'gpt-4');

-- 自定义配置参数
SELECT ai.generate_text(
    '请介绍一下 PostgreSQL 数据库的主要特点',
    'gpt-4',
    '{"temperature": 0.3, "max_tokens": 500}'::jsonb
);
```

#### 数值生成

```sql
-- 整数生成
SELECT ai.generate_int('世界人口有多少？');

-- 浮点数生成
SELECT ai.generate_double('圆周率的值是多少？');
```

#### 布尔值生成

```sql
-- 布尔值生成
SELECT ai.generate_bool('地球是圆的吗？');
```



### 文本处理函数

#### 文本摘要

```sql
-- 基本用法
SELECT ai.summarize('这里是一段很长的文本内容...');

-- 指定模型
SELECT ai.summarize('这里是一段很长的文本内容...', 'gpt-4');

-- 自定义配置
SELECT ai.summarize(
    '这里是一段很长的文本内容...',
    'gpt-4',
    '{"temperature": 0.3}'::jsonb
);
```

#### 文本翻译

```sql
-- 基本用法
SELECT ai.translate('你好，世界！', '中文');

-- 翻译为特定语言
SELECT ai.translate('你好，世界！', '英语');

-- 指定模型和配置
SELECT ai.translate(
    '你好，世界！',
    '英语',
    'gpt-4',
    '{"temperature": 0.3}'::jsonb
);
```

#### 情感分析

```sql
-- 基本用法
SELECT ai.sentiment('这个产品非常好用，我很满意！');

-- 指定模型
SELECT ai.sentiment('这个产品非常好用，我很满意！', 'gpt-4');
```

#### 问答提取

```sql
-- 基本用法
SELECT ai.extract_answer(
    '问题：谁发明了相对论？',
    '爱因斯坦在 1915 年发表了广义相对论，这是物理学的重大突破。'
);

-- 指定模型和配置
SELECT ai.extract_answer(
    '问题：谁发明了相对论？',
    '爱因斯坦在 1915 年发表了广义相对论，这是物理学的重大突破。',
    'gpt-4',
    '{"temperature": 0.1}'::jsonb
);
```

### 嵌入向量生成

```sql
-- 基本用法
SELECT ai.embedding('这是一段需要生成嵌入向量的文本');

-- 指定模型
SELECT ai.embedding('这是一段需要生成嵌入向量的文本', 'text-embedding-ada-002');
```

### 图像分析

```sql
-- 使用图像 URL
SELECT ai.image('这张图片中有什么？', 'https://example.com/image.jpg');

-- 使用二进制图像数据
SELECT ai.image('这张图片中有什么？', image_data_column)
FROM images_table
WHERE id = 1;

-- 指定模型和配置
SELECT ai.image(
    '这张图片中有什么？',
    'https://example.com/image.jpg',
    'gpt-4-vision',
    '{"max_tokens": 500}'::jsonb
);
```

> :bulb: **Tip:** 注意调用大模型时会首先根据函数参数中指定的模型名调用，如果没有指定，就会根据当前 guc 设置的默认模型 l 调用。


## 高级配置与定制

### 模型元数据表

opentenbase_ai 插件使用 ai_model_list 表来存储所有模型的配置信息。该表的结构如下

```sql
CREATE TABLE public.ai_model_list (
    model_name TEXT PRIMARY KEY,        -- 模型名称
    model_provider TEXT,                -- 模型提供商
    request_type TEXT NOT NULL,         -- 请求类型（GET/POST 等）
    request_header http_header[],       -- HTTP 请求头
    uri TEXT NOT NULL,                  -- API 端点 URL
    content_type TEXT NOT NULL,         -- 内容类型
    default_args JSONB NOT NULL,        -- 默认参数
    json_path TEXT NOT NULL             -- JSON 响应路径
)
```



### 添加非 OpenAI 兼容格式大模型

opentenbase_ai 插件支持通过 ai.add_model 函数添加非 OpenAI 兼容格式的大模型。这允许您集成任何自定义 API 格式的模型服务

```sql
SELECT ai.add_model(
    model_name => 'custom_model',           -- 模型名称
    request_header => ARRAY[                -- 请求头
        http_header('Authorization', 'Bearer your_token'),
        http_header('X-Custom-Header', 'value')
    ],
    uri => 'https://api.example.com/v1/endpoint',  -- API 端点
    default_args => '{"key": "value"}'::jsonb,     -- 默认参数
    model_provider => 'custom',                    -- 提供商
    request_type => 'POST',                        -- 请求类型
    content_type => 'application/json',            -- 内容类型
    json_path => 'SELECT %L::jsonb->''result''->''text''::TEXT'  -- 响应解析路径 (根据 http response 的实际路径填写)
);
```

## 网络配置

opentenbase_ai 对远端大模型发起 http 调用是通过 pgsql-http 插件，因此 http 相关的配置可以通过 pgsql-http 插件相关的参数配置进行修改

常见的参数配置如下 

```sql
-- 设置请求的超时时间，单位毫秒
SET http.timeout_msec TO 200000;

SELECT http.http_set_curlopt('CURLOPT_TIMEOUT', '200000');

-- 设置连接超时时间
SELECT http.http_set_curlopt('CURLOPT_CONNECTTIMEOUT_MS', '200000')
```

更多详细配置参考社区 pgsql-http 插件官网

https://github.com/pramsey/pgsql-http


## 附录

### 功能列表

| 功能         | 函数                                                         | 返回类型         |
| ------------ | ------------------------------------------------------------ | ---------------- |
| 多态生成     | `ai.generate(prompt, dummy, model_name, config)`             | anyelement       |
| 文本生成     | `ai.generate_text(prompt, model_name, config)`               | TEXT             |
| 整数生成     | `ai.generate_int(prompt, model_name, config)`                | INTEGER          |
| 浮点数生成   | `ai.generate_double(prompt, model_name, config)`             | DOUBLE PRECISION |
| 布尔值生成   | `ai.generate_bool(prompt, model_name, config)`               | BOOLEAN          |
| 文本摘要     | `ai.summarize(text_content, model_name, config)`             | TEXT             |
| 文本翻译     | `ai.translate(text_content, target_language, model_name, config)` | TEXT             |
| 情感分析     | `ai.sentiment(text_content, model_name, config)`             | TEXT             |
| 问答提取     | `ai.extract_answer(question, context, model_name, config)`   | TEXT             |
| 嵌入向量生成 | `ai.embedding(input, model_name, config)`                    | TEXT             |
| 图像分析     | `ai.image(prompt, image_url, model_name, config)`            | TEXT             |
| 图像分析     | `ai.image(prompt, image_bytea, model_name, config)`          | TEXT             |

### 模型管理函数

| 功能         | 函数                                         | 返回类型            |
| ------------ | -------------------------------------------- | ------------------- |
| 添加通用模型 | `ai.add_model(...)`                          | BOOLEAN             |
| 添加补全模型 | `ai.add_completion_model(...)`               | BOOLEAN             |
| 添加嵌入模型 | `ai.add_embedding_model(...)`                | BOOLEAN             |
| 添加图像模型 | `ai.add_image_model(...)`                    | BOOLEAN             |
| 删除模型     | `ai.delete_model(model_name)`                | BOOLEAN             |
| 更新模型配置 | `ai.update_model(model_name, config, value)` | BOOLEAN             |
| 列出所有模型 | `ai.list_models()`                           | SETOF ai_model_list |

### 高级用法

| 功能           | 函数                                         | 返回类型      |
| -------------- | -------------------------------------------- | ------------- |
| 底层模型调用   | `ai.invoke_model(model_name, user_args)`     | TEXT          |
| 原始 HTTP 响应 | `ai.raw_invoke_model(model_name, user_args)` | http_response |

### GUC 参数列表

| 参数名                | 描述               | 默认值 | 级别    |
| --------------------- | ------------------ | ------ | ------- |
| `ai.completion_model` | 默认的文本补全模型 | NULL   | USERSET |
| `ai.embedding_model`  | 默认的嵌入向量模型 | NULL   | USERSET |
| `ai.image_model`      | 默认的图像分析模型 | NULL   | USERSET |