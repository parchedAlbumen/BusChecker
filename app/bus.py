from dotenv import load_dotenv
import datetime
import csv

def get_arrival(stop_code, feed, stops):
    internal_code = get_internal_id(stop_code, stops)
    if internal_code is None:
        print(f"{stop_code} does not exist")
        return
    for entity in feed.entity:
        for stop_time in entity.trip_update.stop_time_update:
            if stop_time.stop_id == internal_code:
                print(f"{datetime.datetime.fromtimestamp(stop_time.arrival.time)} at stop: {stop_code}")
                print("at:", get_stop_name(stop_code, stops), "\n")

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
