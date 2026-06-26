from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2
import requests 
import os 
import datetime
import csv

load_dotenv()

def get_arrival(stop_code):
    internal_code = get_internal_id(stop_code)
    for entity in feed.entity:
        for stop_time in entity.trip_update.stop_time_update:
            if stop_time.stop_id == internal_code:
                print(f"{datetime.datetime.fromtimestamp(stop_time.arrival.time)} at stop: {stop_code}")
                print("at:", get_stop_name(stop_code), "\n")

def load_stops(filepath):
    stops = {}
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            stops[row["stop_code"]] = {
                "stop_id": row["stop_id"],
                "stop_name": row["stop_name"]
            }
    return stops

def get_internal_id(stop_code):
    return STOPS.get(stop_code).get("stop_id")

def get_stop_name(stop_code):
    return STOPS.get(stop_code).get("stop_name")

# Static Data
STOPS = load_stops("./static/stops.txt")
BASE_URL = "https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey="
API_KEY = os.getenv("MY_API_KEY")

#try  (wait why is it not recommending the thing)
feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get(f"{BASE_URL}{API_KEY}")
feed.ParseFromString(response.content)

get_arrival("51139")

