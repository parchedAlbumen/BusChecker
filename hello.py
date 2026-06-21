from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2
import requests 
import os 
import datetime

load_dotenv()
api_key = os.getenv("MY_API_KEY")

# response = requests.get("https://api.github.com/users/octocat")
# print(response.status_code, "\n")
# data = response.json()
# print(f"name: {data["login"]}\nuser id is {data["id"]} ")

base_url = "https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey="
scheduled_arrival = 4
predicted_arrival = 5
difference = predicted_arrival - scheduled_arrival # if difference > 0, then ahead, if difference < 0, then behind, if difference = 0, then right on time

#try  (wait why is it not recommending the thing)
feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get(f"{base_url}{api_key}")
feed.ParseFromString(response.content)

for entity in feed.entity:
    for stop_time in entity.trip_update.stop_time_update:
        if stop_time.stop_id == "9147":
            print(datetime.datetime.fromtimestamp(stop_time.arrival.time))
            print(stop_time.stop_id)
            print("got here")
    

