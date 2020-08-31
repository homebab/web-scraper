import logging
import logging.config

import yaml


def init_logger(name='__main__'):
    config_path = '../config/logging.yaml'

    with open(config_path) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    logging.config.dictConfig(config)
    return logging.getLogger(name)


if __name__ == '__main__':
    init_logger()
