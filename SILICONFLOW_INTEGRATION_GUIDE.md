# 硅基流动 (SiliconFlow) API 集成指南

> 本文档记录了如何将项目从 OpenAI API 切换到硅基流动 API 的完整过程，供后续维护人员参考。
> 
> 创建日期：2026-02-05

## 概述

本项目原本使用 OpenAI API 作为 LLM 服务提供商。本次改造实现了对硅基流动 API 的支持，硅基流动兼容 OpenAI API 格式，支持多种开源模型（DeepSeek、Qwen、Llama等），且价格更优惠。

## 修改文件清单

| 文件路径 | 修改内容 |
|---------|---------|
| `app/core/config.py` | 添加硅基流动配置项 |
| `app/services/llm.py` | 注册硅基流动模型到 LLMRegistry |
| `app/core/langgraph/graph.py` | 禁用长期记忆功能（需要 OpenAI Embeddings） |
| `.env.development` | 配置硅基流动 API 密钥和模型 |

---

## 详细修改步骤

### 1. 配置文件修改 (`app/core/config.py`)

在 `Settings` 类的 `__init__` 方法中，添加硅基流动和 DeepSeek 配置项：

```python
# 在 LangGraph Configuration 部分后添加

# SiliconFlow Configuration
self.SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
self.SILICONFLOW_BASE_URL = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
self.SILICONFLOW_MODEL = os.getenv("SILICONFLOW_MODEL", "Pro/deepseek-ai/DeepSeek-V3.2")

# DeepSeek Configuration
self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
self.DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
```

### 2. LLM 服务修改 (`app/services/llm.py`)

在 `LLMRegistry.LLMS` 列表中添加硅基流动模型：

```python
# Class-level variable containing all available LLM models
LLMS: List[Dict[str, Any]] = [
    # SiliconFlow models (if configured)
    *([{
        "name": "siliconflow-deepseek-v3.2",
        "llm": ChatOpenAI(
            model=settings.SILICONFLOW_MODEL,
            api_key=settings.SILICONFLOW_API_KEY,
            base_url=settings.SILICONFLOW_BASE_URL,
            temperature=settings.DEFAULT_LLM_TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            tiktoken_model_name="gpt-4",  # 重要：用于 token 计数
        ),
    }] if settings.SILICONFLOW_API_KEY else []),
    # DeepSeek models (if configured)
    *([{
        "name": "deepseek-chat",
        "llm": ChatOpenAI(
            model="deepseek-chat",
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            temperature=settings.DEFAULT_LLM_TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            tiktoken_model_name="gpt-4",  # 重要：用于 token 计数
        ),
    }] if settings.DEEPSEEK_API_KEY else []),
    # OpenAI models (原有配置保持不变)
    ...
]
```

#### 关键参数说明

| 参数 | 说明 |
|-----|------|
| `model` | 硅基流动的实际模型名称，如 `Pro/deepseek-ai/DeepSeek-V3.2` |
| `api_key` | 硅基流动 API 密钥 |
| `base_url` | 硅基流动 API 地址：`https://api.siliconflow.cn/v1` |
| `tiktoken_model_name` | **必须设置为 `gpt-4`**，否则会报 token 计数错误 |

### 3. 禁用长期记忆功能 (`app/core/langgraph/graph.py`)

由于长期记忆功能使用 OpenAI Embeddings API，而硅基流动不兼容该接口，需要在两个函数中添加跳过逻辑：

#### 3.1 修改 `_get_relevant_memory` 函数

```python
async def _get_relevant_memory(self, user_id: str, query: str) -> str:
    """Get the relevant memory for the user and query."""
    # Skip memory if not using OpenAI (embeddings not configured)
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("sk-hupwt"):
        return ""
    
    try:
        memory = await self._long_term_memory()
        results = await memory.search(user_id=str(user_id), query=query)
        return "\n".join([f"* {result['memory']}" for result in results["results"]])
    except Exception as e:
        logger.error("failed_to_get_relevant_memory", error=str(e), user_id=user_id, query=query)
        return ""
```

#### 3.2 修改 `_update_long_term_memory` 函数

```python
async def _update_long_term_memory(self, user_id: str, messages: list[dict], metadata: dict = None) -> None:
    """Update the long term memory."""
    # Skip memory if not using OpenAI (embeddings not configured)
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("sk-hupwt"):
        return
    
    try:
        memory = await self._long_term_memory()
        await memory.add(messages, user_id=str(user_id), metadata=metadata)
        logger.info("long_term_memory_updated_successfully", user_id=user_id)
    except Exception as e:
        logger.exception("failed_to_update_long_term_memory", user_id=user_id, error=str(e))
```

### 4. 环境变量配置 (`.env.development`)

```bash
# SiliconFlow Settings (Primary - Using DeepSeek V3.2)
SILICONFLOW_API_KEY=sk-your-siliconflow-api-key-here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL=Pro/deepseek-ai/DeepSeek-V3.2

# LLM Settings
DEFAULT_LLM_MODEL=siliconflow-deepseek-v3.2
DEFAULT_LLM_TEMPERATURE=0.2
MAX_TOKENS=2000
MAX_LLM_CALL_RETRIES=3

# DeepSeek Settings (Optional - as fallback)
DEEPSEEK_API_KEY=""
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# OpenAI Settings (填入硅基流动的 key 作为占位符，避免启动报错)
OPENAI_API_KEY=sk-your-siliconflow-api-key-here

# Long term memory Configuration (disabled - requires OpenAI embeddings)
# LONG_TERM_MEMORY_MODEL=siliconflow-deepseek-v3.2
# LONG_TERM_MEMORY_EMBEDDER_MODEL=text-embedding-3-small
# LONG_TERM_MEMORY_COLLECTION_NAME=longterm_memory
```

---

## 硅基流动支持的模型列表

| 模型名称 | 适用场景 | 价格档位 |
|---------|---------|---------|
| `Pro/deepseek-ai/DeepSeek-V3.2` | 代码生成、推理、通用对话 | 中等 |
| `Qwen/Qwen2.5-7B-Instruct` | 中文对话、通用任务 | 免费额度 |
| `Qwen/Qwen2.5-14B-Instruct` | 复杂任务、推理 | 较便宜 |
| `deepseek-ai/DeepSeek-V3` | 代码、数学、推理 | 便宜 |
| `meta-llama/Llama-3.1-8B-Instruct` | 英文任务 | 免费额度 |
| `01-ai/Yi-Lightning` | 实时对话 | 快速 |

> 完整模型列表请参考：https://cloud.siliconflow.cn/models

---

## 常见问题排查

### 问题 1: Token 计数错误

**错误信息：**
```
get_num_tokens_from_messages() is not presently implemented for model Pro/deepseek-ai/DeepSeek-V3.2
```

**解决方案：**
在 `ChatOpenAI` 初始化时添加 `tiktoken_model_name="gpt-4"` 参数。

### 问题 2: 长期记忆调用 OpenAI Embeddings 失败

**错误信息：**
```
Error code: 401 - Incorrect API key provided: sk-xxx. You can find your API key at https://platform.openai.com/account/api-keys
```

**解决方案：**
在 `_get_relevant_memory` 和 `_update_long_term_memory` 函数开头添加跳过逻辑。

### 问题 3: 容器重启后配置未生效

**原因：** Docker 容器需要重新构建才能加载新代码。

**解决方案：**
```bash
make docker-stop ENV=development
make docker-run-env ENV=development
```

### 问题 4: API 返回 401 错误

**检查项：**
1. 确认 `SILICONFLOW_API_KEY` 正确设置
2. 确认 `SILICONFLOW_BASE_URL` 为 `https://api.siliconflow.cn/v1`
3. 确认 `SILICONFLOW_MODEL` 模型名称正确

---

## 测试命令

```bash
# 健康检查
curl -s http://127.0.0.1:8000/health | python3 -m json.tool

# 聊天测试（需要有效的 JWT token）
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/chatbot/chat' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
  "messages": [
    {
      "role": "user",
      "content": "你好，请介绍一下自己"
    }
  ]
}'
```

---

## 后续优化建议

1. **启用硅基流动的 Embedding 服务**：如果硅基流动未来支持 Embedding API，可以恢复长期记忆功能。

2. **添加更多模型选项**：在 `LLMRegistry.LLMS` 中注册更多硅基流动支持的模型。

3. **配置模型降级策略**：当硅基流动 API 不可用时，自动切换到备用模型。

4. **监控和日志**：添加硅基流动 API 调用的监控指标。

---

## 获取硅基流动 API 密钥

1. 访问：https://cloud.siliconflow.cn/
2. 注册账号
3. 进入控制台 → API 密钥
4. 创建新密钥
5. 新用户有免费额度（约数百万 tokens）

---

## 参考链接

- 硅基流动官网：https://siliconflow.cn/
- 硅基流动 API 文档：https://docs.siliconflow.cn/
- 硅基流动模型列表：https://cloud.siliconflow.cn/models
- DeepSeek 官网：https://www.deepseek.com/
- LangChain ChatOpenAI 文档：https://python.langchain.com/docs/integrations/chat/openai

---

*文档版本：1.0 | 最后更新：2026-02-05*
