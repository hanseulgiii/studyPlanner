# test_openai.py
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()  # .env 불러오기

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2023-05-15",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

resp = client.chat.completions.create(
    model=deployment,
    messages=[{"role": "user", "content": "안녕, 지금 연결 잘 돼?"}]
)

print(resp.choices[0].message.content)
