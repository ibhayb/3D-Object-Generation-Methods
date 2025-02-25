from flask import Flask, request, jsonify, send_file
import subprocess
import os
import random
from pathlib import Path
from rembg import remove
from PIL import Image
import time


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

def generate_seed():
    return random.randint(1,999999)

def log_attempt(model_name, subject_id, attempt, prompt, seed, complexity, type_completion_time, image_generation_time, object_generation_time, path,file_name):
      # image_generation_time = generation time of image, object_generation_time = generation time of 3d object
      log_file = f"{path}/{subject_id}_{model_name}_log.txt"
      # Check if log file is empty and write header if needed
      if not os.path.exists(log_file) or os.stat(log_file).st_size == 0:
          with open(log_file, "w") as f:
              f.write("subject_id,attempt,prompt,seed,complexity,type_completion_time,image_generation_time,object_generation_time,method,file_name\n")
                    
      with open(log_file, "a") as f:
        f.write(f"{subject_id},{attempt},{prompt},{seed},{complexity},{type_completion_time},{image_generation_time},{object_generation_time},{model_name},{file_name}\n")

def run_model_in_env(model_name, prompt, subject_id, complexity, type_completion_time):
    file_name = ""
    seed = generate_seed()
    image_generation_time = 0
    object_generation_time = 0
    # Define the environment for each model
    if model_name == "3D":
        # first generate the image with perflow
        output_path = Path(f'results/{subject_id}/3D/')  # Convert string to Path
        num_files = len(list(output_path.glob("*.glb")))  # Count files in directory
        file_name = f"{complexity}_{seed}_{num_files + 1}"  # Use f-string for cleaner formatting
        command = f'conda run -n perflow python "C:/Users/FRA-UAS MR-Labor/Documents/MMI-3D/piecewise-rectified-flow/demo.py" --prompt "{prompt}" --seed {seed} --output_dir {output_path} --output_file_name {file_name}'
        print("Method 3D: Running perflow", command)
        start_time = time.time()
        subprocess.run(command, shell=True, check=True)
        image_generation_time = time.time() - start_time
        # use generated image with TripoSR for 3D Object
        command = f'conda run -n TripoSR python "C:/Users/FRA-UAS MR-Labor/Documents/MMI-3D/TripoSR/run.py" {output_path}\{file_name}.png --output-dir {output_path} --output_file_name {file_name} --model-save-format glb'
        start_time = time.time()
        subprocess.run(command, shell=True, check=True)
        object_generation_time = time.time() - start_time
        output_file_path =  Path(f'results/{subject_id}/3D/{file_name}.glb')
    elif model_name == "2D":
        output_path = Path(f'results/{subject_id}/2D/')  # Convert string to Path
        num_files = len(list(output_path.glob("*.png")))  # Count files in directory
        file_name = f"{complexity}_{seed}_{num_files + 1}"  # Use f-string for cleaner formatting
        command = f'conda run -n perflow python "C:/Users/FRA-UAS MR-Labor/Documents/MMI-3D/piecewise-rectified-flow/demo.py" --prompt "{prompt}" --seed {seed} --output_dir {output_path} --output_file_name {file_name}'
        start_time = time.time()
        subprocess.run(command, shell=True, check=True)
        image_generation_time = time.time() - start_time
        output_file_path =  Path(f'results/{subject_id}/2D/{file_name}.png')
    else:
        raise ValueError("Invalid model name")

    try:
        log_attempt(model_name,subject_id,num_files+1,prompt,seed,complexity,type_completion_time,image_generation_time,object_generation_time,output_path,file_name)
        
        if output_file_path and os.path.exists(output_file_path):
            return output_file_path
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
        subject_id = prompt_data.get("subject_id")
        complexity = prompt_data.get("complexity")
        type_completion_time = prompt_data.get("type_completion_time")

        output_file = run_model_in_env(model_type, prompt, subject_id, complexity, type_completion_time)
        print(output_file)
        # Send the .obj file content as response
        if model_type == "3D":
            # send glb file
            return send_file(output_file, as_attachment=True, download_name="obj.glb")
        else:
            # send image
            return send_file(output_file, as_attachment=True, download_name="img.png")
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
