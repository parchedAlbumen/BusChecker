from fastapi import FastAPI
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2
import app.bus as bus

import requests 
import os

load_dotenv()
# Static Data
STOPS = bus.load_stops("./static/stops.txt")
BASE_URL = "https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey="
API_KEY = os.getenv("MY_API_KEY")

app = FastAPI()

@app.get("/")
def root():
    return {"message": "hello"}

@app.get("/stops/{stop_code}")
def get_stop(stop_code: str):
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get(f"{BASE_URL}{API_KEY}")
    feed.ParseFromString(response.content)
    bus.get_arrival(stop_code, feed, STOPS)


#fix the return here, fix the return json file, continue @ wiring bus into fastAPI