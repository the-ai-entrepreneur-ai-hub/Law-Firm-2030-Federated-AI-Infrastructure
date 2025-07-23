import requests
import os

TOGETHER_API_KEY = "YOUR_API_KEY"

headers = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
}

data = {
    "model": "deepseek/deepseek-llm-67b-chat",
    "training_file": "file://C:/Users/Administrator/serveless-apps/Law Firm Vision 2030/law_firm_dataset.jsonl",
    "n_epochs": 3,
    "n_checkpoints": 1,
    "batch_size": 1,
    "learning_rate": 1e-5,
}

print("Script is running...")
response = requests.post("https://api.together.xyz/v1/fine-tunes", headers=headers, json=data)

print(response.text)