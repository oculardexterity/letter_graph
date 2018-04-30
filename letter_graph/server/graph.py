import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from graph_tool import Graph as GT_Graph
from graph_tool import load_graph as GT_load_graph
import graph_tool.draw
import hashlib
from io import StringIO
import logging
import json
import os
import pickle
import weakref

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



'''

### TO DO: farm out graph colours to a config file--- or to JavaScript?
### 


'''



class Graph:

    def __init__(self, g):
        self.g = g

    @classmethod
    def from_graphml(cls, file):
        # Implements this as a class constructor method rather than
        # how graph_tool does it (as a random function?)
        if type(file) == str:
            file = StringIO(file)

        g = GT_load_graph(file, fmt='graphml')
        return cls(g)

    def __getattr__(self, attr):
        return getattr(self.g, attr)

    def hash_graph(self):
        nodes_string = str([self.g.vp.v_id[v] for v in self.vertices()])
        edges_string = str([self.g.ep.e_id[e] for e in self.edges()])
        string_to_hash = ' '.join([nodes_string, edges_string])
        graph_hash = hashlib.md5(string_to_hash.encode('utf-8')).hexdigest()
        return graph_hash


    async def get_positions(self, refresh_layout=False):
        graph_hash = self.hash_graph()
        file_path = f'graph_positions/{graph_hash}.layout'

        if os.path.isfile(file_path) and not refresh_layout:
            with open(file_path, 'rb') as f:
                positions = pickle.load(f)
            
            positions._PropertyMap__base_g = weakref.ref(self.g)
            #self.g.vp.positions = positions  # Don't need to assign; better not to?
            return positions


        else:
            loop = asyncio.get_event_loop()
            positions = await loop.run_in_executor(
                ThreadPoolExecutor(max_workers=20),
                partial(graph_tool.draw.sfdp_layout, self.g, gamma=4.0, mu=20.0, mu_p=10.0, C=2, verbose=True))

            with open(file_path, 'wb') as f:
                pickle.dump(positions, f)

            #self.g.vp.positions = positions  # Don't need to assign; better not to?
            return positions



    # TO REWRITE for Graph-Tool graph...
    async def to_sigmajs_json(self):
        output = {'nodes': [], 'edges': []}
        positions = await self.get_positions()
        for v in self.g.vertices():
            node = {}
            node['id'] = self.g.vp.v_id[v]
            node['x'], node['y'] = positions[v]
            node['size'] = 0.5
            try:
                pass
                node['color'] = {'Person': '#A33643', 'Letter': '#236467'}[self.g.vp.type[v]]
            except KeyError:
                pass

            node['data'] = {}
            for key in self.g.vp.keys():
                try:
                    node['data'][key] = self.g.vp[key][v]
                except KeyError:
                    pass

            output['nodes'].append(node)
            
        for e in self.g.edges():
            edge = {}
            edge['id'] = self.g.ep.e_id[e]
            edge['color'] = {'SenderToLetter': '#A33643', 'LetterToRecipient': '#236467'}[self.g.ep.edge_type[e]]
            edge['source'] = self.g.vp.v_id[e.source()]
            edge['target'] = self.g.vp.v_id[e.target()]
            edge['data'] = {}
            for key in self.g.ep.keys():
                try:
                    edge['data'][key] = self.g.ep[key][e]
                except KeyError:
                    pass

            output['edges'].append(edge)

        return output
            



        '''
        output = {"nodes": [], "edges": []}
        positions = await self.get_positions(refresh_layout=True) # Change this not to redraw
        for key, data in self.nodes(data=True):
            node = {}
            node['data'] = data
            node['id'] = key
            node['x'], node['y'] = positions[key]
            node['color'] = {'Person': '#A33643', 'Letter': '#236467'}[data['type']]
            node['size'] = 0.5
            output["nodes"].append(node)

        for source, target, data in self.edges(data=True):
            edge = data
            edge["id"] = f'{source}{target}'
            edge["source"] = source
            edge["target"] = target
            edge['color'] = {'SenderToLetter': '#A33643', 'LetterToRecipient': '#236467'}[data['edge_type']]
            output["edges"].append(edge)

        return output

        '''