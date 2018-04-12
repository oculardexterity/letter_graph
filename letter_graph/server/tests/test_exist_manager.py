from grappa import should
import os.path
import sys
import unittest
from unittest import mock
import warnings


parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent)

import exist_manager

MOCK_EXIST_CONFIG = {

    'global': {
        'app_name': 'testapp',
        'data_dir': 'testapp/data',
        'xquery_path': os.path.join('letter_graph', 'server', 'xquery')
    },
    'development': {
        'address': '127.0.0.1',
        'port': '8080',
        'username': 'admin',
        'password': 'whatever'
    }
}
MEC = MOCK_EXIST_CONFIG

MOCK_EXIST_getCollectionDesc = {
    'owner': 'admin',
    'collections': ['data'],
    'documents': [
        {'name': 'test1.xql', 'owner': 'admin', 'type': 'BinaryResource', 'permissions': 493, 'group': 'dba'},
        {'name': 'test2.xql', 'owner': 'admin', 'type': 'BinaryResource', 'permissions': 420, 'group': 'dba'}
    ],
    'created': '1523354968082',
    'permissions': 493,
    'name': '/db/apps/testapp',
    'group': 'dba'
}



class TestExistManagerClassMethods(unittest.TestCase):
    '''
    Tests the pre-initialisation class methods

    '''

    def setUp(self):
        with mock.patch('xmlrpc.client.ServerProxy') as xsp:
            # Mock the xmlrpc call to describe the collection
            xsp.return_value.getCollectionDesc.return_value = MOCK_EXIST_getCollectionDesc

            # Set test-class ExistManager class to the conf'd, patched one
            self.EM = exist_manager.ExistManager

            # Configure test ExistManager class
            self.EM.setup(MOCK_EXIST_CONFIG)

    def test_configs_imported(self):
        for k, v in MOCK_EXIST_CONFIG['global'].items():
            getattr(self.EM, k) | should.be.equal.to(v)

    def test_get_xqueries_from_exist(self):
        self.EM._get_xqueries_from_exist() | should.be.equal.to(['test1', 'test2'])
        self.EM.xqueries | should.be.equal.to(['test1', 'test2'])

    def test_build_xqueries_as_methods(self):
        exist = self.EM()
        exist | should.implement.methods('test1', 'test2')


    def test_build_query_url(self):
        d = MOCK_EXIST_CONFIG['development']
        g = MOCK_EXIST_CONFIG['global']

        base_url = f"http://{d['address']}:{d['port']}/exist/apps/{g['app_name']}/test1.xql"

        # Test no args produced base url
        self.EM._build_query_url('test1') | should.be.equal.to(base_url)

        # Test single arg
        self.EM._build_query_url('test1', thing='thang') | \
            should.be.equal.to(base_url + '?thing=thang')

        # Test two args, one with spaces
        self.EM._build_query_url('test1', thing='thang', other='one two') | \
            should.be.equal.to(base_url + '?thing=thang&other=one%20two')

        # Test args passed as dict instead of keywords
        self.EM._build_query_url('test1', {'thing': 'thang'}) | \
            should.be.equal.to(base_url + '?thing=thang')

        # Test throw a warning if *args as dict and **kwargs both used 
        # (n.b. uses only *args dict in such cases)
        with warnings.catch_warnings(record=True) as ws:
            self.EM._build_query_url('test1', {'argKey': 'argValue'}, thing='thang')
            str(ws[0].message) | \
            should.be.equal.to('Args passed as dict and keyword arguments; only args used')

            
