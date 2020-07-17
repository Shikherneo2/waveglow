import os
import sys
import numpy as np
import matplotlib.pyplot as plt

logfile = sys.argv[1]

lines = open( logfile, "r" ).read().split("\n")

losses = []

for i in range( len(lines) ):
	if lines[i].find("Speed")!=-1:
		if( lines[i+1].find(":")!=-1 ):
			g = float(lines[i+1].split(":")[1].strip())
			if( g<-4 ):
				losses.append( g )

losses_array = [ np.mean(losses[i:i+40]) for i in range(len(losses)-40) ]
plt.plot( losses_array )
plt.show()
