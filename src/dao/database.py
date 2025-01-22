import os
from pymongo import MongoClient


def get_database():
    client = MongoClient(os.environ.get('MONGODB_URL'))
    return client['iot_database']


# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":
    # Get the database
    collection = get_database()
