from flask import Flask, request, jsonify, send_file
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
    file_name = prompt.replace(" ","_")
    output_file = f"objects/{file_name}.obj"  # Ensure this path matches the model's output

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
        print(f'Running {model_name} script with prompt: {prompt}')
        print(command)
        subprocess.run(command, shell=True, check=True)
        print("outputfile:" , output_file)
        if output_file and os.path.exists(output_file):
            return output_file
        else:
            raise FileNotFoundError("Output file not generated.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Model execution failed: {e.stderr}")

@app.route('/generate-object', methods=['POST'])
def generate_3d_object():
    try:
        # Retrieve prompt from the request data
        prompt_data = request.json
        model_type = prompt_data.get("model_type")  # model_1 or model_2
        prompt = prompt_data.get("prompt")
        print(prompt_data)
        output_file = run_model_in_env(model_type, prompt)
        print(output_file)
        # Send the .obj file content as response
        return send_file(output_file, as_attachment=True, download_name="model.obj")
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
