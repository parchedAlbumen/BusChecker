from fastapi import FastAPI
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2
import app.bus as bus

import requests 
import os

load_dotenv()
# Static Data
STOPS = bus.load_stops("./static/stops.txt")
# ROUTES = bus.load_stops("./static/routes.txt")
DIRECTIONS = bus.load_directions("./static/directions.txt")
DIRECTION_NAMES = bus.load_direction_names("./static/direction_names_exceptions.txt")
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
    info = bus.get_arrival(stop_code, feed, STOPS, DIRECTIONS, DIRECTION_NAMES)
    if info is None: 
        return {"message": "doesn't exist lol"}
    else:
        return info
    


#CLEAN CODE + CONTINUE WITH PROGRESS 
# figure out schedule relationship
# figure out caching and rate limiting