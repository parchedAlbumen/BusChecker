# from dotenv import load_dotenv
# import os 
import requests 

# load_dotenv()
# api_key = os.getenv("MY_API_KEY")
# print(api_key)

response = requests.get("https://api.github.com/users/octocat")
print(response.status_code, "\n")
data = response.json()
print(f"name: {data["login"]}\nuser id is {data["id"]} ")