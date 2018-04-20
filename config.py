import os

from config_SECRET import EXIST_SECRET



MODE = 'development'

EXIST_CONFIG = {

    'global': {
        'app_name': 'Letters1916',
        'data_dir': 'Letters1916/data',
        'xquery_path': os.path.join('letter_graph', 'server', 'xquery')
    },
    'development': {
        'address': '127.0.0.1',
        'port': '8080',


        # And import in and unpack the secret info.
        **EXIST_SECRET['development']
    }
}


if __name__ == '__main__':
    print(exist_config)