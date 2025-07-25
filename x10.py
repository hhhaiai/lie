import openai

client = openai.OpenAI(
    api_key="sk-test",
    base_url="https://small-worm-50.deno.dev/api/v1"
)

def chat_with_gpt(prompt, model="gpt-4.1",stream=False):
    try:
        if not stream:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.choices[0].message.content
            return answer
        else:
            # 流式输出
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            full_content = ""
            for chunk in response:
                # 新版 API: chunk.choices[0].delta.content 可能为 None
                # print("1 chunk:", chunk)
                if chunk and chunk.choices:
                    delta = chunk.choices[0].delta
                    # print("2 delta:", delta)
                    content = getattr(delta, "content", None)
                    if content:
                        # print(content, end="", flush=True)
                        full_content += content
            print()  # 换行
            return full_content

    except Exception as e:
        print(f"请求出错: {e}")
        return None


models=["gpt-4.1","gpt-4o-mini","grok-3-mini","deepseek-r1"]
for model in models:
    print("========================================================", f"============================使用模型: {model}============================","========================================================")
    # 测试普通回复
    prompt = "请介绍下人工智能,人工智能的基础是什么？"
    result = chat_with_gpt(prompt,model=model)
    if result:
        print(result)

    # 测试流式回复
    print("==========================================\r\n流式回复：")
    result = chat_with_gpt(prompt,model=model, stream=True)
    if result:
        print(result)