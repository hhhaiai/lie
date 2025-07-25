"""
pip install fastapi uvicorn openai sse-starlette


openai 生产

uvicorn server:app --host 0.0.0.0 --port 7860



curl http://localhost:7860/v1/models

windows

curl -X POST http://localhost:7860/v1/chat/completions ^
-H "Content-Type: application/json" ^
-d "{\"messages\": [{\"role\": \"user\", \"content\": \"你好\"}], \"model\": \"gpt-4.1\", \"stream\": false}"


curl -X POST http://localhost:7860/v1/chat/completions ^
-H "Content-Type: application/json" ^
-d "{\"messages\": [{\"role\": \"user\", \"content\": \"介绍一下人工智能\"}], \"model\": \"gpt-4.1\", \"stream\": true}"


linux

curl -X POST http://localhost:7860/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "messages": [{"role": "user", "content": "你好"}],
  "model": "gpt-4.1",
  "stream": false
}'

curl -X POST http://localhost:7860/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "messages": [{"role": "user", "content": "你好"}],
  "model": "gpt-4.1",
  "stream": true
}'


"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse
import openai
import asyncio

app = FastAPI()

# 模型支持列表
MODELS = ["gpt-4.1", "gpt-4o-mini", "grok-3-mini", "deepseek-r1"]

# 构造 OpenAI 客户端
client = openai.OpenAI(
    api_key="sk-test",
    base_url="https://small-worm-50.deno.dev/api/v1"
)

@app.get("/v1/models")
async def list_models():
    return {"object": "list", "data": [{"id": model, "object": "model"} for model in MODELS]}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    try:
        payload = await request.json()
        model = payload.get("model")
        messages = payload.get("messages", [])
        stream = payload.get("stream", False)

        if model not in MODELS:
            return JSONResponse(status_code=400, content={"error": f"Model '{model}' not supported"})

        if not stream:
            # 非流式回复
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response  # 已经是 OpenAI 格式
        else:
            # 流式回复
            async def generate():
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True
                )
                for chunk in response:
                    if chunk and chunk.choices:
                        delta = chunk.choices[0].delta
                        content = getattr(delta, "content", None)
                        if content:
                            yield f'data: {{"choices":[{{"delta":{{"content":"{content}"}}}}]}}\n\n'
                yield 'data: [DONE]\n\n'

            return EventSourceResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
