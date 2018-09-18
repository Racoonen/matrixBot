import yaml

__config = None
_config_yml = 'config.yml'


def load_configuration():
    with open(_config_yml, 'r') as f:
        cfg = yaml.load(f)

    globals()['__config'] = cfg

    return cfg


def config(key=None):
    cfg = __config or load_configuration()
    return cfg[key] if key else cfg
