from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2
import app.bus as bus
import datetime
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

#redis
r = redis.Redis(host="localhost", port=6379) 

# #for rate limiting
# rate_limit : dict[str, tuple[int, datetime.datetime]] = {}

app = FastAPI()

@app.get("/")
def root(req: Request):
    if not check_rate_limit(req.client.host):
        raise HTTPException(status_code=429, detail=f"Error 429, Too many Request")
    return {"message": "you are good lil bro"}

@app.get("/stops/{stop_code}")
def get_stop(stop_code: str, req: Request):
    if not check_rate_limit(req.client.host):
        raise HTTPException(status_code=429, detail=f"Error 429, Too many Request")

    if r.get("translink_info") is None: 
        try:
            response = requests.get(f"{BASE_URL}{API_KEY}", timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            raise HTTPException(status_code=503, detail="Translink is not working at the moment") 
        
        #try to understand this part a little bit better, i kind of dont understand how the protobuf works either, please at least get the gist of it
        gtfs_val = gtfs_realtime_pb2.FeedMessage()
        gtfs_val.ParseFromString(response.content)
        gtfs_byte = gtfs_val.SerializeToString()
        r.set("translink_info", gtfs_byte, ex=60)

        print("i reached here using API REQ")
    else:
        print("i reached here using CACHING")

    feed = gtfs_realtime_pb2.FeedMessage() 
    feed.ParseFromString(r.get("translink_info"))
    info = bus.get_arrival(stop_code, feed, STOPS, DIRECTIONS, DIRECTION_NAMES)
    if info is None: 
        return {"message": "doesn't exist lol"}
    else:
        return info
    
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

# CLEAN CODE + CONTINUE WITH PROGRESS 
# figure out caching and rate limiting
# clean code 
# start pytest/testing codes, its starting to get big


