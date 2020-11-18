from json import load
from pymongo import MongoClient

port = int(input("Please enter the port to connect to: "))


client = MongoClient('localhost', port)
db = client['291db']


posts_collection = db['posts_collection']
posts_collection.delete_many({})
with open('Posts.json') as file:
    data = load(file)
for row in data['posts']['row']:
    posts_collection.insert_one(row)
    
tags_collection = db['tags_collection']
tags_collection.delete_many({})
with open('Tags.json') as file:
    data = load(file)
for row in data['tags']['row']:
    tags_collection.insert_one(row)

votes_collection = db['votes_collection']
votes_collection.delete_many({})
with open('Votes.json') as file:
    data = load(file)
for row in data['votes']['row']:
    votes_collection.insert_one(row)

client.close()
