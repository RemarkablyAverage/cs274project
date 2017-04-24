class vertex:
	def __init__(self): 
		self.coordinates, self.edge, self.id = 3*[None]

	def add_edge(self, e):
		self.edge = e