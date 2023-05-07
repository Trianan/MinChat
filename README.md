# MinChat
A terminal-based chatroom server and client written in Python, with a GUI.

MinChat is currently in alpha development, and is not guaranteed to work
on your platform.

## Usage
### Installation
    To install the MinChat toolset, simply clone this repo, and have Python3 installed.

### To run MinChat as a client:
    The client version you are using and the version the server is using
    must match.
    Run the following command, using the ip of a running MinChat server:

        python MinChat/{version_folder}/minclient.py {server_ip}

    Enter your username, and the GUI should appear.

### To run MinChat as a server:
    Run the following command, using the ip of the hosting computers public ip:
        
        python MinChat/{version_folder}/minserver.py {public_ip}

    The server will begin listening for client connections immediately.

## Credit
    Heavy credit due to Zhang Zeyu, writer of the tutorial used to create the core of this
    program.

    Link to tutorial here:
    https://dev.to/zeyu2001/build-a-chatroom-app-with-python-44fa