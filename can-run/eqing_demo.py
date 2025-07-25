import requests
import json
import time

def chat_completion(prompt, model="gpt-3.5-turbo", stream=True, on_stream=None):
    """发送聊天完成请求到OpenAI API
    
    Args:
        prompt (str): 用户提示内容
        model (str, optional): 模型名称。默认是 "gpt-3.5-turbo"
        stream (bool, optional): 是否启用流式响应。默认是 True
        on_stream (callable, optional): 流式响应的回调函数。每次接收到数据时会调用
    """
    headers = {
        "authority": "next.eqing.tech",
        "accept": "text/event-stream",
        "accept-language": "en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://next.eqing.tech",
        "plugins": "0",
        "pragma": "no-cache",
        "referer": "https://next.eqing.tech/",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"99\", \"Google Chrome\";v=\"115\", \"Chromium\";v=\"115\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "usesearch": "false",
        "x-requested-with": "XMLHttpRequest"
    }

    data = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": model,
        "stream": stream,
        "temperature": 0.5,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "top_p": 1
    }

    try:
        response = requests.post(
            url="https://next.eqing.tech/api/openai/v1/chat/completions",
            headers=headers,
            json=data,
            stream=stream
        )

        if response.status_code != 200:
            print(f"请求失败，状态码：{response.status_code}")
            print(f"错误信息：{response.text}")
            return None
        result = ""
        created = None
        object_type = None
        if stream :
            for line in response.iter_lines():
                if line:
                    # 解码字节数据为字符串
                    if isinstance(line, bytes):
                        line = line.decode('utf-8').strip()
                    if on_stream:
                        on_stream(line.decode('utf-8'))
                    # print("line:", line)
                    if line.startswith("data:"):
                        # print(line)
                        data_str = line[len("data:"):].strip()
                        if not data_str or data_str == "[DONE]":
                            continue
                        try:
                            data = json.loads(data_str)
                            # 提取第一个data行的元信息
                            if isinstance(data, dict) and not created:
                                created = data.get("created")
                                object_type = data.get("object")
                            
                            # 安全访问嵌套字段，确保是字典类型
                            if isinstance(data, dict):
                                # 检查是否存在choices字段且为列表
                                if "choices" in data and isinstance(data["choices"], list):
                                    for choice in data["choices"]:
                                        # 检查每个choice是否为字典且包含delta字段
                                        if isinstance(choice, dict) and "delta" in choice:
                                            delta = choice["delta"]
                                            # 确保delta是字典且包含content字段
                                            if isinstance(delta, dict) and "content" in delta:
                                                content = delta["content"]
                                                # 确保content是字符串类型
                                                if isinstance(content, str):
                                                    result += content
                        except json.JSONDecodeError:
                            continue
                    
        # 移除最后的广告信息
        if result and result.endswith("> provided by [EasyChat](https://site.eqing.tech/)"):
            result = result.rsplit('\n', 1)[0]  # 按最后一个换行符分割，取前半部分

        return result
        
    except Exception as e:
        print(f"请求发生错误：{str(e)}")
        return None

# 示例调用：
if __name__ == "__main__":
    for i  in range(100):
        print(f"第{i+1}次请求:")
        t1 = time.time()
        response = chat_completion(
            prompt="你好，你是什么模型？",  # 用户提示词
            model="gpt-3.5-turbo",  # 模型名称
            # on_stream=lambda data: print("流式响应:", data)  # 流式响应回调
        )
        t2 = time.time()
        print(f"耗时:{t2-t1}, 最终响应:{response}")


# gpt-4o-mini
# gpt-4o-mini-image-free
#
