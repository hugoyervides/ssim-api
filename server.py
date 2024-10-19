from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
from skimage.metrics import structural_similarity as ssim
import io
import os
import time

app = Flask(__name__)

# Track if the server is busy
server_busy = False

def calculate_ssim(image1, image2):
    # Resize images to the smaller size between the two
    min_size = (min(image1.size[0], image2.size[0]), min(image1.size[1], image2.size[1]))
    image1 = image1.resize(min_size)
    image2 = image2.resize(min_size)

    # Convert images to grayscale (if not already)
    image1 = image1.convert('L')
    image2 = image2.convert('L')
    
    # Convert images to numpy arrays
    image1_np = np.array(image1)
    image2_np = np.array(image2)
    
    # Calculate SSIM
    score, _ = ssim(image1_np, image2_np, full=True)

    return score

@app.route('/compare', methods=['POST'])
def compare_images():
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({'error': 'Please upload two images.'}), 400
    
    global server_busy
    server_busy = True
    
    start_time_request = time.time()
    node_name = os.getenv('NODE_NAME', 'Unknown')
    image1 = request.files['image1']
    image2 = request.files['image2']
    
    try:
        img1 = Image.open(io.BytesIO(image1.read()))
        img2 = Image.open(io.BytesIO(image2.read()))
        start_time_calculation = time.time()
        score = calculate_ssim(img1, img2)
        end_time = time.time()
        elapsed_time_request_ms = (end_time - start_time_request) * 1000
        elapsed_time_calculation_ms = (end_time - start_time_calculation) * 1000
        return jsonify({'ssim_score': score, 'node_name' : node_name, 'elapsed_time_request_ms': elapsed_time_request_ms, 'elapsed_time_calculation_ms': elapsed_time_calculation_ms})
    except Exception as e:
        return jsonify({'error': f'Failed to process images: {str(e)}', 'node_name' : node_name}), 400
    finally:
        server_busy = False

@app.route('/ready', methods=['GET'])
def readiness_probe():
    global server_busy
    # If the server is busy, return 503
    if server_busy:
        return "Server is busy", 503
    return "Ready", 200

if __name__ == '__main__':
    app.run()