import sys, os, codecs, vertex, face, edge, geompreds, time
import numpy as np
import matplotlib.pyplot as plt


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

def ccw_edge(e):
	next_edge = e.origin_next()
	while next_edge != e:
		c1 = rightof(next_edge.origin_next().destination(), next_edge)
		c2 = rightof(next_edge.origin_previous().destination(), next_edge)
		if not c1 and not c2:
			return next_edge
		next_edge = next_edge.origin_next()
	return next_edge

def cw_edge(e):
	next_edge = e.origin_next()
	while next_edge != e:
		c1 = leftof(next_edge.origin_next().destination(), next_edge)
		c2 = leftof(next_edge.origin_previous().destination(), next_edge)
		if not c1 and not c2:
			return next_edge
		next_edge = next_edge.origin_next()
	return next_edge

def DT2(point_set, vertical=True):
	""" returns two.edge_list, le and re, which are the counterclockwise convex hull
		edge out of the leftmost vertex and the clockwise convex hull edge out of the
		rightmost vertex, respectively. """
	if len(point_set) == 2:
		a = edge.quad_edge().edge_list[0]
		origin, destination = vertex.vertex(), vertex.vertex()
		origin.coordinates, origin.id = point_set[0][0:2], point_set[0][2]
		destination.coordinates, destination.id = point_set[1][0:2], point_set[1][2]
		a.set_origin(origin)
		a.set_destination(destination)
		a.set_left(face.face())
		a.set_right(a.get_left())
		vertex_list = [origin, destination]
		return [a, a.symmetrical(), vertex_list]

	elif len(point_set) == 3:
		s1, s2, s3 = vertex.vertex(), vertex.vertex(), vertex.vertex()
		s1.coordinates, s2.coordinates, s3.coordinates = point_set
		s1.coordinates, s1.id = point_set[0][:2], point_set[0][2]
		s2.coordinates, s2.id = point_set[1][:2], point_set[1][2]
		s3.coordinates, s3.id = point_set[2][:2], point_set[2][2]
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
		vertices = [s1, s2, s3]
		if ccw(s1.coordinates, s2.coordinates, s3.coordinates):
			c = connect(b, a)
			return [a, b.symmetrical(), vertices]
		elif ccw(s1.coordinates, s3.coordinates, s2.coordinates):
			c = connect(b, a)
			return [c.edge_list[0].symmetrical(), c.edge_list[0], vertices]
		else:
			return [a, b.symmetrical(), vertices]

	else:
		if vertical:
			m = np.median(point_set[:,0])
			L, R = np.array([p for p in point_set if p[0] < m]), np.array([p for p in point_set if p[0] >= m])
			ldo, ldi, vertex_left = DT2(L, vertical=False)
			rdi, rdo, vertex_right = DT2(R, vertical=False)
		else:
			m = np.median(point_set[:,1])
			L, R = np.array([p for p in point_set if p[1] < m]), np.array([p for p in point_set if p[1] >= m])
			ldo, ldi, vertex_left = DT2(L, vertical=True)
			rdi, rdo, vertex_right = DT2(R, vertical=True)

		if not vertical:
			lower_max, upper_min = vertex_left[0], vertex_right[0]
			global_x_maximum, global_x_minimum = vertex_left[-1], vertex_left[-1]
			for i in range(len(R)):
				if vertex_right[i].coordinates[0] < global_x_minimum.coordinates[0]:
					global_x_minimum = vertex_right[i]
				elif vertex_right[i].coordinates[0] > global_x_maximum.coordinates[0]:
					global_x_maximum = vertex_right[i]
				if vertex_right[i].coordinates[1] < upper_min.coordinates[1]:
					upper_min = vertex_right[i]
			for i in range(len(L)):
				if vertex_left[i].coordinates[0] < global_x_minimum.coordinates[0]:
					global_x_minimum = vertex_left[i]
				elif vertex_left[i].coordinates[0] > global_x_maximum.coordinates[0]:
					global_x_maximum = vertex_left[i]
				if vertex_left[i].coordinates[1] > lower_max.coordinates[1]:
					lower_max = vertex_left[i]
			ldi = cw_edge(lower_max.edge)
			rdi = ccw_edge(upper_min.edge)
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
		if not vertical:
			ldo = ccw_edge(global_x_minimum.edge)
			rdo = cw_edge(global_x_maximum.edge)
		vertex_list = vertex_left + vertex_right
	return [ldo, rdo, vertex_list]

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

def main2(file):
	ps = parse_and_sort(file) 
	ps = np.array(ps)
	start = time.time()
	qe1, qe2, vertices = DT2(ps)
	end = time.time()
	print("Alternating cuts took (seconds):")
	print(end - start)
	qe1, qe2 = qe1.quad_edge, qe2.quad_edge
	faces = find_faces(qe1,qe2)
	ele_file(file, faces, 2)





