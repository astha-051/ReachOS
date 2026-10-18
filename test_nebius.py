import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("NEBIUS_BASE_URL"),
    api_key=os.getenv("NEBIUS_API_KEY")
)

print("Checking available Nemotron models...\n")

models = client.models.list()

nemotron_models = [
    model.id
    for model in models.data
    if "nemotron" in model.id.lower()
]

if not nemotron_models:
    print("No Nemotron models found.")
else:
    print("Nemotron models available:")
    for model in nemotron_models:
        print("-", model)