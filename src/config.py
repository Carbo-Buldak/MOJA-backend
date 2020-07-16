from yaml import load, Loader

with open('config.yaml', 'r') as config_yaml:
    config = load(config_yaml, Loader=Loader)