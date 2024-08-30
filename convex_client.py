import os
from dotenv import load_dotenv
from convex import ConvexClient

load_dotenv()

CONVEX_URL = os.getenv("CONVEX_URL")

client = ConvexClient(CONVEX_URL)


def get_convex_client():
    return client
