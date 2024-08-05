import os
import json
import re
from openravepy import *
import imageio
import time

# utility function to get all available robots in specific folder
def list_robots(UPLOAD_FOLDER):
    res = []
    # append robot list with files with '.dae' extension
    for f in os.listdir(UPLOAD_FOLDER):
        f_split = f.split('.')
        if os.path.isfile(os.path.join(UPLOAD_FOLDER, f)) and f_split[1] == 'dae':
            res.append(f_split[0])
            
    return res

# utility function to get robot properties by parsing .dae file
def get_robot_info(UPLOAD_FOLDER, filename):
    name = ""
    num_joint_in = 0
    num_joint_na = 0
    num_link = 0
    filepath = os.path.join(UPLOAD_FOLDER, filename + '.dae')
    file = open(filepath, 'r')
    lines = file.readlines()
    prev = None

    # get robot properties based on keyword
    for line in lines:
        # count number of links
        if re.search("link sid",line):
            num_link += 1
        # cout number of joints
        if re.search("instance_joint", line):
            num_joint_in += 1
        if re.search("joint name", line):
            num_joint_na += 1
        # obtain name
        if re.search("visual_scene id", line) and len(line.split("name=")) > 1:
            name = line.split("name=")[1][:-2].strip('\"')
        elif prev and re.search("visual_scene id", prev) and name == "":
            name = line.split("name=")[1][:-2].strip('\"')
        prev = line
    file.close()

    return name, max(num_joint_in, num_joint_na), num_link

# utility function to update a robot name in .dae file
def update_name(UPLOAD_FOLDER, filename, name):
    old_name = ""
    filepath = os.path.join(UPLOAD_FOLDER, filename + '.dae')
    prev = None

    # search for an existing name and replace with a new name
    with open(filepath,'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            # look for name
            if re.search("visual_scene id", line) and len(line.split("name=")) > 1:
                old_name = line.split("name=")[1][:-2].strip('\"')
                lines[i] = line.replace(old_name, name)
            elif prev and re.search("visual_scene id", prev) and old_name == "":
                old_name = line.split("name=")[1][:-2].strip('\"')
                lines[i] = line.replace(old_name, name)
            prev = line

    with open(filepath,'w') as file:
        file.writelines(lines)
    file.close()

    return old_name

# utility function to get a preview of a robot
def get_preview(UPLOAD_FOLDER, filename):
    env = Environment()
    env.SetViewer('qtcoin')
    # load environment with a robot
    env.Load(os.path.join(UPLOAD_FOLDER, filename + '.dae'))
    time.sleep(1)
    
    try:
        env.GetViewer().SendCommand('SetFiguresInCamera 1')
        # take image
        I = env.GetViewer().GetCameraImage(640,480,  env.GetViewer().GetCameraTransform(), [640,640,320,240]) 
        # write to 'openrave.jpg' file 
        imageio.imwrite('preview.jpg',I)
        return True
    except:
        print("Openrave exception occured")
        return False
