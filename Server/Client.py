import requests
import json
import time

# Flask API URL
api_url = "http://127.0.0.1:5000/generate-object"  # Update this if your Flask API is running on a different host/port

# Sample input data (this would be the data you want to send to the Flask API)
input_data = {
    "model_type": "text-3d",  # or "model_2", depending on which model you want to use
    "prompt": "a high quality dragon"
}

start = time.time()
# Send POST request to the Flask API
response = requests.post(api_url, json=input_data)

completion_time = time.time() - start
print("Task completed in ", completion_time)
# response = requests.get(api_url)

# Check if the request was successful
if response.status_code == 200:
    # Successfully received response from API
    print("Response from API:", response)
else:
    # If there was an error in the request
    print("Failed to connect to the API.")
    print("Status Code:", response.status_code)
