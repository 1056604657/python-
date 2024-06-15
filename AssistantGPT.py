import openai
from loguru import logger
from config import *
import httpx
import requests
from typing import List, Dict, Union
import json
import logging
class AssistantGPT:
    def __init__(self): 
        import os
        from typing import List
        os.environ["OPENAI_API_BASE"] = 'https://api.xty.app/v1'
        os.environ["OPENAI_API_KEY"] = 'sk-A2dkpolqc9XtWx6xC36e2498A24748489d3348Ef1a23395a'
        self.client = openai.OpenAI(
            base_url="https://api.xty.app/v1",
            api_key="sk-A2dkpolqc9XtWx6xC36e2498A24748489d3348Ef1a23395a",
            http_client=httpx.Client(
                base_url="https://api.xty.app/v1",
                follow_redirects=True,
            ),
        )

    def get_completion(
            self,
            messages,
            model=DEFAULT_MODEL,
            max_tokens=2000,
            temperature=0.7,
            stream=False,
    ):
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        elif not isinstance(messages, list):
            return "无效的 'messages' 类型。它应该是一个字符串或消息列表。"

        response = self.client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            stream=stream,
            temperature=temperature,
        )

        if stream:
            return response

        logger.success(f"非流式输出 | total_tokens: {response.usage.total_tokens} "
                       f"= prompt_tokens:{response.usage.prompt_tokens}"
                       f"+ completion_tokens: {response.usage.completion_tokens}")
        return response.choices[0].message.content

    def get_embeddings(self, input):
        response = self.client.embeddings.create(
            input=input,
            model='text-embedding-ada-002',
        )
        embeddings = [data.embedding for data in response.data]
        return embeddings

    def get_completion3(
        self,
        messages: Union[str, List[Dict[str, str]]],
        api_url: str = "http://10.10.10.15:11434/api/generate",
        #model: str = "qwen:110b",
        model: str = "wangshenzhi/llama3-8b-chinese-chat-ollama-q8:latest",
        
        stream: bool = False
    ) -> Union[str, List[Dict]]:

        if isinstance(messages, str):
            prompt_string = messages
        elif isinstance(messages, list) and all(isinstance(msg, dict) for msg in messages):
            prompt_string = "\n".join(msg.get("content", "") for msg in messages if msg.get("role") == "user")
        else:
            return "无效的 'messages' 类型。它应该是一个字符串或消息字典列表。"
        headers = {'Content-Type': 'application/json'}
        data = {
            "model": model,
            "prompt": prompt_string.strip()
        }

        try:
            if stream:
                responses = []
                session = requests.Session()
                with session.post(api_url, headers=headers, json=data, stream=True) as resp:
                    for line in resp.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            try:
                                chunk = json.loads(decoded_line)
                                responses.append(chunk)
                                if 'done' in chunk and chunk['done']:
                                    break
                                if 'response' in chunk:
                                    yield chunk['response']
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON: {e}", file=sys.stderr)
                return responses
            else:
                response = requests.post(api_url, headers=headers, json=data)
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    response_lines = response.text.strip().split("\n")
                    response_data = [json.loads(line) for line in response_lines]
                    combined_response = "".join(chunk.get('response', '') for chunk in response_data)
                    return combined_response
                else:
                    return response.text

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
if __name__ == "__main__":
    gpt = AssistantGPT()
    prompt = '你好'
    bot_response = gpt.get_completion(prompt, stream=True)
    completion = ""
    for character in bot_response:
        character_content = character.choices[0].delta.content
        if character_content is not None:
            completion += character_content
        else:
            from file_processor_helper import FileProcessorHelper
            prompt_tokens = FileProcessorHelper.tiktoken_len(prompt)
            completion_tokens = FileProcessorHelper.tiktoken_len(completion)
            total_tokens = prompt_tokens + completion_tokens
            logger.success(f"流式输出 | bot_response: {completion}")
            logger.success(f"流式输出 | total_tokens: {total_tokens} "
                           f"= prompt_tokens:{prompt_tokens} + completion_tokens: {completion_tokens}")

