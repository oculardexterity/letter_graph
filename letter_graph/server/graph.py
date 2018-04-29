import asyncio
from concurrent.futures import ThreadPoolExecutor
from fa2 import ForceAtlas2
from functools import partial
import hashlib
from io import StringIO
import logging
import json
import networkx as nx
import os
import pickle

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


forceatlas2 = ForceAtlas2(
                          # Behavior alternatives
                          outboundAttractionDistribution=False,  # Dissuade hubs
                          linLogMode=False,  # NOT IMPLEMENTED
                          adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
                          edgeWeightInfluence=1.0,

                          # Performance
                          jitterTolerance=1.0,  # Tolerance
                          barnesHutOptimize=True,
                          barnesHutTheta=1.2,
                          multiThreaded=False,  # NOT IMPLEMENTED

                          # Tuning
                          scalingRatio=20.0,
                          strongGravityMode=True,
                          gravity=50.0,

                          # Log
                          verbose=True)



class Graph(nx.Graph):
    
    @classmethod
    def create_instance(cls, baseObject):
        # Turn an nx.from_graphml Graph instance into the class itself
        instance =  __class__()
        instance.__class__ = type(baseObject.__class__.__name__,
                              (instance.__class__, baseObject.__class__),
                              {})
        instance.__dict__ = baseObject.__dict__
        return instance


    @classmethod
    def from_graphml(cls, file):
        # Implements this as a class constructor method rather than
        # how nx does it (as a random function?)
        if type(file) == str:
            file = StringIO(file)

        baseObject = nx.read_graphml(file)
        return cls.create_instance(baseObject)


    def hash_graph(self):
        nodes_string = str(self.nodes)
        edges_string = str(self.edges)
        string_to_hash = ' '.join([nodes_string, edges_string])
        graph_hash = hashlib.md5(string_to_hash.encode('utf-8')).hexdigest()
        return graph_hash


    async def get_positions(self, refresh_layout=False):
        graph_hash = self.hash_graph()
        file_path = f'graph_positions/{graph_hash}.layout'
        
        if os.path.isfile(file_path) and not refresh_layout:
            with open(file_path, 'rb') as f:
                return pickle.load(f)

        else:
            loop = asyncio.get_event_loop()
            
            # The async task
            positions = await loop.run_in_executor(
                ThreadPoolExecutor(max_workers=20), 
                #partial(forceatlas2.forceatlas2_networkx_layout, self, pos=None, iterations=2000)
                partial(nx.nx_pydot.pydot_layout, self, prog='sfdp', args="-Ln1000 -Lg -LO")

                #partial(nx.spring_layout, self, pos=None, iterations=50)
                )
            '''
            positions = await loop.run_in_executor(
                ThreadPoolExecutor(max_workers=20), 
                partial(forceatlas2.forceatlas2_networkx_layout, self, pos=positions, iterations=100)

                #partial(nx.spring_layout, self, pos=positions)
                )
            '''

# positions = forceatlas2.forceatlas2_networkx_layout(G, pos=None, iterations=2000)
            with open(file_path, 'wb') as f:
                pickle.dump(positions, f)
            return positions


    async def to_sigmajs_json(self):
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


    async def __add__(self, other_graph):
        """ Think out the logic for merging two graphs """
        new_graph = nx.Graph()
        pass
        