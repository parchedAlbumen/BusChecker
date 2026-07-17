from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2
import app.bus as bus
import datetime
import requests 
import os

load_dotenv()
# Static Data
STOPS = bus.load_stops("./static/stops.txt")
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
    if not check_rate_limit(req.client.host, rate_limit):
        raise HTTPException(status_code=429, detail=f"Error 429, Too many Request")
    return {"message": "you are good lil bro"}

@app.get("/stops/{stop_code}")
def get_stop(stop_code: str, req: Request):
    global cached_time, cached_feed
    if not check_rate_limit(req.client.host, rate_limit):
        raise HTTPException(status_code=429, detail=f"Error 429, Too many Request")

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
    
def is_ttl_good(time: datetime.datetime) -> bool:
    if time is None:
        return False
    age = (datetime.datetime.now().astimezone() - time).total_seconds()
    return age < TTL #if age is bigger than TTL get a fresh api call, update cache 

#settling with 20 times per 2 minutes rate limiting for now.
def check_rate_limit(ip: str, rate_limiter: dict[str, tuple[int, datetime.datetime]]) -> bool:
    if rate_limiter.get(ip) is None: #if doesn't exist
        print("adding ts")
        rate_limiter[ip] = (1, datetime.datetime.now().astimezone()) #count, time 
        return True
    
    if (datetime.datetime.now().astimezone() - rate_limiter[ip][1]).total_seconds() >= 120: #2 minutes
        rate_limiter[ip] = (1, datetime.datetime.now().astimezone()) #must reset
        print("We chillin")
        return True
    elif rate_limiter[ip][0] >= 20: 
        print("CANT REQ MORE FOR NOW!")
        print(f"resetting in: {120 - (datetime.datetime.now().astimezone() - rate_limiter[ip][1]).total_seconds()}")
        return False
    new_val= rate_limiter[ip][0] + 1
    rate_limiter[ip] = (new_val, rate_limiter[ip][1])
    return True

# CLEAN CODE + CONTINUE WITH PROGRESS 
# figure out caching and rate limiting
# clean code 
# start pytest/testing codes, its starting to get big


