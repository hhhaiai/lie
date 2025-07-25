import requests
import json

class ChatGPTClient:
    def __init__(self, base_url, api_token, model="gpt-4", context=None, context_limit=10):
        self.base_url = base_url
        self.api_token = api_token
        self.model = model
        self.context = context if context is not None else []
        self.context_limit = context_limit

    def set_model(self, model):
        self.model = model

    def _update_context(self, message):
        if len(self.context) >= self.context_limit:
            self.context.pop(0)
        self.context.append(message)

    def _make_headers(self):
        if api_token is None:
            return {
                "Content-Type": "application/json"
            }
        else:
            return {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }

    def send_message(self, message, use_context=True, stream=False):
        if use_context:
            self._update_context({"role": "user", "content": message})
            prompt = self.context
        else:
            prompt = [{"role": "user", "content": message}]

        payload = {
            "model": self.model,  # Use the model set in the instance
            "messages": prompt,
            "stream": stream
        }

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers=self._make_headers(),
            data=json.dumps(payload),
            stream=stream
        )
        print(response.text)
        if stream:
            return self._handle_stream_response(response)
        else:
            return self._handle_response(response)

    def _handle_response(self, response):
        if response.status_code == 200:
            response_data = response.json()
            message_content = response_data['choices'][0]['message']['content']
            if self.context:
                self._update_context({"role": "assistant", "content": message_content})
            return message_content
        else:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

    def _handle_stream_response(self, response):
        if response.status_code == 200:
            collected_chunks = []
            for line in response.iter_lines():
                if line:
                    # Remove the prefix "data: " from each line
                    line_data = line.decode('utf-8').lstrip("data: ")
                    if line_data.strip() == "[DONE]":
                        break
                    if line_data:
                        try:
                            json_data = json.loads(line_data)
                            if 'choices' in json_data:
                                # 不带上下文, 单个词
                                temp_str=json_data['choices'][0]['delta'].get('content', '')
                                collected_chunks.append(temp_str)
                                # print(f"{temp_str}")
                        except json.JSONDecodeError:
                            continue
            message_content = ''.join(collected_chunks)
            if self.context:
                self._update_context({"role": "assistant", "content": message_content})
            return message_content
        else:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

    def clear_context(self):
        self.context = []

# Example usage
if __name__ == "__main__":
    base_url = "https://sanbo1200-duck2api.hf.space/hf"
    api_token = ""

    client = ChatGPTClient(base_url, api_token)

    # Set model
    client.set_model("gpt-4o-mini")

    # Sending a message without streaming
    response = client.send_message("Hello, how are you?", use_context=True, stream=False)
    print(f"Non-streamed response:\r\n {response}")
