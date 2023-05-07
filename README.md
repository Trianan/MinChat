# MinChat
A terminal-based chatroom server and client written in Python, with a GUI.

# Usage
To install the MinChat toolset, simply clone this repo, and have Python3 installed.

To run MinChat as a client:
    Run the following command, using the ip of a running MinChat server:
    `python MinChat/minclient.py {server_ip}`

    Enter your username, and the GUI should appear.

To run MinChat as a server:
    Run the following command, using the ip of the hosting computers public ip:
    `python MinChat/minserver.py {public_ip}`

    The server will begin listening for client connections immediately.

