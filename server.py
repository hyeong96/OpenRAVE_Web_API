import os
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
import json
from zipfile import ZipFile
from utils import list_robots, get_robot_info, update_name, get_preview

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'robots')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.json.sort_keys = False
app.use_x_sendfile = True


# POST endpoints

# add a new robot file to the server
@app.route('/api/robot', methods=['POST'])
def add_robot():
    # check if the post request has the robot_file key
    if 'robot_file' not in request.files:
        return jsonify({'success': False,
                        'message': 'key not found. add a \'robot_file\' key to the request'}), 400

    file = request.files['robot_file']
    # check if the file is selected
    if file.filename == '':
        return jsonify({'success': False,
                        'message': 'no selected file'}), 400

    # get secure filename
    filename = secure_filename(file.filename)
    # process the files based on the extension type
    if file and file.filename.split('.')[1].lower() in {'zae', 'dae'}:
        if file.filename.split('.')[1].lower() == 'zae':
            with ZipFile(file, 'r') as zObject:
                for name in zObject.namelist():
                    if name.split('.')[1].lower() == 'dae':
                        # unzip .zae file before processing
                        zObject.extract(name, app.config['UPLOAD_FOLDER'])
        else:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return jsonify({'success': True,
                        'message': f'\'{file.filename}\' has been successfully ' \
                        'uploaded to the server!'})

    return jsonify({'success': False,
                    'message': 'selected file type is not compatible' \
                    'try again with a file with either .zae or .dae extensions'}), 406

# GET endpoints

# get list of all robots
@app.route('/api/robot', methods=['GET'])
def get_robots():
    # get robot list
    robots = list_robots(app.config['UPLOAD_FOLDER'])
    return jsonify({'success': True, 'robots': robots})

# get properties of a particular robot
@app.route('/api/robot/<filename>', methods=['GET'])
def get_property(filename):
    if filename == '':
        return jsonify({'success': False,
                        'message': 'no selected file'}), 400
 
    if len(filename.split('.')) > 1:
        filename = filename.split('.')[0]
    # get secure filename
    filename = secure_filename(filename)
    # get updated robot list
    robots = list_robots(app.config['UPLOAD_FOLDER'])
    if filename not in robots:
         return jsonify({'success': False,
                         'message': 'the requested robot does not exist on the server' \
                         'please try again from the robots listed below', \
                         'available robots': robots}), 404

    #get robot properties
    name, num_joint, num_link = get_robot_info(app.config['UPLOAD_FOLDER'], filename)

    return jsonify({'success': True,
                    'robotProperties': {"name": name, "number_of_joint": num_joint,
                    'number_of_link': num_link}})

# download a robot file from the server
@app.route('/api/robot/<filename>/download', methods=['GET'])
def download_robot(filename):
    if filename == '':
        return jsonify({'success': False,
                        'message': 'no selected file'}), 400

    if len(filename.split('.')) > 1:
        filename = filename.split('.')[0]
    # get secure filename
    filename = secure_filename(filename)
    # get updated robot list
    robots = list_robots(app.config['UPLOAD_FOLDER'])
    if filename not in robots:
         return jsonify({'success': False,
                         'message': f'the requested robot file \'{filename}\' does not exist' \
                         'on the server. please try again from the robots listed below', \
                         'available_robots': robots}), 404

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename + '.dae')

# download a robot preview image from the server
@app.route('/api/robot/<filename>/preview', methods=['GET'])
def preview_robot(filename):
    if filename == '':
        return jsonify({'success': False,
                        'message': 'no selected file'}), 400

    if len(filename.split('.')) > 1:
        filename = filename.split('.')[0]
    # get secure filename
    filename = secure_filename(filename)
    # get updated robot list
    robots = list_robots(app.config['UPLOAD_FOLDER'])
    if filename not in robots:
         return jsonify({'success': False,
                         'message': f'the requested robot file \'{filename}\' does not exist ' \
                         'on the server. please try again from the robots listed below', \
                         'available_robots': robots}), 404
    
    if not get_preview(app.config['UPLOAD_FOLDER'], filename):
        return jsonify({'success': False,
                        'message': 'openrave exception occured'}), 500

    return send_from_directory(os.path.dirname(os.path.realpath(__file__)), "preview.jpg")

# PUT endpoints

# update existing robot properties
@app.route('/api/robot/<filename>', methods=['PUT'])
def update_properties(filename):
    if 'name' not in request.form:
        return jsonify({'success': False,
                        'message': 'key not found. add a \'name\' to the request'}), 400

    name = request.form['name']

    if filename == '':
        return jsonify({'success': False,
                        'message': 'no selected file'}), 400

    if len(filename.split('.')) > 1:
        filename = filename.split('.')[0]
    # get secure filename
    filename = secure_filename(filename)
    # get updated robot list
    robots = list_robots(app.config['UPLOAD_FOLDER'])
    if filename not in robots:
         return jsonify({'success': False,
                         'message': 'the requested robot does not exist on the server. ' \
                         'please try again from the robots listed below', \
                         'available_robots': robots}), 404

    old_name = update_name(app.config['UPLOAD_FOLDER'], filename, name)

    return jsonify({'success': True,
                    'message': f"robot name updated from \'{old_name}\' to \'{name}\'"})

# DELETE endpoints

# remove a robot from the server
@app.route('/api/robot/<filename>', methods=['DELETE'])
def remove_robot(filename):
    if filename == '':
        return jsonify({'success': False,
                        'message': 'no selected file'}), 400

    if len(filename.split('.')) > 1:
        filename = filename.split('.')[0]
    # get secure filename
    filename = secure_filename(filename)
    # get updated robot list
    robots = list_robots(app.config['UPLOAD_FOLDER'])
    if filename not in robots:
         return jsonify({'success': False,
                         'message': 'the requested robot does not exist on the server. ' \
                         'please try again from the robots listed below', 
                         'available_robots': robots}), 404
    
    # remove a robot from the folder
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename + '.dae'))

    return jsonify({'success': True,
                    'message': f"\'{filename}\' has been removed from the server"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, 
            debug=True, use_reloader=False)
