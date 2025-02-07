from flask import Flask, request, jsonify
import subprocess
import os

from rembg import remove
from PIL import Image


app = Flask(__name__)

def remove_background(input_image):
    # Open the input image file
    output_image = input_image.replace(".", "-no-bg.")
    with open(f'images/samples/{input_image}', 'rb') as input_file:
        input_data = input_file.read()

    # Remove the background
    output_data = remove(input_data)

    # Save the output image
    with open(f'images/samples/{output_image}', 'wb') as output_file:
        output_file.write(output_data)

    return output_image

def run_model_in_env(model_name, prompt):
    # Define the environment for each model
    if model_name == "text-3d":
        command = f'conda run -n shap-e python "C:/Users/FRA-UAS MR-Labor/Documents/MMI-3D/shap-e/shap_e/examples/text_to_3d.py" --prompt "{prompt}"'
    elif model_name == "text-image":
        command = f'conda run -n ldm python "C:/Users/FRA-UAS MR-Labor/Documents/MMI-3D/stable-diffusion/scripts/txt2img.py" --prompt "{prompt}" --plms --skip_grid --n_samples 4 --n_iter 1 --outdir "images/"'
    elif model_name == "image-3d":
        image = remove_background(prompt)
        command = f'conda run -n shap-e python "C:/Users/FRA-UAS MR-Labor/Documents/MMI-3D/shap-e/shap_e/examples/image_to_3d.py" --image "{image}"'

    else:
        raise ValueError("Invalid model name")

    try:
        print(f'trying to run the {model_name} script with prompt {prompt}')
        print(command)
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(result)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

@app.route('/generate-object', methods=['POST'])
def generate_3d_object():
    try:
        # Retrieve prompt from the request data
        prompt_data = request.json
        model_type = prompt_data.get("model_type")  # model_1 or model_2
        prompt = prompt_data.get("prompt")

        # Run the AI model and get the output
        output = run_model_in_env(model_type, prompt)
        return jsonify({"result": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
