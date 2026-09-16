import configparser

config = configparser.ConfigParser()
with open("config.properties") as stream:
    config.read_string("[DEFAULT]\n" + stream.read())

ACTIVE_MAP = config.get("DEFAULT", "ACTIVE_MAP")
COMMUNICATION_PORT = config.getint("DEFAULT", "COMMUNICATION_PORT")
DASH_PORT = config.getint("DEFAULT", "DASH_PORT")
SIMULATION_SPEED = config.getfloat("DEFAULT", "SIMULATION_SPEED")