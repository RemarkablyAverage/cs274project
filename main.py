import sys
print "READ: please read the writeup's instructions for details"
print ""
print "Make sure all proper libraries are installed (in the instructions) and the files to run are in the same folder as the code"
print "If generating points, run the script first to generate points and then run this with the correct parameters"



if len(sys.argv) != 4:
	print "insufficent arguments"
else: 
	from DT1 import *
	from DT2 import *

	"""
	Parameters: 
	enter the following
	argument 1 - file name
	argument 2 - 'v' for vertical cuts, 'a' for alternating cuts
	argument 3 - plot visualization 't' for plot, 'f' for no plot
	"""
	file_name, vertical, viz = sys.argv[1], sys.argv[2], sys.argv[3]
	if vertical == 'v':
		main()
		if viz == 't':
			from visualize import *
			main3(file_name, 1)
	if vertical == 'a':
		main2(file_name)
		if viz == 't':
			from visualize import *
			main3(file_name, 2)



