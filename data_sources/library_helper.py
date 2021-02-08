import os

def assure_ext_library(package:str):
    try:
        __import__(package)
    except:
        os.system("pip install "+ package)