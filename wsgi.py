import sys

sys.path.append("/home/dotcloud/current");

from app import app as application
from flask import *

if __name__ == "__main__":
    application.debug = True;
    application.run();
