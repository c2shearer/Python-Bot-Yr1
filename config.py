import configparser

config = None

def Load(path):
    global config

    config = configparser.ConfigParser()
    config.read(path)

def Get():
    return config
