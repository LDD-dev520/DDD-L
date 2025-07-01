#这东西是一个叫吕迪的山西大学的孩子花了三个星期完成的前端后端的项目，遇到很多困难，做出来其实很一般，但是我觉得我一直不断努力一会一定会更好的
#还是可以的，但是要花很多时间去理解代码，并且要自己写一个前端，但是这个项目还是可以的。
#这是一个启动Ollama API服务器的脚本
import uvicorn
import sys
import os

def main():
    """
    启动Ollama API服务器
    """
    host = "0.0.0.0"
    port = 8000
    
    print(f"启动服务器在 {host}:{port}...")
    
    # 添加当前目录到PYTHONPATH
    sys.path.insert(0, os.path.abspath("."))
    
    # 启动FastAPI服务器
    uvicorn.run("app.main:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    main()