from flask import Flask
from flask_sock import Sock
import time
import sys

app = Flask(__name__)
sock = Sock(app)



from gameServer import *
from login import *



if __name__ == '__main__':
    # my_port needs to match the second number in line 10 of compose.yaml
    my_port = 5000
    app.run(host='0.0.0.0', port = my_port, debug=True)