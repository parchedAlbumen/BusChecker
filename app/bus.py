from fastapi import HTTPException
import datetime
import csv

def get_arrival(stop_code, feed, stops, directions, dict_names):
    stop = stops.get(stop_code)
    internal_code = get_internal_id(stop)
    if internal_code is None:
        raise HTTPException(status_code=404, detail=f"Stop: {stop_code} does not exist")
    
    bus_infos = {
        "stop_code": stop_code,
        "stop_name": get_stop_name(stop),
        "date": datetime.datetime.now().astimezone().strftime("%Y-%m-%d"),
        "buses": []
    }
    
    for entity in feed.entity:
        if entity.trip_update.trip.schedule_relationship not in (
                entity.trip_update.trip.SCHEDULED,
                entity.trip_update.trip.ADDED,
            ):#for the whole bus trip
            continue
        for stop_time in entity.trip_update.stop_time_update:
            if stop_time.schedule_relationship != stop_time.SCHEDULED: #for the specific bus stop
                continue
            if stop_time.stop_id == internal_code:
                #testing here
                route_id = entity.trip_update.trip.route_id
                direction_id = entity.trip_update.trip.direction_id
                route_short_name = directions.get((route_id, str(direction_id)))

                bus_time = datetime.datetime.fromtimestamp(stop_time.arrival.time).astimezone()
                minutes = round(find_time_diff(bus_time).total_seconds()/60)
                if minutes >= 50:
                    continue
                bus_infos["buses"].append({
                    "time_12h": bus_time.strftime("%I:%M %p"),
                    "predicted_arrival": format_minutes(minutes),
                    "ending_destination": get_destination_name(route_short_name, direction_id, dict_names)
                })
                break #already found here
    return bus_infos

def load_stops(filepath):
    stops = {}
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            stops[row["stop_code"]] = {
                "stop_id": row["stop_id"],
                "stop_name": row["stop_name"],
            }
    return stops

def load_directions(filepath):
    directions = {}
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            directions[(row["route_id"], row["direction_id"])] = row["route_short_name"]
    return directions

def load_direction_names(filepath):
    direction_names = {} 
    with open(filepath,  encoding="utf-8-sig") as f: #tf is encoding
        reader = csv.DictReader(f)
        for row in reader:
            direction_names[(row["direction_id"], row["route_name"])] = row["direction_name"]
    return direction_names

# def load_routes(filepath):
#     routes = []
#     with open(filepath) as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             routes[row["route_id"]] = {
#                 "route_short_name": row["route_short_name"]
#             }
#     return routes

def get_internal_id(stop):
    if stop is None:
        return None
    return stop.get("stop_id")

def get_stop_name(stop):
    if stop is None:
        return "no name"
    return stop.get("stop_name")

def find_time_diff(bus_time):
    current_time = datetime.datetime.now().astimezone()
    difference = bus_time - current_time
    return difference

def format_minutes(value): 
    if (value < 0):
        return f"{abs(value)} minutes ago..."
    return f"{value} minutes away!"

def get_destination_name(route_short_name: str, direction_id, direction_names):
    if route_short_name is None:
        return None
    name = route_short_name.lstrip("0") or route_short_name #if theres a leading 0, remove, else nothing happens
    return direction_names.get((str(direction_id), name))
