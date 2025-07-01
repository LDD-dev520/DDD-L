import chromadb
from sentence_transformers import SentenceTransformer
import os

# 新版 Chroma 初始化
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("kb_store")

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def index_docs():
    for fname in os.listdir("./docs"):
        with open(f"./docs/{fname}", encoding="utf-8") as f:
            text = f.read()
        for i, para in enumerate(text.split("\n\n")):
            para = para.strip()
            if len(para) < 10:
                continue
            emb = embed_model.encode(para).tolist()
            collection.add(
                ids=[f"{fname}_{i}"],
                documents=[para],
                embeddings=[emb],
                metadatas=[{"source": fname, "para_id": i}]
            )
    print("知识库索引完成！")

if __name__ == "__main__":
    index_docs()



