import subprocess

# 请用 ollama list 确认这个模型名
MODEL_NAME = "deepseek-r1:7b"

def generate_response(prompt: str) -> str:
    cmd = ["ollama", "run", MODEL_NAME, prompt]
    try:
        # 明确把 stdout/stderr 都收集起来，指定 text=True 和 encoding='utf-8'
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",     # 强制用 utf-8 解码，不走 GBK
            timeout=60
        )
    except subprocess.TimeoutExpired:
        return "抱歉，调用 Ollama 超时。"
    except Exception as e:
        return f"抱歉，调用 Ollama 出错：{e}"

    if result.returncode != 0:
        # 把 stderr 原样返回，便于排查
        return f"抱歉，生成失败。\nOllama stderr:\n{result.stderr.strip()}"

    # 走到这里，一定有 stdout，直接 strip 并返回
    return result.stdout.strip()
