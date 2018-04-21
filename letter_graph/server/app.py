import asyncio
from exist_manager import ExistManager
from graph import Graph
import os.path
from sanic import Sanic
from sanic import response
from signal import signal
from signal import SIGINT
import sys
import uvloop


sys.path.append('../letter_graph')
from config import EXIST_CONFIG

# Set up ExistManager
ExistManager.setup(EXIST_CONFIG)
#ExistManager.copy_xqueries_to_exist(reSetup=True)

# Create app
app = Sanic()

# Create an ExistManager instance
exist = ExistManager()

# Load the base graph for convenience
# n.b. use synchronous version for pre-emptive setup
default_graph = Graph.from_graphml(exist.letters_base_graph_sync())


# Funky little class that could probably be a function?
class Client:
    def __init__(self, root=None):
        self.root = root or 'letter_graph/client'

    def __call__(self, client_file):
        return os.path.join(self.root, client_file)

client = Client()



############################
#       Begin routes       #
############################

@app.get('/')
async def index(request):
    return await response.file(client('index.html'))


@app.get('/graph/<graph_type>')
async def graph(request, graph_type='default'):
    resp = await default_graph.to_sigmajs_json()
    return response.json(resp)


@app.get('/test')
def test(request):
    return response.json({'hello': 'world'})


@app.get('/exist_test')
async def exist_test(request):
    result = await exist.letters_test(name='John', other='Ian')
    return response.text(result)



def main(): 
    # Some comments so I remember how this works as it's non-standard example
    # Needs to be done like this so Graph.py can use event loop for layout
    # task.
    
    # So we set the app-wide event loop to uvloop
    asyncio.set_event_loop(uvloop.new_event_loop())

    # Then we create a server
    server = app.create_server(host="0.0.0.0", port=8000)

    # Then we get the event loop
    loop = asyncio.get_event_loop()

    # And run the server on the loop
    task = asyncio.ensure_future(server)

    # Then do if ctrl + c?
    signal(SIGINT, lambda s, f: loop.stop())
    
    # And then run the asyncio event loop
    try:
        loop.run_forever()
    except:
        loop.stop()


if __name__ == '__main__':
    main()
