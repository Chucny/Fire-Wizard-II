#imports, not all needed

import sys
import traceback
import os
import time
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# FUNCTIONS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== DEBUG EXCEPTIONS =====
def handle_exception(exc_type, exc_value, exc_traceback):
    print("Uncaught error!")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    input("Press enter to exit...")

def safe_model(path):
    full_path = os.path.join(BASE_DIR, path)
    if not os.path.exists(full_path):
        print(f"WARNING: model {full_path} not found, using 'cube'")
        return 'cube'
    return full_path

def safe_texture(path):
    full_path = os.path.join(BASE_DIR, path)
    if not os.path.exists(full_path):
        print(f"WARNING: texture {full_path} not found, using None")
        return None
    return full_path
