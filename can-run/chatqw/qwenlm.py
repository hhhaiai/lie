import json
import time
import uuid
import requests
from typing import Dict, List, Any, Optional

class QwenAPI:
    def __init__(self):
        self.QWEN_API_URL = 'https://chat.qwenlm.ai/api/chat/completions'
        self.QWEN_MODELS_URL = 'https://chat.qwenlm.ai/api/models'
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 1  # 1秒
        
        # 模型缓存
        self.cached_models = None
        self.cached_models_timestamp = 0
        self.CACHE_TTL = 60 * 60  # 缓存1小时

    def _sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def _fetch_with_retry(self, url: str, method: str = 'GET', headers: Dict = None, json_data: Dict = None) -> requests.Response:
        last_error = None
        
        for i in range(self.MAX_RETRIES):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data
                )

                if response.ok:
                    return response

                if response.status_code >= 500 or 'text/html' in response.headers.get('content-type', ''):
                    last_error = {
                        'status': response.status_code,
                        'content_type': response.headers.get('content-type'),
                        'response_text': response.text[:1000],
                        'headers': dict(response.headers)
                    }
                    
                    if i < self.MAX_RETRIES - 1:
                        self._sleep(self.RETRY_DELAY * (i + 1))
                        continue
                else:
                    last_error = {
                        'status': response.status_code,
                        'headers': dict(response.headers)
                    }
                    break
                    
            except Exception as e:
                last_error = str(e)
                if i < self.MAX_RETRIES - 1:
                    self._sleep(self.RETRY_DELAY * (i + 1))
                    continue

        raise Exception(json.dumps({
            'error': True,
            'message': 'All retry attempts failed',
            'last_error': last_error,
            'retries': self.MAX_RETRIES
        }))

    def get_models(self, auth_token: str) -> Dict:
        """获取可用的模型列表"""
        now = time.time()
        
        # 检查缓存
        if self.cached_models and now - self.cached_models_timestamp < self.CACHE_TTL:
            return self.cached_models

        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'authorization': f'Bearer {auth_token}',
            'bx-v': '2.5.0',
            'content-type': 'application/json',
            'origin': 'https://chat.qwenlm.ai',
            'referer': 'https://chat.qwenlm.ai/'
        }
        
        try:
            response = self._fetch_with_retry(
                url=self.QWEN_MODELS_URL,
                headers=headers
            )
            
            self.cached_models = response.json()
            self.cached_models_timestamp = now
            
            return self.cached_models
            
        except Exception as e:
            raise Exception(f"Failed to fetch models: {str(e)}")

    def chat_completion(
        self,
        auth_token: str,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        session_id: Optional[str] = None,
        chat_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Any:
        """发送聊天请求"""
        if not model:
            raise ValueError("Model parameter is required")

        # 如果未提供ID，则生成新的UUID
        session_id = session_id or str(uuid.uuid4())
        chat_id = chat_id or str(uuid.uuid4())
        request_id = request_id or str(uuid.uuid4())

        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'authorization': f'Bearer {auth_token}',
            'bx-v': '2.5.0',
            'content-type': 'application/json',
            'origin': 'https://chat.qwenlm.ai',
            'referer': 'https://chat.qwenlm.ai/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-request-id': request_id
        }

        request_data = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "session_id": session_id,
            "chat_id": chat_id,
            "id": request_id
        }

        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens

        try:
            response = requests.post(
                url=self.QWEN_API_URL,
                headers=headers,
                json=request_data,
                stream=stream
            )
            
            if not response.ok:
                raise Exception(f"Request failed with status {response.status_code}: {response.text}")
            
            if stream:
                return response.iter_lines()
            else:
                return response.json()
                
        except Exception as e:
            raise Exception(f"Chat completion failed: {str(e)}")

def process_stream_response(line: bytes, previous_content: str = "") -> tuple[Optional[str], Optional[str]]:
    """处理流式响应的单行数据
    返回: (增量内容, 完整内容)
    """
    try:
        if not line:
            return None, None
            
        line_text = line.decode('utf-8')
        if not line_text.startswith('data: '):
            return None, None
            
        data = json.loads(line_text[6:])
        if not data.get('choices'):
            return None, None
            
        delta = data['choices'][0].get('delta', {})
        current_content = delta.get('content', '')
        
        # 如果当前内容与之前的内容相同，返回空字符串作为增量
        if current_content == previous_content:
            return "", current_content
            
        # 如果当前内容包含之前的内容，只返回新增的部分
        if current_content.startswith(previous_content) and previous_content:
            increment = current_content[len(previous_content):]
            return increment, current_content
            
        return current_content, current_content
        
    except Exception as e:
        print(f"Error processing line: {e}")
        return None, None


def main():
    # 配置信息
    AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImI0YmUyZDBkLWM1MjAtNDVkNS1hODhmLTgwOWEwYzhhNjUxYiIsImV4cCI6MTczOTM2MjQ2NH0.h4hyDs--W8KHHk2B9JLYtjiC3yXx5k6TB2lkshJ5_pw"
    # 2.5 plus
    MODEL = "qwen-plus-latest"
    # qvq-72b-preview
    # qwq-32b-preview
    # qwen2.5-coder-32b-instruct
    # qwen-vl-max-latest

    
    # 初始化API客户端
    qwen = QwenAPI()
    
    try:
        # # 1. 获取可用模型列表
        # print("获取模型列表...")
        # models = qwen.get_models(AUTH_TOKEN)
        # print(f"可用模型: {json.dumps(models, ensure_ascii=False, indent=2)}\n")

        # 2. 发送聊天请求
        messages = [
            {"role": "user", "content": "你好，你是什么模型？"}
        ]
        
        # print("发送聊天请求...")
        # print("用户: 你好\n")
        # print("助手: ", end='', flush=True)
        
        # 使用流式响应
        stream_response = qwen.chat_completion(
            auth_token=AUTH_TOKEN,
            messages=messages,
            model=MODEL,
            stream=True
        )
        
        # 处理流式响应
        previous_content = ""
        result_content = ""
        for line in stream_response:
            increment, current_content = process_stream_response(line, previous_content)
            # print(f"increment:{increment}\ncurrent_content:{current_content}\n")
            if increment is not None:
                # print(increment, end='', flush=True)
                result_content += increment  # 累积所有增量内容
                previous_content = current_content
        
        print(f"\n结果:{result_content}\n")
                    
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main()