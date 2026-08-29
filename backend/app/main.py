from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2
import app.bus as bus
import requests 
import os
import redis

load_dotenv()
# Static Data
STOPS = bus.load_stops("./static/stops.txt")
DIRECTIONS = bus.load_directions("./static/directions.txt")
DIRECTION_NAMES = bus.load_direction_names("./static/direction_names_exceptions.txt")
BASE_URL = "https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey="
API_KEY = os.getenv("MY_API_KEY")

#intializations
r = redis.Redis(host="localhost", port=6379) 
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root(req: Request):
    if not check_rate_limit(req.client.host):
        raise HTTPException(status_code=429, detail=f"Error 429, Too many Request")
    return {"message": "you are good lil bro"}

@app.get("/stops/{stop_code}")
def get_stop(stop_code: str, req: Request):
    if not check_rate_limit(req.client.host):
        raise HTTPException(status_code=429, detail=f"Error 429, Too many Request")
    
    feed = get_feed()
    info = bus.get_arrival(stop_code, feed, STOPS, DIRECTIONS, DIRECTION_NAMES)
    if info is None: 
        return {"message": "doesn't exist lol"}
    else:
        return info

@app.get("/debug/stop/{stop_code}")
def debug_raw_feed(stop_code: str):
    feed = get_feed()
    result = bus.get_raw_feed(stop_code, STOPS, feed)
    return result

#settling with 20 times per 2 minutes rate limiting for now.
def check_rate_limit(ip: str) -> bool:
    if r.get(f"address:{ip}") is None:
        print("adding")
        r.set(f"address:{ip}", 1, ex=120)
        return True

    if int(r.get(f"address:{ip}")) > 20:
        print("CANT REQ MORE FOR NOW!")
        return False

    r.incr(f"address:{ip}", 1)
    return True

# to get feed
def get_feed() -> gtfs_realtime_pb2.FeedMessage:
    cached = r.get("translink_info")
    if cached is None:
        try:
            response = requests.get(f"{BASE_URL}{API_KEY}", timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            raise HTTPException(status_code=503, detail="Translink is not working at the moment")

        gtfs_val = gtfs_realtime_pb2.FeedMessage()
        gtfs_val.ParseFromString(response.content)
        r.set("translink_info", gtfs_val.SerializeToString(), ex=60)
        print("i reached here using API REQ")
    else:
        print("i reached here using CACHING")

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(r.get("translink_info"))
    return feed

# start pytest/testing codes, its starting to get big


