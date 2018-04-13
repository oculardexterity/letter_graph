import aiohttp
import asyncio
import logging
import re
from syncer import sync
import urllib.parse
import xmlrpc.client
import warnings


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ExistError(Exception):
    pass

class ExistQueryNotFoundError(Exception):
    pass

class ExistQueryExceptionError(Exception):
    pass

class ExistCollectionNotFoundError(Exception):
    pass

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

    # Write tests for this...!
    @classmethod
    def _raise_existman_exceptions_from_exist_rpc(cls, error):
        if re.findall(r'collection\b.*\bnot found', str(error)):
            raise ExistCollectionNotFoundError(f'"{cls.app_name}" not found in eXist.') from None
        raise ExistError('There was a non-identifiable error with eXist-XMLRPC connection.') from None

    # And test to make sure this throws errors if not there...!
    @classmethod
    def _get_xqueries_from_exist(cls):
        try:
            desc = cls.rpc.getCollectionDesc(cls.app_path)
        except xmlrpc.client.Fault as e:
            cls.logger.debug(e)
            cls._raise_existman_exceptions_from_exist_rpc(e)
            
        xqueries = [d['name'].replace('.xql', '')
                    for d
                    in desc['documents']
                    if d['name'].endswith('.xql')]
        return xqueries

    @classmethod
    def _build_xquery_gets_as_methods(cls):
        for xquery in cls.xqueries:
            func = cls._build_xquery_getter_func(xquery)
            setattr(cls, xquery, func)
            sync_func = sync(func)
            setattr(cls, f'{xquery}_sync', sync_func)

    @classmethod
    def _build_xquery_getter_func(cls, xquery):

        async def func(self, *x, **y):
            self.logger.debug('function called')
            url = self._build_xquery_url(xquery, *x, **y)
            self.logger.debug('URL:', url)
            async with aiohttp.ClientSession() as session:
                resp = await session.get(url)
                self.validate_resp_status(xquery, resp.status)
                resp_text = await resp.text()
                self.validate_resp_text(xquery, resp_text)
            return resp_text

        return func

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

    def validate_resp_status(self, xquery, status):
        if status == 404:
            raise ExistQueryNotFoundError(f'{xquery}.xql not found.')

    def validate_resp_text(self, xquery, text):
        text = text.replace('<?xml version="1.0" ?>', '').strip()
        if text.startswith('<exception>') and text.endswith('</exception>'):
            msg = re.findall(r'(?<=<message>).*?(?=\s?</message>)', text)[0]
            raise ExistQueryExceptionError(msg)







if __name__ == '__main__':
    import sys
    sys.path.append('../letter_graph')
    from config import EXIST_CONFIG
    #print(EXIST_CONFIG)

    ExistManager.setup(EXIST_CONFIG)

    exist = ExistManager()

    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(exist.test(name='John', thing='strawberries'))
    print(res)


