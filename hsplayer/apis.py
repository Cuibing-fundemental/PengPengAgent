from openai import OpenAI
import os

def generate(prompt: str, model:str = "local", **kwargs):
    print(f"正在使用模型 '{model}' 生成响应...")
    if "qwen" in model:
        return qwen_generate(prompt, model=model, **kwargs)
    else:
        return local_generate(prompt, **kwargs)

def qwen_generate(prompt: str, model: str = "qwen3-flash", **kwargs):
    client = OpenAI(
        api_key=os.getenv("QWEN_API"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    response_format = {"type": "json_object"}
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=8192,
        n=1,
        stream=True,
        response_format=response_format,
        temperature=0.75,
        stream_options={"include_usage": True},
    )

    full_content = ""
    for chunk in response:
        if chunk.choices and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if delta.content:
                content = delta.content
                full_content += content
                yield content

def local_generate(prompt: str, **kwargs):
    client = OpenAI(
        api_key="CS500020",
        base_url="http://10.176.50.208:20031/v1",
    )
    response_format = {"type": "json_object"}
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        response_format=response_format,
        model="Qwen3-30B-A3B-Instruct-2507",
        max_tokens=8192,
        n=1,
        stream=True,
        temperature=0.75,
    )

    full_content = ""
    for chunk in response:
        if chunk.choices and len(chunk.choices) > 0:
            delta = chunk.choices[0].delta
            if delta.content:
                content = delta.content
                full_content += content
                yield content

