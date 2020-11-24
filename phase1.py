from json import load
from pymongo import MongoClient
from time import monotonic

port = int(input("Please enter the port to connect to: "))

print("Start.")
client = MongoClient('localhost', port)
db = client['291db']

posts_collection = db['posts_collection']
posts_collection.delete_many({})

print("Loading Posts...")
with open('Posts.json') as file:
    data = load(file)
print("Posts Loaded.")
ts = monotonic()
posts_collection.insert_many(data['posts']['row'])
print("Inserted Posts: %ds" % (monotonic() - ts))

tags_collection = db['tags_collection']
tags_collection.delete_many({})

print("Loading Tags...")
with open('Tags.json') as file:
    data = load(file)
print("Tags Loaded.")

ts = monotonic()
tags_collection.insert_many(data['tags']['row'])
print("Inserted Tags: %ds" % (monotonic() - ts))

votes_collection = db['votes_collection']
votes_collection.delete_many({})

print("Loading Votes...")
with open('Votes.json') as file:
    data = load(file)
print("Votes Loaded.")

ts = monotonic()
votes_collection.insert_many(data['votes']['row'])
print("Inserted Votes: %ds" % (monotonic() - ts))

client.close()
print("Exit.")