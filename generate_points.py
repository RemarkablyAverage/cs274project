import numpy as np

print "generating points with the bounding box x = [-1, 1] and y = [-0.1, -0.1] at uniform random for 5000 total points"

def generate_points(x_bounds=[-1,1], y_bounds=[-.01, .01], num_points=5000):
	x = np.random.uniform(x_bounds[0], x_bounds[1], num_points)
	y = np.random.uniform(y_bounds[0], y_bounds[1], num_points)
	return zip(x, y)

def write_node(points, num_points=5000):
	f = open("g.node", "w+")
	header, c = str(num_points) + " 2 0 0\n", 1
	f.write(header)
	for point in points:
		f.write(str(c) + " " + " ".join([str(p) for p in point]) + "\n")
		c += 1
	return

p = generate_points()
write_node(p)

print "done generating points and saved file as g.node"