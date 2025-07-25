import requests
import time
import hashlib
import random
from typing import List, Dict, Any

class FreeGptAPI:
    """FreeGpt API客户端封装类"""
    
    # 定义常量
    DOMAINS = [
        "https://s.aifree.site",
        "https://v.aifree.site",
        "https://al.aifree.site",
        "https://u4.aifree.site"
    ]
    RATE_LIMIT_ERROR_MESSAGE = "当前地区当日额度已消耗完"
    DEFAULT_MODEL = 'gemini-1.5-pro'
    MODELS = [DEFAULT_MODEL, 'gemini-1.5-flash']
    
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    
    @staticmethod
    def generate_signature(timestamp: int, message: str, secret: str = "") -> str:
        """生成API签名 (SHA256)"""
        data = f"{timestamp}:{message}:{secret}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = DEFAULT_MODEL,
        proxy: str = None,
        timeout: int = 120,
        stream: bool = False,
        **kwargs: Any
    ) -> str:
        """
        发送请求到FreeGpt API
        
        参数:
        - messages: 消息列表, 格式: [{"role": "...", "content": "..."}, ...]
        - model: 使用的模型 (gemini-1.5-pro 或 gemini-1.5-flash)
        - proxy: 代理设置 (可选)
        - timeout: 请求超时时间 (秒)
        - stream: 是否流式接收响应 (默认为False)
        
        返回:
        API响应内容 (字符串)
        """
        # 1. 验证模型
        if model not in self.MODELS:
            raise ValueError(f"无效模型: {model}. 有效模型: {', '.join(self.MODELS)}")
        
        # 2. 准备请求数据
        prompt = messages[-1]["content"]
        timestamp = int(time.time())
        
        data = {
            "messages": messages,
            "time": timestamp,
            "pass": None,
            "sign": self.generate_signature(timestamp, prompt)
        }
        
        # 3. 随机选择一个域名
        domain = random.choice(self.DOMAINS)
        url = f"{domain}/api/generate"
        
        # 4. 设置请求头
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": domain
        }
        
        # 5. 设置代理
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        # 6. 发送请求
        try:
            response = requests.post(
                url,
                json=data,
                headers=headers,
                proxies=proxies,
                timeout=timeout,
                stream=stream
            )
            
            # 7. 检查响应状态
            response.raise_for_status()
            
            # 8. 处理速率限制错误
            content = ""
            if stream:
                for chunk in response.iter_content(chunk_size=1024):
                    chunk_decoded = chunk.decode(errors="ignore")
                    if chunk_decoded == self.RATE_LIMIT_ERROR_MESSAGE:
                        raise RuntimeError("Rate limit reached: 当前地区当日额度已消耗完")
                    content += chunk_decoded
            else:
                content = response.text
                if self.RATE_LIMIT_ERROR_MESSAGE in content:
                    raise RuntimeError("Rate limit reached: 当前地区当日额度已消耗完")
            
            return content
        
        except requests.exceptions.HTTPError as e:
            # 处理HTTP错误
            status_code = e.response.status_code
            error_msg = f"HTTP错误: {status_code}"
            if e.response.text:
                error_msg += f" | 响应内容: {e.response.text[:500]}"
            raise RuntimeError(error_msg)
        
        except Exception as e:
            # 处理其他错误
            raise RuntimeError(f"请求失败: {str(e)}")

# 使用示例
if __name__ == "__main__":
    # 1. 创建API客户端
    api = FreeGptAPI()
    
    # 2. 准备消息对话 (至少需要最后一条消息)
    conversation = [
        {"role": "system", "content": "你是一个乐于助人的AI助手"},
        {"role": "user", "content": "你好！"},
        {"role": "assistant", "content": "你好！有什么我可以帮助您的吗？"},
        {"role": "user", "content": "什么是神经网络？"}
    ]
    
    print("开始发送API请求...")
    try:
        # 3. 发送请求并获取响应 (默认使用流式响应)
        response = api.create_completion(
            messages=conversation,
            model="gemini-1.5-pro",
            # proxy="http://127.0.0.1:8080"  # 如果需要代理
            stream=True
        )
        
        # 4. 输出结果
        print("\nAPI响应内容:")
        print(response)
        
    except Exception as e:
        print(f"\n发生错误: {str(e)}")