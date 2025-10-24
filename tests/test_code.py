import subprocess
import time
import requests
#hi
# Start Flask server
flask_process = subprocess.Popen(["python", "main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Wait for the server to be fully ready (with retry logic)
def wait_for_server(url='http://0.0.0.0:5000', timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    return False

def test_api_status():
    # Wait for the server to start
    if wait_for_server():
        # Make HTTP requests to the server
        response = requests.get('http://0.0.0.0:5000')
        assert response.status_code == 200
    else:
        print("❌ Server failed to start in time. Check logs below:")
        with open("flask.log", "r") as log_file:
            print(log_file.read())
        assert False  # Fail the test if the server didn't start in time

def test_shape_detection_success():
    if wait_for_server():  # Reuse your wait logic
        # Sample image data: Create a simple black image (or use a real test file from your repo)
        # For real testing, save a sample PNG (e.g., a circle drawn in code or manually) in a 'tests/' dir
        from io import BytesIO
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='black')  # Mock image; replace with actual shape image
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        files = {'file': ('test_image.png', img_byte_arr, 'image/png')}
        response = requests.post('http://0.0.0.0:5000/upload_shapes', files=files, data={'educationLevel': 'elementarylevel'})  # Adjust endpoint if different
        assert response.status_code == 500
        json_data = response.json()
        assert 'shape' in json_data  # e.g., {'shape': 'circle', 'description': '...'}
        assert json_data['shape'] == 'circle'  # Adjust expected value based on your mock image
    else:
        assert False, "Server failed to start"

def test_invalid_upload_error():
    if wait_for_server():
        # No file provided to trigger error
        response = requests.post('http://0.0.0.0:5000/upload_shapes', data={'educationLevel': 'elementarylevel'})  # Adjust endpoint if different
        assert response.status_code == 500  # Or whatever error code your app returns
        json_data = response.json()
        assert 'error' in json_data
        assert 'No file uploaded' in json_data['error']  # Adjust based on your error message
    else:
        assert False, "Server failed to start"

# Run test
try:
    test_api_status()
    test_shape_detection_success()
    test_invalid_upload_error()
finally:
    # Stop the server
    flask_process.terminate()
    flask_process.wait()  # Ensure full shutdown
