import logging
import urllib.parse
import xmlrpc.client
import warnings


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class ExistManager:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    @classmethod
    def setup(cls, config, mode='development'):

        cls.logger.debug(f"{__name__}.setup method called: config: {config}")
        

        for key, value in {**config[mode], **config['global']}.items():
            setattr(cls, key, value)

        cls.app_path = f'/db/apps/{cls.app_name}'

        rpc_string = f'http://{cls.username}:{cls.password}'
        rpc_string += f'@{cls.address}:{cls.port}/exist/xmlrpc'

        cls.rpc = xmlrpc.client.ServerProxy(
            rpc_string, encoding='UTF-8', verbose=False
        )

        cls.xqueries = cls._get_xqueries_from_exist()
        cls._build_xqueries_as_methods()

    @classmethod
    def _get_xqueries_from_exist(cls):
        desc = cls.rpc.getCollectionDesc(cls.app_path)
        xqueries = [d['name'].replace('.xql', '')
                    for d
                    in desc['documents']
                    if d['name'].endswith('.xql')]
        return xqueries


    @classmethod
    def _build_xqueries_as_methods(cls):
        for xquery in cls.xqueries:
            func = cls._build_xquery_caller(xquery)
            setattr(cls, xquery, func)

    @staticmethod
    def _build_xquery_caller(xquery):
        async def func(*args, **kwargs):


            pass


        return func

    @classmethod
    def _build_query_url(cls, xquery, *args, **kwargs):
        url = [f"http://{cls.address}"]
        if cls.port:
            url.append(f":{cls.port}")
        url.append(f"/exist/apps/{cls.app_name}/{xquery}.xql")
        if len(args) == 1 and type(args[0]) == dict and kwargs:
            warnings.warn('Args passed as dict and keyword arguments; only args used', SyntaxWarning)
        if len(args) == 1 and type(args[0]) == dict:
            url.append('?')
            url.append(urllib.parse.urlencode(args[0], quote_via=urllib.parse.quote))
        elif kwargs:
            url.append('?')
            url.append(urllib.parse.urlencode(kwargs, quote_via=urllib.parse.quote))
        return ''.join(url)









if __name__ == '__main__':
    import sys
    sys.path.append('../letter_graph')
    from config import EXIST_CONFIG
    print(EXIST_CONFIG)
