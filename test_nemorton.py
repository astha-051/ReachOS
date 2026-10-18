import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("NEBIUS_BASE_URL"),
    api_key=os.getenv("NEBIUS_API_KEY")
)

MODEL = "nvidia/nemotron-3-super-120b-a12b"

print(f"Testing model: {MODEL}\n")

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": "In one sentence, what is a qualified sales lead?"
        }
    ],
    max_tokens=300
)

print("========== RAW RESPONSE ==========")
print(response)

print("\n========== CHOICES ==========")
print("Number of choices:", len(response.choices))

choice = response.choices[0]

print("\nFinish reason:")
print(choice.finish_reason)

print("\nMessage:")
print(choice.message)

print("\nMessage content:")
print(repr(choice.message.content))