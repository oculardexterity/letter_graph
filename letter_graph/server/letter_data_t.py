from exist_manager import ExistManager
from graph import Graph

import sys

sys.path.append('../letter_graph')
from config import EXIST_CONFIG

# Set up ExistManager
ExistManager.setup(EXIST_CONFIG)
ExistManager.copy_xqueries_to_exist(reSetup=True)


exist = ExistManager()

graphml = exist.letters_base_graph_sync()

#print(graphml)
graph = Graph.from_graphml(graphml)



#print()






'''
graph = nx.read_graphml(StringIO(graphml))
positions = get_positions(graph)

output = build_graph_json(graph, positions)


    
with open("output.json", 'w') as f:
    f.write(json.dumps(output))
'''