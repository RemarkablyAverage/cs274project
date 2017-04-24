from vertex import vertex
import face

class edge:
	def __init__(self): 
		self.vertex, self.index, self.next, self.quad_edge, self.face = 5*[None]

	def rotation(self):
		if self.index < 3: return self.quad_edge.edge_list[self.index + 1]
		else: return self.quad_edge.edge_list[self.index - 3]

	def inverse_rotation(self):
		if self.index > 0: return self.quad_edge.edge_list[self.index - 1]
		else: return self.quad_edge.edge_list[self.index  + 3]

	def symmetrical(self):
		if self.index < 2: return self.quad_edge.edge_list[self.index + 2]
		else: return self.quad_edge.edge_list[self.index - 2]

	def set_left(self, left):
		self.inverse_rotation().face = left
		left.add_edge(self)

	def get_left(self):
		return self.inverse_rotation().face

	def set_right(self, right):
		self.rotation().face = right
		right.add_edge(self)
	
	def get_right(self):
		return self.rotation().face
		
	def origin_next(self):
		return self.next

	def origin_previous(self):
		return self.rotation().origin_next().rotation()

	def destination_next(self):
		return self.symmetrical().origin_next().symmetrical()

	def left_next(self):
		return self.inverse_rotation().origin_next().rotation()

	def left_previous(self):
		return self.origin_next().symmetrical()

	def right_next(self):
		return self.rotation().origin_next().inverse_rotation()

	def right_previous(self):
		return self.symmetrical().origin_next()

	def origin(self):
		return self.vertex

	def destination(self):
		return self.symmetrical().vertex

	def set_origin(self, origin): #origin is a vertex
		self.vertex = origin
		self.vertex.add_edge(self)

	def set_destination(self, destination):
		self.symmetrical().vertex = destination
		self.symmetrical().vertex.add_edge(self.symmetrical())


class quad_edge:
	def __init__(self): #.edge_list is an array ofedges
		self.edge_list = [edge() for _ in range(4)]
		for i in range(len(self.edge_list)):
			self.edge_list[i].index = i
			self.edge_list[i].quad_edge = self
		# instantiate circular links
		self.edge_list[0].next = self.edge_list[0]
		self.edge_list[1].next = self.edge_list[3]
		self.edge_list[2].next = self.edge_list[2]
		self.edge_list[3].next = self.edge_list[1]





