"""

curl -X POST "https://chat9.fastgpt.me/api/openai/v1/chat/completions" \
     -H "authority: chat9.fastgpt.me" \
     -H "accept: text/event-stream" \
     -H "accept-language: en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3" \
     -H "cache-control: no-cache" \
     -H "content-type: application/json" \
     -H "origin: https://chat9.fastgpt.me" \
     -H "plugins: 0" \
     -H "pragma: no-cache" \
     -H "referer: https://chat9.fastgpt.me/" \
     -H "sec-ch-ua: \"Not/A)Brand\";v=\"99\", \"Google Chrome\";v=\"115\", \"Chromium\";v=\"115\"" \
     -H "sec-ch-ua-mobile: ?0" \
     -H "sec-ch-ua-platform: \"macOS\"" \
     -H "sec-fetch-dest: empty" \
     -H "sec-fetch-mode: cors" \
     -H "sec-fetch-site: same-origin" \
     -H "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36" \
     -H "usesearch: false" \
     -H "x-requested-with: XMLHttpRequest" \
     --data-raw '{
       "messages": [
         {
           "role": "user",
           "content": "Hello World"
         }
       ],
       "model": "gpt-3.5-turbo",
       "stream": true,
       "temperature": 0.5,
       "presence_penalty": 0,
       "frequency_penalty": 0,
       "top_p": 1
     }'

"""


import requests
import json

def chat(prompt: str, model: str = "gpt-3.5-turbo", stream: bool = True) -> str:
    """
    Sends a chat request based on the provided cURL command.

    Args:
        prompt (str): The user's message.
        model (str, optional): The model to use. Defaults to "gpt-3.5-turbo".
        stream (bool, optional): Whether to stream the response. Defaults to True.

    Returns:
        str: The full response from the API.
    """
    url = "https://chat9.fastgpt.me/api/openai/v1/chat/completions"
    
    headers = {
        "authority": "chat9.fastgpt.me",
        "accept": "text/event-stream",
        "accept-language": "en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://chat9.fastgpt.me",
        "plugins": "0",
        "pragma": "no-cache",
        "referer": "https://chat9.fastgpt.me/",
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

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "model": model,
        "stream": stream,
        "temperature": 0.5,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "top_p": 1
    }

    full_response = ""
    try:
        with requests.post(url, headers=headers, json=payload, stream=stream) as response:
            response.raise_for_status()
            
            if stream:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data:'):
                            json_str = decoded_line[len('data:'):].strip()
                            if json_str == "[DONE]":
                                break
                            try:
                                data = json.loads(json_str)
                                choices = data.get("choices", [])
                                if choices and "delta" in choices[0] and "content" in choices[0]["delta"]:
                                    full_response += choices[0]["delta"]["content"]
                            except json.JSONDecodeError:
                                # In case of malformed JSON, just continue
                                continue
            else:
                # Handle non-streamed response
                data = response.json()
                full_response = data.get("choices", [{}])[0].get("message", {}).get("content", "")

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"
    
    return full_response

if __name__ == "__main__":
    user_prompt = "Hello World"
    print(f"> User: {user_prompt}\n")
    print("🤖 API Response:")
    response_text = chat(user_prompt)
    print(response_text) 