from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import openai
from typing import Optional, List, Dict, Generator
from pydantic import BaseModel
import uvicorn

# 定义请求和响应模型
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    model: str = "gpt-4.1"
    stream: bool = False

class ModelListResponse(BaseModel):
    object: str = "list"
    data: List[Dict[str, Optional[str]]]

# 初始化服务
app = FastAPI(title="ChatGPT-like API Service")

class ChatService:
    def __init__(self, api_key: str, base_url: str):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.available_models = ["gpt-4.1", "gpt-4o-mini", "grok-3-mini", "deepseek-r1"]
    
    def list_models(self) -> ModelListResponse:
        return ModelListResponse(
            data=[{"id": model, "object": "model", "created": None, "owned_by": "system"} 
                 for model in self.available_models]
        )
    
    def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        stream: bool = False
    ) -> Generator[str, None, None]:
        try:
            if model not in self.available_models:
                raise ValueError(f"Model {model} is not available")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream
            )
            
            if not stream:
                content = response.choices[0].message.content
                yield content
            else:
                for chunk in response:
                    if chunk and chunk.choices:
                        delta = chunk.choices[0].delta
                        content = getattr(delta, "content", None)
                        if content:
                            yield content
                            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# 初始化聊天服务
chat_service = ChatService(
    api_key="sk-test",
    base_url="https://small-worm-50.deno.dev/api/v1"
)

# API端点
@app.get("/v1/models", response_model=ModelListResponse)
async def list_models():
    """获取可用模型列表"""
    return chat_service.list_models()

@app.post("/v1/chat/completions")
async def chat_completion(request: ChatCompletionRequest):
    """聊天补全接口，支持流式和非流式"""
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    if request.stream:
        def generate():
            for chunk in chat_service.create_completion(
                messages=messages,
                model=request.model,
                stream=True
            ):
                print(chunk)
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        gen = chat_service.create_completion(
            messages=messages,
            model=request.model,
            stream=False
        )
        content = next(gen)
        return {
            "object": "chat.completion",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                }
            }]
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
