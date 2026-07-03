from dotenv import load_dotenv
from fastapi import HTTPException
import datetime
import csv

def get_arrival(stop_code, feed, stops):
    internal_code = get_internal_id(stop_code, stops)
    if internal_code is None:
        raise HTTPException(status_code=404, detail=f"Stop: {stop_code} does not exist")
    
    bus_infos = {
        "stop_code": stop_code,
        "stop_name": get_stop_name(stop_code, stops),
        "buses": []
    }

    for entity in feed.entity:
        for stop_time in entity.trip_update.stop_time_update:
            if stop_time.stop_id == internal_code:
                utc_time = datetime.datetime.fromtimestamp(stop_time.arrival.time, tz=datetime.timezone.utc)
                bus_infos["buses"].append({
                    "time": utc_time.astimezone(),
                    "predicted_arrival": find_time_diff(utc_time)
                    }
                )

    return bus_infos

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

def get_internal_id(stop_code, stops):
    stop = stops.get(stop_code) #check dictionary if key exist, returns none if not
    if stop is None:
        return None
    return stop.get("stop_id")

def get_stop_name(stop_code, stops):
    stop = stops.get(stop_code)
    if stop is None:
        return None
    return stop.get("stop_name")

def find_time_diff(bus_time):
    current_time = datetime.datetime.now(datetime.timezone.utc)
    return (bus_time - current_time)/60
