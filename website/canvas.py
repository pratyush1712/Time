# This is the first step to using the Canvas Python API. We import the Canvas class from the canvasapi
# package and then initialize a new Canvas object.
# Import the Canvas class
from canvasapi import Canvas

# Canvas API URL
API_URL = "https://login.canvas.cornell.edu/"
# Canvas API key
API_KEY = "p@$$w0rd"

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
