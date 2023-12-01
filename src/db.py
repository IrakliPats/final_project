import os
from pymongo import MongoClient


def get_mongo_client():
    connection_string_name = 'MONGODB_CS'

    # Check if the environment variable is defined
    if connection_string_name not in os.environ:
        raise Exception(f'Application requires {connection_string_name} to be '
                        f'defined in environment')

    # Fetch the connection string from the environment variables
    connection_string = os.getenv(connection_string_name)

    # Check if the connection string is present
    if connection_string is None:
        raise Exception(f'Connection string {connection_string_name} '
                        f'is not set in the environment')

    # Create a MongoDB client and return it
    return MongoClient(connection_string)
