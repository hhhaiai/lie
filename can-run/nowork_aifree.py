import requests
import json
import time
import hashlib
import random

def chat(prompt: str) -> str:
    """
    Sends a chat request to a randomly selected aifree.site endpoint,
    handling dynamic URL selection and request signing.

    Args:
        prompt (str): The user's message.

    Returns:
        str: The full text response from the API, or an error message.
    """
    # Randomly select a base URL from the list
    base_urls = [
        'https://s.aifree.site',
        'https://v.aifree.site',
        'https://al.aifree.site',
        'https://u4.aifree.site'
    ]
    chosen_base_url = random.choice(base_urls).strip('/')
    
    url = f"{chosen_base_url}/api/generate"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Referer": f"{chosen_base_url}/",
        "Origin": chosen_base_url,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Priority": "u=1, i"
    }

    # Generate Unix timestamp (seconds) and signature
    timestamp = int(time.time())
    sign_string = f"{timestamp}:{prompt}:"
    signature = hashlib.sha256(sign_string.encode('utf-8')).hexdigest()

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "time": timestamp,
        "pass": None,
        "sign": signature
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        # Assuming the response is text, similar to the previous example
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