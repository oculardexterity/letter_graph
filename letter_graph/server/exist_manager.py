import aiohttp
import logging
import requests
import urllib.parse
import xmlrpc.client
import warnings


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



class ExistManager:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    @classmethod
    def setup(cls, config, mode='development'):

        #cls.logger.debug(f"{__name__}.setup method called: config: {config}")

        for key, value in {**config[mode], **config['global']}.items():
            setattr(cls, key, value)

        cls.app_path = f'/db/apps/{cls.app_name}'

        rpc_string = f'http://{cls.username}:{cls.password}'
        rpc_string += f'@{cls.address}:{cls.port}/exist/xmlrpc'

        cls.rpc = xmlrpc.client.ServerProxy(
            rpc_string, encoding='UTF-8', verbose=False
        )

        cls.xqueries = cls._get_xqueries_from_exist()
        cls._build_xquery_gets_as_methods()

    @classmethod
    def _get_xqueries_from_exist(cls):
        desc = cls.rpc.getCollectionDesc(cls.app_path)
        xqueries = [d['name'].replace('.xql', '')
                    for d
                    in desc['documents']
                    if d['name'].endswith('.xql')]
        return xqueries

    @classmethod
    def _build_xquery_gets_as_methods(cls):
        for xquery in cls.xqueries:

            async def func(self, *x, **y):
                self.logger.debug('function called')
                url = self._build_xquery_url(xquery, *x, **y)         
                
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://api.github.com/events') as resp:
                        print(resp.status)
                        print(await resp.text())


            setattr(cls, xquery, func)

    def _build_xquery_url(self, xquery, *args, **kwargs):
        '''
        Builds query url from xquery name and parameters
        to pass as GET variables

        Parameters can be passed as single dict,
        or as keyword arguments.

        (Dict takes precedence over keywords)
        '''
        url = [f"http://{self.address}"]
        if self.port:
            url.append(f":{self.port}")
        url.append(f"/exist/apps/{self.app_name}/{xquery}.xql")
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
