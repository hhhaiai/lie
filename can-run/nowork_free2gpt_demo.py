import requests
import json
import time
import hashlib

def chat(prompt: str) -> str:
    """
    Sends a chat request to the free2gpt API, handling dynamic signing.

    Args:
        prompt (str): The user's message.

    Returns:
        str: The full text response from the API, or an error message.
    """
    url = "https://chat10.free2gpt.xyz/api/generate"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "text/plain;charset=UTF-8",
        "Referer": "https://chat10.free2gpt.xyz/",
        "Origin": "https://chat10.free2gpt.xyz",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Ch-Ua": "\"Chromium\";v=\"127\", \"Not)A;Brand\";v=\"99\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Linux\"",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Priority": "u=1, i"
    }

    # Generate dynamic timestamp and signature
    timestamp = int(time.time() * 1000)
    sign_string = f"{timestamp}:{prompt}:"
    signature = hashlib.sha256(sign_string.encode('utf-8')).hexdigest()

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "time": timestamp,
        "pass": None,
        "sign": signature
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        # The response is streamed as raw text, so we can return it directly.
        return response.text
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    user_prompt = "Hello World"
    print(f"> User: {user_prompt}\n")
    print("🤖 API Response:")
    response_text = chat(user_prompt)
    print(response_text) 