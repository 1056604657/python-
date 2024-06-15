
import os
from dotenv import load_dotenv, find_dotenv
import os
from typing import List
os.environ["OPENAI_API_BASE"] = 'https://api.xty.app/v1'
os.environ["OPENAI_API_KEY"] = 'sk-A2dkpolqc9XtWx6xC36e2498A24748489d3348Ef1a23395a'

MODELS = [
    "llama3-8b-chines",
    "gpt-3.5-turbo-1106", # 最新的 GPT-3.5 Turbo 模型，具有改进的指令遵循、JSON 模式、可重现输出、并行函数调用等。最多返回 4,096 个输出标记。
    "gpt-3.5-turbo",  # 当前指向 gpt-3.5-turbo-0613 。自 2023 年 12 月 11  日开始指向gpt-3.5-turbo-1106。
    "gpt-3.5-turbo-16k",  # 当前指向 gpt-3.5-turbo-0613 。将指向gpt-3.5-turbo-1106 2023 年 12 月 11 日开始。
]
#DEFAULT_MODEL = MODELS[-2]
DEFAULT_MODEL = MODELS[0]

MODEL_TO_MAX_TOKENS = {
    "llama3-8b-chines": 4096,
    "gpt-3.5-turbo-1106": 4096,
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16385,
}

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

DEFAULT_MAX_TOKENS = 4000