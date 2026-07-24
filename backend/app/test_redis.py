import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True) 
r.set("test_key", "hello", ex=10)


val = r.get("test_key")
print(f"value: {val}")