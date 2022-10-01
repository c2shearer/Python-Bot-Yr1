import configparser

config = configparser.ConfigParser()
config.read("config.ini")

def Get():
    return config
