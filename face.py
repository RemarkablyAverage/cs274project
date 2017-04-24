class face:
	def __init__(self): 
		self.position, self.edge = None, None

	def add_edge(self, e):
		self.edge = e

	def get_edge(self):
		return self.edge

	def set_edges(self, e):
		e.set_left(self)
		next_edge = e.left_next()
		while next_edge != e:
			next_edge.set_left(self)
			next_edge = next_edge.left_next()