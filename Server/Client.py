import requests
import time
import os

# Flask API URL
api_url = "http://127.0.0.1:5000/generate-object"  # Update if Flask API runs on a different host/port

# Sample input data
input_data = {
    "subject_id": 55,
    "complexity": "easy",
    "model_type": "3D",  # Options: "2D", "3D"
    "prompt": "a husky dog",
    "type_completion_time": 122,
    "object_to_be_generated": "ball",
}

def save_response_content(response, filename):
    """
    Save the content of the response to a file.
    """
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"File saved as: {filename}")

def main():
    # Log the start time
    start_time = time.time()

    try:
        # Send POST request to the Flask API
        print(f"Sending request to {api_url} with data: {input_data}")
        response = requests.post(api_url, json=input_data)

        # Measure completion time
        completion_time = time.time() - start_time
        print(f"Task completed in {completion_time:.2f} seconds")

        # Handle response
        if response.status_code == 200:
            # Check Content-Disposition header to determine the file type
            content_disposition = response.headers.get("Content-Disposition", "")
            
            if "attachment" in content_disposition:
                filename = content_disposition.split("filename=")[-1].strip('"')
                
                if filename.endswith(".png") or filename.endswith(".glb"):
                    save_response_content(response, filename)
                else:
                    print("Unknown file format received.")
            else:
                print("Response from API:", response.text)
        else:
            # Handle errors
            print("Failed to connect to the API.")
            print(f"Status Code: {response.status_code}")
            print("Response Text:", response.text)

    except requests.exceptions.RequestException as e:
        print("An error occurred while making the request:", e)

if __name__ == "__main__":
    main()
