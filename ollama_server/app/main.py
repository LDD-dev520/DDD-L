from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
from app.ollama_client import generate_response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 添加CORS中间件以允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 新版 Chroma 初始化：PersistentClient
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("kb_store")

# 初始化 embedding 模型
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# 请求模型
class ChatRequest(BaseModel):
    user_id: str
    query: str

class KnowledgeRequest(BaseModel):
    query: str
    limit: int = 3

@app.get("/")
async def root():
    return {"message": "欢迎使用智能服务API"}

@app.get("/api/status")
async def get_status():
    return {
        "success": True,
        "status": "running",
        "model": "deepseek-r1:7b",
        "datetime": "",  # 可以添加服务器时间
    }

@app.post("/chat")
async def chat(req: ChatRequest):
    # 生成 query embedding
    q_emb = embed_model.encode([req.query]).tolist()[0]
    
    # 检索最近的知识片段
    result = collection.query(query_embeddings=[q_emb], n_results=3)
    
    # 打印检索结果
    print("Raw query result:", result)

    # 安全获取检索到的文档
    if result["documents"] and result["documents"][0]:
        docs = result["documents"][0]
    else:
        docs = []

    print("Docs to use as context:", docs)

    context = "\n".join(docs) if docs else "无相关背景知识"

    # 构建 prompt
    prompt = f"""
以下是背景知识：
{context}

请根据背景知识回答：
{req.query}
"""
    # 调用 Ollama 生成回答
    answer = generate_response(prompt)
    return {"answer": answer, "docs": docs}

@app.post("/api/chat/ask")
async def api_chat(req: ChatRequest):
    # 复用现有的chat功能
    result = await chat(req)
    
    # 返回适配前端的格式
    return {
        "success": True,
        "answer": result["answer"],
        "used_knowledge": len(result.get("docs", [])) > 0,
        "knowledge_items": result.get("docs", []),
        "processing_time": 0  # 可以添加处理时间计算
    }

@app.post("/api/knowledge/search")
async def search_knowledge(req: KnowledgeRequest):
    # 生成 query embedding
    q_emb = embed_model.encode([req.query]).tolist()[0]
    
    # 检索知识片段
    result = collection.query(query_embeddings=[q_emb], n_results=req.limit)
    
    # 构造返回结果
    items = []
    if result["documents"] and result["documents"][0]:
        for i, doc in enumerate(result["documents"][0]):
            items.append({
                "id": result["ids"][0][i] if result["ids"] and result["ids"][0] else f"item_{i}",
                "content": doc,
                "metadata": result["metadatas"][0][i] if result["metadatas"] and result["metadatas"][0] else {}
            })
    
    return {
        "success": True,
        "results": items,
        "count": len(items)
    }

@app.get("/api/knowledge/stats")
async def get_knowledge_stats():
    # 获取知识库统计信息
    count = collection.count()
    
    return {
        "success": True,
        "count": count,
        "domains": []  # 可以添加领域分类统计
    }


