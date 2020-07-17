import os
import sys

indir = sys.argv[1]
outfile = sys.argv[2]

files = [ os.path.join(indir, i) for i in os.listdir(indir) ]

f = open( outfile, "w" )
f.write( "\n".join( files ) )
f.close()