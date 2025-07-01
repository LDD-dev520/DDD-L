 #这东西是一个叫吕迪的山西大学的孩子花了三个星期完成的前端后端的项目，遇到很多困难，做出来其实很一般，但是我觉得我一直不断努力一会一定会更好的
 # Ollama 服务器

这是一个基于FastAPI的Ollama服务器，提供知识库检索增强的AI聊天功能。

## 安装

1. 确保安装了Python 3.8+
2. 安装依赖:
   ```
   pip install -r requirements.txt
   ```
3. 确保已安装并启动Ollama (https://ollama.com/)
4. 确保已拉取模型: `ollama pull deepseek-r1:7b`

## 启动服务器

运行以下命令启动服务器:

```bash
python start_server.py
```

服务器将在 http://127.0.0.1:8000 上运行。

## API接口

### 1. 状态检查
- **URL**: `/api/status`
- **方法**: GET
- **返回示例**:
  ```json
  {
    "success": true,
    "status": "running",
    "model": "deepseek-r1:7b",
    "datetime": ""
  }
  ```

### 2. 聊天
- **URL**: `/api/chat/ask`
- **方法**: POST
- **请求体**:
  ```json
  {
    "user_id": "user123",
    "query": "什么是向量数据库?"
  }
  ```
- **返回示例**:
  ```json
  {
    "success": true,
    "answer": "向量数据库是一种特殊的数据库...",
    "used_knowledge": true,
    "knowledge_items": ["向量数据库是..."],
    "processing_time": 0
  }
  ```

### 3. 知识库搜索
- **URL**: `/api/knowledge/search`
- **方法**: POST
- **请求体**:
  ```json
  {
    "query": "向量数据库",
    "limit": 5
  }
  ```
- **返回示例**:
  ```json
  {
    "success": true,
    "results": [
      {
        "id": "doc1_0",
        "content": "向量数据库是...",
        "metadata": {"source": "doc1.txt", "para_id": 0}
      }
    ],
    "count": 1
  }
  ```

### 4. 知识库统计
- **URL**: `/api/knowledge/stats`
- **方法**: GET
- **返回示例**:
  ```json
  {
    "success": true,
    "count": 42,
    "domains": []
  }
  ```

## 前端集成

修改zhinengapp中的`utils/api.js`文件中的`API_BASE_URL`变量，指向此服务器的地址（例如`http://127.0.0.1:8000`）。需要根据你自己的进行修改

前端已经配置好通过适配的API接口与此服务器通信。