import asyncio
from concurrent.futures import ThreadPoolExecutor
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


    async def get_positions(self):
        graph_hash = self.hash_graph()
        file_path = f'graph_positions/{graph_hash}.layout'
        
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                return pickle.load(f)

        else:
            loop = asyncio.get_event_loop()

            # The async task
            positions = await loop.run_in_executor(
                ThreadPoolExecutor(max_workers=20), 
                partial(nx.spring_layout, self))

            with open(file_path, 'wb') as f:
                pickle.dump(positions, f)
            return positions


    async def to_sigmajs_json(self):
        output = {"nodes": [], "edges": []}
        positions = await self.get_positions()
        for key, data in self.nodes(data=True):
            node = {}
            node['data'] = data
            node['id'] = key
            node['x'], node['y'] = positions[key]
            output["nodes"].append(node)

        for source, target, data in self.edges(data=True):
            edge = data
            edge["source"] = source
            edge["target"] = target
            output["edges"].append(edge)

        return output