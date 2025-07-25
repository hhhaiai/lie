from __future__ import annotations
import asyncio
import json
import random
import string
from typing import Optional
from aiohttp import ClientSession


def generate_machine_id() -> str:
    """Generates random machine id"""
    part1 = "".join(random.choices(string.digits, k=16))
    part2 = "".join(random.choices(string.digits + ".", k=25))
    return f"{part1}.{part2}"


async def chat(
    prompt: str,
    model: str = 'gpt-4o-mini-2024-07-18',
    proxy: Optional[str] = None
) -> str:
    """
    Make an asynchronous request to the Chatai stream API.
    
    Args:
        prompt: The user's prompt
        model: Model to use
        proxy: Optional proxy URL
        
    Returns:
        Full response text
    """
    api_endpoint = "https://chatai.aritek.app/stream"
    headers = {
        'Accept': 'text/event-stream',
        'Content-Type': 'application/json',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-G935F Build/N2G48H)',
        'Host': 'chatai.aritek.app',
        'Connection': 'Keep-Alive',
    }

    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": prompt}
    ]
    
    machine_id = generate_machine_id()
    c_token = "eyJzdWIiOiIyMzQyZmczNHJ0MzR0MzQiLCJuYW1lIjoiSm9objM0NTM0NT"
    
    payload = {
        "machineId": machine_id,
        "msg": messages,
        "token": c_token,
        "type": 0,
        "model": model  # Pass model to payload
    }

    result = ""
    async with ClientSession(headers=headers) as session:
        try:
            async with session.post(
                api_endpoint,
                json=payload,
                proxy=proxy
            ) as response:
                response.raise_for_status()
                
                async for line_bytes in response.content:
                    if not line_bytes:
                        continue
                        
                    line = line_bytes.decode('utf-8').strip()
                    
                    if not line or line.startswith(": ping"):
                        continue
                        
                    if line.startswith("data:"):
                        data_str = line[len("data:"):].strip()
                        
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            
                            for choice in data.get("choices", []):
                                delta = choice.get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    result += content
                        except json.JSONDecodeError:
                            print(f"⚠️ Failed to parse JSON: {data_str}")
                            continue
                        except Exception as e:
                            print(f"⚠️ Error processing chunk: {e}")
                            continue
        except Exception as e:
            print(f"🚨 API request failed: {e}")
            raise
    
    return result

async def main():
    """Main function to test the chat function."""
    prompt = "Explain quantum computing in simple terms. Please reply in Chinese."
    
    print("🚀 Starting chat request...")
    try:
        response = await chat(prompt)
        print("\n💬 Full Response:")
        print(response)
    except Exception as e:
        print(f"🔴 Error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())