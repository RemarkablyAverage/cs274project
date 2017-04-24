import sys, os, codecs, vertex, face, edge, geompreds, time
import numpy as np
import matplotlib.pyplot as plt

####### UTILITY FUNCTIONS

def plot(points):
	x, y = zip(*points)
	ax = min(x), max(x), min(y), max(y)
	plt.plot(x, y, '-o')
	plt.axis(ax)
	plt.show()

def scatter(points):
	x, y = zip(*points)
	plt.scatter(x, y)
	plt.show()

def plnext(edge):
	p(edge)
	c = edge.left_next()
	while c != edge:
		p(c)
		c = c.left_next()

def ponext(edge):
	p(edge)
	c = edge.origin_next()
	while c != edge:
		p(c)
		c = c.origin_next()

def p(edge):
	print("origin ", edge.origin().coordinates)
	print("destination ", edge.destination().coordinates)

def hull(l, r):
	ret = []
	ret_edge = None
	check_left = l.edge_list[0].symmetrical()
	check_right = r.edge_list[0]
	edge = check_left.symmetrical().origin_next()
	ret.append(check_left)
	while edge.vertex.coordinates != check_left.origin().coordinates:
		ret.append(edge)
		edge = edge.symmetrical().origin_next()
	ret.append(edge)
	return ret

def parse_and_sort(file):
	lines = [map(float, p.split()) for p in codecs.open(file, encoding="utf-8").read().splitlines()]
	points = list(set([(x[1], x[2], int(x[0])) for x in lines][1:]))
	sorted_x = sorted(points, key=lambda x: (x[0], x[1]))
	return sorted_x

def ele_file(file, faces, dt=1):
	if dt == 1:
		print "Creating .ele file for vertical cuts"
	if dt == 2:
		print "Creating .ele file for alternating cuts"
	fname = file[:-5] + "DT" + str(dt) + ".ele"
	f = open(fname, "w+")
	header, c = str(len(faces) - 1) + " 3 0", 0
	f.write(header)
	for face in faces:
		edge, coords = face.get_edge(), []
		while edge.left_next() != face.get_edge():
			coords.append(str(int(edge.vertex.id)))
			edge = edge.left_next()
		coords.append(str(int(edge.vertex.id)))
		if len(coords) != 3:
			continue
		else:
			c += 1
			f.write("\n" + str(c) + " ")
			f.write(" ".join(coords))
	print "Wrote file as ", fname

#global variable
s = sys.argv[1]
point_set = parse_and_sort(s)

def splice(a, b): 
	alpha = a.origin_next().rotation()
	beta = b.origin_next().rotation()
	e1 = b.origin_next()
	e2 = a.origin_next()
	e3 = beta.origin_next()
	e4 = alpha.origin_next()
	a.next, b.next, alpha.next, beta.next = e1, e2, e3, e4

def connect(e1, e2): #regular.edge_list
	e, f = edge.quad_edge().edge_list[0], face.face()
	splice(e, e1.left_next())
	splice(e.symmetrical(), e2)
	e.set_origin(e1.destination())
	e.set_destination(e2.origin())
	e.set_left(e2.get_left())
	f.set_edges(e.symmetrical())
	return e.quad_edge

def delete_edge(edge):
	e1, e2 = edge.origin_previous(), edge.symmetrical().origin_previous()
	if e1 == edge.symmetrical(): e1 = e2
	splice(e2, edge.symmetrical())
	splice(e1, edge)
	e2.get_left().set_edges(e1)
	e1.origin().add_edge(e1)
	e1.get_left().add_edge(e1)
	e2.get_left().add_edge(e2)
	edge.quad_edge = None

def rightof(p, e):
	return ccw(p.coordinates, e.destination().coordinates, e.origin().coordinates)

def leftof(p, e):
	return ccw(p.coordinates, e.origin().coordinates, e.destination().coordinates)

def ccw(p1, p2, p3):
	check = geompreds.orient2d(p1, p2, p3)
	if check > 0: return True
	else: return False

def valid(e, basel):
	return rightof(e.destination(), basel)

def incircle(a, b, c, d):
	check = geompreds.incircle(a.coordinates, b.coordinates, c.coordinates, d.coordinates)
	if check > 0: return True
	else: return False

def DT(point_set=point_set, index=0, end=len(point_set)):
	""" returns two.edge_list, le and re, which are the counterclockwise convex hull
		edge out of the leftmost vertex and the clockwise convex hull edge out of the
		rightmost vertex, respectively. """
	if end-index == 2:
		a = edge.quad_edge().edge_list[0]
		origin, destination = vertex.vertex(), vertex.vertex()
		points = point_set[index:end]
		origin.coordinates, origin.id = points[0][:2], points[0][2]
		destination.coordinates, destination.id = points[1][:2], points[1][2]
		a.set_origin(origin)
		a.set_destination(destination)
		a.set_left(face.face())
		a.set_right(a.get_left())
		return [a, a.symmetrical()]

	elif end-index == 3:
		s1, s2, s3 = vertex.vertex(), vertex.vertex(), vertex.vertex()
		points = point_set[index:end]
		s1.coordinates, s1.id = points[0][:2], points[0][2]
		s2.coordinates, s2.id = points[1][:2], points[1][2]
		s3.coordinates, s3.id = points[2][:2], points[2][2]
		a, b = edge.quad_edge().edge_list[0], edge.quad_edge().edge_list[0]
		splice(a.symmetrical(), b)
		a.set_origin(s1)
		a.set_destination(s2)
		b.set_origin(s2)
		b.set_destination(s3)
		a.set_left(face.face())
		a.set_right(a.get_left())
		b.set_left(a.get_left())
		b.set_right(a.get_left())
	
		if ccw(s1.coordinates, s2.coordinates, s3.coordinates):
			c = connect(b, a)
			return [a, b.symmetrical()]
		elif ccw(s1.coordinates, s3.coordinates, s2.coordinates):
			c = connect(b, a)
			return [c.edge_list[0].symmetrical(), c.edge_list[0]]
		else:
			return [a, b.symmetrical()]
	else:
		m = (end-index)//2 
		ldo, ldi = DT(index=index, end=index+m)
		rdi, rdo = DT(index=index+m, end=end)
		while True:
			if leftof(rdi.origin(), ldi):
				ldi = ldi.left_next()
			elif rightof(ldi.origin(), rdi):
				rdi = rdi.right_previous()
			else:
				break
		basel = connect(rdi.symmetrical(), ldi).edge_list[0]
		if ldi.origin() == ldo.origin():
			ldo = basel.symmetrical()
		if rdi.origin() == rdo.origin():
			rdo = basel
		while True:
			lcand = basel.symmetrical().origin_next()
			if valid(lcand, basel):
				while incircle(basel.destination(), basel.origin(), lcand.destination(), lcand.origin_next().destination()):
					t = lcand.origin_next()
					delete_edge(lcand)
					lcand = t
			rcand = basel.origin_previous()
			if valid(rcand, basel):
				while incircle(basel.destination(), basel.origin(), rcand.destination(), rcand.origin_previous().destination()):
					t = rcand.origin_previous()
					delete_edge(rcand)
					rcand = t
			if not valid(lcand, basel) and not valid(rcand, basel):
				break
			rc_b = valid(rcand, basel) and incircle(lcand.destination(), lcand.origin(), rcand.origin(), rcand.destination())
			if not valid(lcand, basel) or rc_b:
				basel = connect(rcand, basel.symmetrical()).edge_list[0]
			else:
				basel = connect(basel.symmetrical(), lcand.symmetrical()).edge_list[0]
	return [ldo, rdo]


def find_faces(l, r):
	#dfs traversal to get faces
	current_face = l.edge_list[0].get_left()
	queue = [current_face]
	ret = set()
	ret.add(current_face)
	while len(queue) != 0:
		current_face = queue.pop(0)
		next_face = current_face.get_edge().inverse_rotation().origin_next().symmetrical()
		while next_face != current_face.get_edge().inverse_rotation().symmetrical():
			if next_face.face not in ret:
				ret.add(next_face.face)
				queue.insert(0, next_face.face)
			next_face = next_face.symmetrical().origin_next().symmetrical()
		if next_face.face not in ret:
			ret.add(next_face.face)
			queue.insert(0, next_face.face)
	return ret

def main():
	start = time.time()
	qe1, qe2 = DT()
	end = time.time()
	print "Vertical cuts time took (seconds):"
	print(end - start)
	qe1 = qe1.quad_edge
	qe2 = qe2.quad_edge
	faces = find_faces(qe1, qe2)
	ele_file(s, faces)



