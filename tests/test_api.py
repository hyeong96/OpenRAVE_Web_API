import requests
import pytest
import os
import shutil
import os.path
import json
from server import app
from pathlib import Path

API_KEY = "http://localhost:5000/api/robot"
TEST_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_resource')
        

####################### TEST FIXTURES ####################

@pytest.fixture
def client():
    flask_app = app
    flask_app.config['UPLOAD_FOLDER'] = TEST_FOLDER
    client = flask_app.test_client()
    yield client

######################## API TESTS #########################

# unit test for GET /api/robot
def test_get_robot_list(client):
    response = client.get(API_KEY)
    json_response = response.get_json()
    
    assert response.status_code == 200
    assert len(json_response['robots']) == 2

# unit test for GET/api/robot/<filename>
def test_get_robot_properties(client):
    response = client.get(API_KEY + "/kr150.dae")
    json_response = response.get_json()

    assert response.status_code == 200
    assert json_response['robotProperties']['number_of_joint'] == 9
    assert json_response['robotProperties']['number_of_link'] == 10

# unit test for POST/api/robot
def test_post_robot(client):
    filename = "barrett-hand.dae"
    shutil.copyfile(os.path.join(TEST_FOLDER, filename), os.path.join(TEST_FOLDER, "test_post.dae"))
    data = {
        'robot_file': (open(os.path.join(TEST_FOLDER, filename), 'rb'), "test_post.dae")
    }
    response = client.post(API_KEY, data=data)
    assert os.path.isfile(os.path.join(TEST_FOLDER, "test_post.dae"))
    os.remove(os.path.join(TEST_FOLDER, "test_post.dae"))
    assert response.status_code == 200

# unit test for PUT /api/robot/<filename>
def test_modify_robot(client):
    new_name = 'CoolRobot'
    filename = "barrett-hand.dae"
    data = {
        'name': new_name
    }
    response = client.put(API_KEY + "/" + filename, data=data)
    json_response = response.get_json()

    assert new_name in json_response['message'] 
    assert response.status_code == 200

# unit test for GET /api/robot/<filename>/download
def test_download_robot(client):
    filename = "barrett-hand.dae"
    response = client.get(API_KEY + "/" + filename + "/download")

    assert response.status_code == 200

# unit test for DELETE /api/robot/<filename>
def test_delete_robot(client):
    filename = "kr150.dae"
    shutil.copyfile(os.path.join(TEST_FOLDER, filename), os.path.join(TEST_FOLDER, "test_delete.dae"))
    response = client.delete(API_KEY + "/test_delete.dae")

    assert not os.path.isfile(os.path.join(TEST_FOLDER, "test_delete.dae"))
    assert response.status_code == 200
