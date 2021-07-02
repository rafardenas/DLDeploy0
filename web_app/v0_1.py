import os 
import sys
sys.path.append(os.getcwd())
from app import app


DEVICE = "cpu"


if __name__ == "__main__":
    app.run()