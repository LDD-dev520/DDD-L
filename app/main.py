from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
from app.ollama_client import generate_response

app = FastAPI()

# 新版 Chroma 初始化：PersistentClient
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("kb_store")

# 初始化 embedding 模型
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# 请求模型
class ChatRequest(BaseModel):
    user_id: str
    query: str

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
    return {"answer": answer}


