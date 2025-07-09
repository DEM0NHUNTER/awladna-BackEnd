# BackEnd/tests/test_redis.py

import redis

r = redis.Redis(host='localhost', port=6379, db=0)

print("Setting key...")
r.set('test_key', 'test_value')
print(f"Set 'test_key' to 'test_value'.")

print("Getting key...")
value = r.get('test_key')
print(f"Got 'test_key': {value.decode('utf-8')}")

print("Updating key...")
r.set('test_key', 'new_value')
new_value = r.get('test_key')
print(f"Updated 'test_key' to: {new_value.decode('utf-8')}")

print("Deleting key...")
r.delete('test_key')
deleted_value = r.get('test_key')
print(f"Deleted 'test_key', current value: {deleted_value}")

r.close()
