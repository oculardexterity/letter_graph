let s = new sigma({
			
			renderer: {
			    container: 'graph_container', 
			    type: 'webgl'

			},
			settings: {
					drawLabels: true,
			    nodesPowRatio: 0.0007,
			    rescaleIgnoreSize: false,
			    autoResize: false,
			    zoomMax: 3000,
			    minNodeSize: 6,
			    maxNodeSize: 7,
			    maxEdgeSize: 0.5,
			    labelThreshold: 10,
			   // nodeActiveLevel: 5,
			    zoomMin: 0.01,
			    shortLabelsOnHover: true

			}
	});


function build_graph(resp_json) {
	
	for (let node of resp_json.nodes) {
		s.graph.addNode(node);
	}

	for (let edge of resp_json.edges) {
		s.graph.addEdge(edge);
	}

	s.refresh();


}

fetch('json/graph/default')
	.then((resp) => resp.json())
	.then((resp_json) => build_graph(resp_json))





//sigmaWebgl.
