# OpenRAVE Web API

This repository contains source code for the RESTFUL API server app that manages a collection of OpenRave robots. 

You can run this server locally if OpenRAVE is installed, 

See below instructions for more details.

### Run server locally ###

1. after cloning this git repository, go into OpenRAVE_Web_API folder
2. enter the following command in terminal/command-prompt `python3 server.py`

Note: openrave is required to run the server

## API Endpoints ##
Please see below for more details on available API endpoints:

| METHOD |                URL                 |           Query Param       |                   Description                                             |  Response |
| ------ | ---------------------------------- |-----------------------------| ---------------------------------------------                             | ----------|
| GET    | /api/robot                         |None                         | list all robots on the server                                             |    JSON   |
| GET    | /api/robot/\<filename>             |None                         | get properties of a requested robot including name, num_joints, num_links |    JSON   |
| POST   | /api/robot                         |robot_file = *.dae or *.zae  | add a robot to the server by uploading a robot file (*.dae or *.zae)      |    JSON   |
| PUT    | /api/robot/\<filename>             |name = value                 | update robot properties. only supports name update at the moment          |    JSON   |
| GET    | /api/robot/\<filename>/donwload    |None                         | download a robot file (.dae) from the server                              |   *.dae   |
| DELETE | /api/robot/\<filename>             |None                         | remove a robot from the server                                            |    JSON   |
| GET    | /api/robot/\<filename>/preview     |None                         | get a preview of a robot using openrave                                   |preview.jpg|

## Automated Server Testing using PyTest ##
Please follow the steps below to run automated unit test to sanity check API endpoints.

Note: currently, there are 6 tests to test all API endpoints except preview endpoint.

1. go into Mujin_Final_Project folder
2. type the following command in terminal/command-prompt `python3 -m pytest`