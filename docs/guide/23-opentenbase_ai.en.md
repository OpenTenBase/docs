# opentenbase_ai Plugin Documentation

## Introduction

The opentenbase_ai plugin provides an interface for integrating large language model AI capabilities into PostgreSQL databases, allowing you to use AI features directly in SQL. The plugin supports multiple AI model providers (including OpenAI, DeepSeek, Tencent Hunyuan, Alibaba Tongyi Qianwen, etc.), offering text generation, translation, sentiment analysis, question answering, text summarization, embedding vector generation, and image analysis capabilities.

## Installation

### Prerequisites

- HTTP extension (the plugin depends on HTTP extension for API calls)

### Installation Steps

1. Ensure your instance has the HTTP extension installed
2. Install the opentenbase_ai plugin:

```sql
CREATE EXTENSION opentenbase_ai;
```

Or install with the pgsql-http plugin together:
```sql
CREATE EXTENSION opentenbase_ai CASCADE;
```

## Quick Start (Using Hunyuan Model as Example)

### Configure Hunyuan Model

1. Obtain an API token for the Hunyuan model

2. Add the Hunyuan model definition to the model metadata table

   ```sql
   SELECT ai.add_completion_model(
       model_name => 'hunyuan_chat',
       uri => 'https://api.hunyuan.cloud.tencent.com/v1/chat/completions',
       default_args => '{"model": "hunyuan-lite"}'::jsonb,
       token => 'your_hunyuan_api_key',
       model_provider => 'tencent'
   );
   ```

3. Configure Hunyuan as the default model

   ```sql
   SET ai.completion_model = 'hunyuan_chat';
   ```

### Using the LLM

After configuring the Hunyuan model, you can start using it:

**Text Generation**

```sql
SELECT ai.generate_text('Write an attractive description for the following product: Smart Watch');
```

**Sentiment Analysis**

```sql
SELECT ai.sentiment('This product is very good, I am satisfied');
```

**Text Summarization** 

```sql
SELECT ai.summarize('Here is a long product description text...');
```

**Generate with Specific Return Type**

```sql
SELECT ai.generate('9*9 = ?',NULL::integer);
```

### Model Management

#### Adding Models

The plugin provides multiple ways to add AI models:

1. **Add OpenAI-compatible completion model**:

```sql
SELECT ai.add_completion_model(
    model_name => 'gpt-4',
    uri => 'https://api.openai.com/v1/chat/completions',
    default_args => '{"model": "gpt-4", "temperature": 0.7}'::jsonb,
    token => 'your_openai_api_key',
    model_provider => 'openai'
);
```

2. **Add OpenAI-compatible embedding model**:

```sql
SELECT ai.add_embedding_model(
    model_name => 'text-embedding-ada-002',
    uri => 'https://api.openai.com/v1/embeddings',
    default_args => '{"model": "text-embedding-ada-002"}'::jsonb,
    token => 'your_openai_api_key',
    model_provider => 'openai'
);
```

3. **Add OpenAI-compatible image model**:

```sql
SELECT ai.add_image_model(
    model_name => 'gpt-4-vision',
    uri => 'https://api.openai.com/v1/chat/completions',
    default_args => '{"model": "gpt-4-vision-preview", "max_tokens": 300}'::jsonb,
    token => 'your_openai_api_key',
    model_provider => 'openai'
);
```

4. **Examples of adding other LLM models**:

```sql
-- DeepSeek
SELECT ai.add_completion_model(
    model_name => 'deepseek-chat',
    uri => 'https://api.deepseek.com/v1/chat/completions',
    default_args => '{"model": "deepseek-chat", "temperature": 0.7}'::jsonb,
    token => 'your_deepseek_api_key',
    model_provider => 'deepseek'
);

-- Tencent Hunyuan
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

-- Alibaba Tongyi Qianwen
SELECT ai.add_completion_model(
    model_name => 'qwen_chat',
    uri => 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
    default_args => '{"model": "qwen-turbo"}'::jsonb,
    token => 'your_qwen_api_key',
    model_provider => 'aliyun'
);
```

> :bulb: **Tip:** Note that the 'model' field in default_args must be filled in.

#### Managing Existing Models

```sql
-- List all configured models
SELECT * FROM ai.list_models();

-- Get details for a specific model
SELECT * FROM ai.get_model_details('model_name');

-- Update model configuration
SELECT ai.update_model('model_name', 'config_field', 'new_value');

-- Delete a model
SELECT ai.delete_model('model_name');
```

## Configuration

### Setting Default Models

You can configure the default AI models by setting the following GUC (Grand Unified Configuration) parameters:

```sql
-- Set the default text completion model
SET ai.completion_model = 'model_name';

-- Set the default embedding vector model
SET ai.embedding_model = 'embedding_model_name';

-- Set the default image analysis model
SET ai.image_model = 'image_model_name';
```

You can set these parameters at different levels:

```sql
-- Session level (only effective for the current session)
SET ai.completion_model = 'gpt-4';

-- User level (effective for all sessions of a specific user)
ALTER USER username SET ai.completion_model = 'gpt-4';

-- Database level (effective for all sessions in a specific database)
ALTER DATABASE dbname SET ai.completion_model = 'gpt-4';

-- Global level (needs to be configured in postgresql.conf)
-- Add to postgresql.conf: ai.completion_model = 'gpt-4'
```

## Basic Features

### Polymorphic Generate Function

The core of opentenbase_ai is its polymorphic `generate` function, which can return different data types as needed. This function is the foundation for all type-specific generation functions:

```sql
-- Complete signature of the polymorphic generate function
ai.generate(
    prompt text,             -- Prompt text
    dummy anyelement,        -- Placeholder to determine return type
    model_name text = NULL,  -- Optional: model name to use
    config jsonb = '{}'      -- Optional: additional configuration parameters
) RETURNS anyelement;        -- Returns a result of the same type as the dummy parameter
```

Usage examples:

```sql
-- Return text
SELECT ai.generate('What are the main features of PostgreSQL?', NULL::text);

-- Return integer
SELECT ai.generate('Calculate the result of 123 + 456', NULL::integer);

-- Return floating point
SELECT ai.generate('What is the value of pi?', NULL::double precision);

-- Return boolean
SELECT ai.generate('Is the Earth round?', NULL::boolean);

-- Specify model
SELECT ai.generate('What is artificial intelligence?', NULL::text, 'gpt-4');

-- Specify configuration
SELECT ai.generate(
    'Explain the basic principles of quantum computing',
    NULL::text,
    'gpt-4',
    '{"temperature": 0.2, "max_tokens": 1000}'::jsonb
);
```

The polymorphic generate function currently supports the following return types:
- Text types: text
- Integer types: integer, bigint
- Floating point types: real, double precision
- Boolean type: boolean

### Type-Specific Generation Functions

opentenbase_ai provides various type-specific generation functions, which are wrappers around the polymorphic `generate` function, generating different types of results based on your needs:

#### Text Generation

```sql
-- Basic text generation
SELECT ai.generate_text('Please introduce the main features of PostgreSQL database');

-- Specify model
SELECT ai.generate_text('Please introduce the main features of PostgreSQL database', 'gpt-4');

-- Custom configuration parameters
SELECT ai.generate_text(
    'Please introduce the main features of PostgreSQL database',
    'gpt-4',
    '{"temperature": 0.3, "max_tokens": 500}'::jsonb
);
```

#### Numeric Generation

```sql
-- Integer generation
SELECT ai.generate_int('What is the world population?');

-- Floating point generation
SELECT ai.generate_double('What is the value of pi?');
```

#### Boolean Generation

```sql
-- Boolean generation
SELECT ai.generate_bool('Is the Earth round?');
```

### Text Processing Functions

#### Text Summarization

```sql
-- Basic usage
SELECT ai.summarize('Here is a long text content...');

-- Specify model
SELECT ai.summarize('Here is a long text content...', 'gpt-4');

-- Custom configuration
SELECT ai.summarize(
    'Here is a long text content...',
    'gpt-4',
    '{"temperature": 0.3}'::jsonb
);
```

#### Text Translation

```sql
-- Basic usage
SELECT ai.translate('Hello, world!', 'Chinese');

-- Translate to specific language
SELECT ai.translate('你好，世界！', 'English');

-- Specify model and configuration
SELECT ai.translate(
    '你好，世界！',
    'English',
    'gpt-4',
    '{"temperature": 0.3}'::jsonb
);
```

#### Sentiment Analysis

```sql
-- Basic usage
SELECT ai.sentiment('This product is very good, I am satisfied!');

-- Specify model
SELECT ai.sentiment('This product is very good, I am satisfied!', 'gpt-4');
```

#### Question Answering

```sql
-- Basic usage
SELECT ai.extract_answer(
    'Question: Who invented relativity?',
    'Einstein published the general theory of relativity in 1915, which was a major breakthrough in physics.'
);

-- Specify model and configuration
SELECT ai.extract_answer(
    'Question: Who invented relativity?',
    'Einstein published the general theory of relativity in 1915, which was a major breakthrough in physics.',
    'gpt-4',
    '{"temperature": 0.1}'::jsonb
);
```

### Embedding Vector Generation

```sql
-- Basic usage
SELECT ai.embedding('This is a text that needs to generate embedding vectors');

-- Specify model
SELECT ai.embedding('This is a text that needs to generate embedding vectors', 'text-embedding-ada-002');
```

### Image Analysis

```sql
-- Using image URL
SELECT ai.image('What is in this image?', 'https://example.com/image.jpg');

-- Using binary image data
SELECT ai.image('What is in this image?', image_data_column)
FROM images_table
WHERE id = 1;

-- Specify model and configuration
SELECT ai.image(
    'What is in this image?',
    'https://example.com/image.jpg',
    'gpt-4-vision',
    '{"max_tokens": 500}'::jsonb
);
```

> :bulb: **Tip:** Note that when calling a model, it will first use the model name specified in the function parameters. If not specified, it will use the default model set in the current GUC settings.

## Advanced Configuration and Customization

### Model Metadata Table

The opentenbase_ai plugin uses the ai_model_list table to store configuration information for all models. The structure of this table is as follows:

```sql
CREATE TABLE public.ai_model_list (
    model_name TEXT PRIMARY KEY,        -- Model name
    model_provider TEXT,                -- Model provider
    request_type TEXT NOT NULL,         -- Request type (GET/POST etc.)
    request_header http_header[],       -- HTTP request headers
    uri TEXT NOT NULL,                  -- API endpoint URL
    content_type TEXT NOT NULL,         -- Content type
    default_args JSONB NOT NULL,        -- Default parameters
    json_path TEXT NOT NULL             -- JSON response path
)
```

### Adding Non-OpenAI Compatible Format Models

The opentenbase_ai plugin supports adding models with non-OpenAI compatible formats through the ai.add_model function. This allows you to integrate model services with any custom API format:

```sql
SELECT ai.add_model(
    model_name => 'custom_model',           -- Model name
    request_header => ARRAY[                -- Request headers
        http_header('Authorization', 'Bearer your_token'),
        http_header('X-Custom-Header', 'value')
    ],
    uri => 'https://api.example.com/v1/endpoint',  -- API endpoint
    default_args => '{"key": "value"}'::jsonb,     -- Default parameters
    model_provider => 'custom',                    -- Provider
    request_type => 'POST',                        -- Request type
    content_type => 'application/json',            -- Content type
    json_path => 'SELECT %L::jsonb->''result''->''text''::TEXT'  -- Response parsing path (fill according to actual http response path)
);
```

## Network Configuration

opentenbase_ai makes HTTP calls to remote models through the pgsql-http plugin, so HTTP-related configuration can be modified through parameters related to the pgsql-http plugin.

Common parameter configurations are as follows:

```sql
-- Set request timeout in milliseconds
SET http.timeout_msec TO 200000;

SELECT http.http_set_curlopt('CURLOPT_TIMEOUT', '200000');

-- Set connection timeout
SELECT http.http_set_curlopt('CURLOPT_CONNECTTIMEOUT_MS', '200000')
```

For more detailed configuration, refer to the community pgsql-http plugin official website:

https://github.com/pramsey/pgsql-http

## Appendix

### Function List

| Feature | Function | Return Type |
| ------- | -------- | ----------- |
| Polymorphic Generation | `ai.generate(prompt, dummy, model_name, config)` | anyelement |
| Text Generation | `ai.generate_text(prompt, model_name, config)` | TEXT |
| Integer Generation | `ai.generate_int(prompt, model_name, config)` | INTEGER |
| Float Generation | `ai.generate_double(prompt, model_name, config)` | DOUBLE PRECISION |
| Boolean Generation | `ai.generate_bool(prompt, model_name, config)` | BOOLEAN |
| Text Summarization | `ai.summarize(text_content, model_name, config)` | TEXT |
| Text Translation | `ai.translate(text_content, target_language, model_name, config)` | TEXT |
| Sentiment Analysis | `ai.sentiment(text_content, model_name, config)` | TEXT |
| Question Answering | `ai.extract_answer(question, context, model_name, config)` | TEXT |
| Embedding Vector Generation | `ai.embedding(input, model_name, config)` | TEXT |
| Image Analysis | `ai.image(prompt, image_url, model_name, config)` | TEXT |
| Image Analysis | `ai.image(prompt, image_bytea, model_name, config)` | TEXT |

### Model Management Functions

| Feature | Function | Return Type |
| ------- | -------- | ----------- |
| Add Generic Model | `ai.add_model(...)` | BOOLEAN |
| Add Completion Model | `ai.add_completion_model(...)` | BOOLEAN |
| Add Embedding Model | `ai.add_embedding_model(...)` | BOOLEAN |
| Add Image Model | `ai.add_image_model(...)` | BOOLEAN |
| Delete Model | `ai.delete_model(model_name)` | BOOLEAN |
| Update Model Config | `ai.update_model(model_name, config, value)` | BOOLEAN |
| List All Models | `ai.list_models()` | SETOF ai_model_list |

### Advanced Usage

| Feature | Function | Return Type |
| ------- | -------- | ----------- |
| Low-level Model Call | `ai.invoke_model(model_name, user_args)` | TEXT |
| Raw HTTP Response | `ai.raw_invoke_model(model_name, user_args)` | http_response |

### GUC Parameter List

| Parameter Name | Description | Default Value | Level |
| -------------- | ----------- | ------------ | ----- |
| `ai.completion_model` | Default text completion model | NULL | USERSET |
| `ai.embedding_model` | Default embedding vector model | NULL | USERSET |
| `ai.image_model` | Default image analysis model | NULL | USERSET |