from exist_manager import ExistManager
import os.path
from sanic import Sanic
from sanic import response
import sys


sys.path.append('../letter_graph')
from config import EXIST_CONFIG

# Set up ExistManager
ExistManager.setup(EXIST_CONFIG)
ExistManager.copy_xqueries_to_exist(reSetup=True)

# Create app
app = Sanic()



# Funky little class that could probably be a function?
class Client:
    def __init__(self, root=None):
        self.root = root or 'letter_graph/client'

    def __call__(self, client_file):
        return os.path.join(self.root, client_file)

client = Client()




exist = ExistManager()





@app.get('/')
async def index(request):
    return await response.file(client('index.html'))



@app.get('/test')
def test(request):
    return response.json({'hello': 'world'})


@app.get('/exist_test')
async def exist_test(request):
    result = await exist.another_test(name='John', other='Ian')
    return response.text(result)



def main():

    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()
