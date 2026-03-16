from openai import OpenAI

def generate(prompt: str, json_mode: bool = True, **kwargs):
    client = OpenAI(
        api_key="CS500020",
        base_url="http://10.176.50.208:20031/v1",
    )
    response_format = {"type": "text"}
    if json_mode:
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

