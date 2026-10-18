import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

client = TavilyClient(api_key=api_key)

response = client.search(
    query="latest AI automation trends 2026",
    max_results=3
)

print("\nTavily search successful!\n")

for result in response["results"]:
    print("TITLE:", result["title"])
    print("URL:", result["url"])
    print()