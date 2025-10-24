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

# Run test
try:
    test_api_status()
finally:
    # Stop the server
    flask_process.terminate()
    flask_process.wait()  # Ensure full shutdown
