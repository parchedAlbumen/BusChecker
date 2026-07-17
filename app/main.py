from fastapi import FastAPI, Request
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2
import app.bus as bus
import datetime
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
TTL = 60 

#for caching
cached_time = None
cached_feed = None 

#for rate limiting
rate_limit : dict[str, tuple[int, datetime.datetime]] = {}

app = FastAPI()

@app.get("/")
def root(req: Request):
    global rate_limit
    if (check_rate_limit(req.client.host, rate_limit)):
        print("okay bet u valid")
        return {"message": "okay bet u valid"}
    return {"message": "you not valid lil bro"}

@app.get("/stops/{stop_code}")
def get_stop(stop_code: str):
    global cached_time, cached_feed
    if not (is_ttl_good(cached_time)):
        response = requests.get(f"{BASE_URL}{API_KEY}")
        cached_feed = gtfs_realtime_pb2.FeedMessage()
        cached_feed.ParseFromString(response.content)
        cached_time = datetime.datetime.now().astimezone()
        print("i reached here using API REQ")
    else:
        print("i reached here using CACHING")

    info = bus.get_arrival(stop_code, cached_feed, STOPS, DIRECTIONS, DIRECTION_NAMES)
    if info is None: 
        return {"message": "doesn't exist lol"}
    else:
        return info
    
def is_ttl_good(time: datetime.datetime):
    if time is None:
        return False
    age = (datetime.datetime.now().astimezone() - time).total_seconds()
    return age < TTL #if age is bigger than TTL get a fresh api call, update cache 

def check_rate_limit(ip: str, rate_limiter: dict[str, tuple[int, datetime.datetime]]):
    if (rate_limiter[ip] is None): #if doesn't exist
        rate_limiter[ip] = (1, datetime.datetime.now().astimezone()) #count, time 
        return True
    count, time = rate_limiter[ip]
    if ((datetime.datetime.now().astimezone() - time).total_seconds() >= 120): #2 minutes
        rate_limiter[ip] = (1, datetime.datetime.now().astimezone()) #must reset
        return True
    else if ((count >= 10)): 
        print("CANT REQ MORE FOR NOW!")
        return False
    return True

# CLEAN CODE + CONTINUE WITH PROGRESS 
# figure out caching and rate limiting
# clean code 
# start pytest/testing codes, its starting to get big
