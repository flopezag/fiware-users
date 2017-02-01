#<a name="top"></a>fiware-users
[![License badge](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Script to get the number of Trial and Community users in a FIWARE Lab node.


## Build and Install

### Requirements

The following software must be installed:

- Python 2.7
- pip
- virtualenv

### Installation

The recommend installation method is using a virtualenv. Actually, the installation 
process is only about the python dependencies, because the python code do not need 
installation.

1. Clone this repository.
2. Create virtualenv: 'virtualenv -p python2.7 env
3. Activate the virtualenv: 'source env/bin/activate
4. Install dependencies: 'pip install -r requirements.txt'

[Top](#top)


## Configuration

The configuration file can be found in fiware-users.ini. You need to specify a valid
administrator user credentials (tenant id, username and password) besides with the 
correct name of the FIWARE Lab node. You can copy this file in the /etc/fiware.d or
define the environment variable 'FIWARE_USERS_SETTINGS_FILE' to the place in which
you put yout config file.

    $ export FIWARE_USERS_SETTINGS_FILE=fiware-users.ini 

[Top](#top)


## Run

To execute the script, just run the command:

    $ python get_users.py

[Top](#top)


## License

These scripts are licensed under Apache License 2.0.
