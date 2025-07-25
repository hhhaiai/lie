import requests
import time
from hashlib import sha256

# Free2GPT API封装类
class Free2GPTAPI:
    BASE_URL = "https://chat10.free2gpt.xyz"
    DEFAULT_MODEL = "gemini-1.5-pro"
    
    @staticmethod
    def generate_signature(timestamp: int, text: str, secret: str = "") -> str:
        """生成API请求签名"""
        message = f"{timestamp}:{text}:{secret}"
        return sha256(message.encode()).hexdigest()
    
    @classmethod
    def create_completion(
        cls,
        messages: list[dict],
        model: str = DEFAULT_MODEL,
        proxy: str = None,
    ) -> str:
        """
        发送请求到Free2GPT API并获取响应
        
        参数:
        messages - 消息列表, 格式: [{"role": "user", "content": "..."}]
        model - 使用的模型 (默认为gemini-1.5-pro)
        proxy - 代理设置 (可选)
        
        返回:
        API响应内容
        """
        # 准备请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": f"{cls.BASE_URL}/",
            "Origin": cls.BASE_URL,
        }
        
        # 准备请求数据
        timestamp = int(time.time() * 1000)  # 毫秒时间戳
        last_message = messages[-1]["content"]
        
        data = {
            "messages": messages,
            "time": timestamp,
            "pass": None,
            "sign": cls.generate_signature(timestamp, last_message)
        }
        
        # 设置代理
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        # 发送请求
        response = requests.post(
            url=f"{cls.BASE_URL}/api/generate",
            headers=headers,
            json=data,
            proxies=proxies,
            stream=True  # 启用流式响应
        )
        
        # 处理响应
        if response.status_code == 500 and "Quota exceeded" in response.text:
            raise RuntimeError("Rate limit reached: Quota exceeded")
        
        response.raise_for_status()  # 处理其他HTTP错误
        
        # 流式读取响应内容
        content = ""
        for chunk in response.iter_content(chunk_size=1024):
            content += chunk.decode(errors="ignore")
        
        return content

if __name__ == "__main__":
    # 使用示例
    try:
        # 1. 准备消息 - 对话历史（含最后一条消息）
        conversation = [
            {"role": "user", "content": "你好！"},
            {"role": "assistant", "content": "你好！有什么可以帮您的吗？"},
            {"role": "user", "content": "解释一下量子计算的基本原理"},
        ]
        
        # 2. 发送请求
        result = Free2GPTAPI.create_completion(
            messages=conversation,
            model="gemini-1.5-pro",  # 可选模型: gemini-1.5-pro, gemini-1.5-flash
            # proxy="http://user:pass@proxy:port"  # 如果需要代理
        )
        
        # 3. 处理结果
        print("API响应内容:")
        print(result)
        
    except requests.HTTPError as e:
        print(f"HTTP错误: {e.response.status_code}")
        print(f"响应内容: {e.response.text}")
    except Exception as e:
        print(f"请求失败: {str(e)}")