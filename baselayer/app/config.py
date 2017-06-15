import yaml
import os
from pathlib import Path
import glob


class Config(dict):
    def __init__(self, config_files=None):
        dict.__init__(self)
        if config_files is not None:
            for f in config_files:
                self.update_from(f)

    def update_from(self, filename):
        """Update configuration from YAML file"""
        if os.path.isfile(filename):
            more_cfg = yaml.load(open(filename))
            dict.update(self, more_cfg)
            print('[baselayer] Loaded {}'.format(os.path.relpath(filename)))

    def __getitem__(self, key):
        keys = key.split(':')

        val = self
        for key in keys:
            val = val.get(key)
            if val is None:
                return None

        return val

    def show(self):
        """Print configuration"""
        print()
        print("=" * 78)
        print("Configuration")

        for key in self:
            print("-" * 78)
            print(key)

            if isinstance(self[key], dict):
                for key, val in self[key].items():
                    print('  ', key.ljust(30), val)

        print("=" * 78)


def load_config(config_files=None):
    basedir = Path(os.path.dirname(__file__))/'..'

    if config_files is None:
        config_files = [Path(basedir/'config.yaml'),
                        Path(basedir/'../config.yaml')]

    # Always load the default configuration values first, and override
    # with values in user configuration files
    config_files = [Path(basedir/'config.yaml.example'),
                    Path(basedir/'../config.yaml.example')] + config_files

    config_files = [os.path.abspath(Path(c).absolute()) for c in config_files]

    cfg = Config(config_files)

    return cfg


if __name__ == "__main__":
    show()
