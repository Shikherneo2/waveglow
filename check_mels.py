import os
import sys
import numpy as np
import pickle

mel_location1 = sys.argv[1]
mel_location2 = sys.argv[2]
#wav_location = sys.argv[3]

#mel_files1 = [ os.path.join(mel_location1, i) for i in os.listdir(mel_location1) ]
#mel_files2 = [ os.path.join(mel_location2, i) for i in os.listdir(mel_location2) ]

mel_files1 = open(mel_location1).read().split("\n")
mel_files2 = open(mel_location2).read().split("\n")

mels1 = dict()
mels2 = dict()

for i in mel_files1:
    mels1[ os.path.basename(i) ] = np.load(i).shape[0]

print("Loaded 1")

for i in mel_files2:
    mels2[ os.path.basename(i) ] = np.load(i).shape[0]

print("Loaded 2")

def check_mel_lengths( mels_large, mels_smaller  ):
    ret = []
    for i in mels_smaller.keys():
        if mels_large[i]!=mels_smaller[i]:
            ret.append( [i, mels_large[i], mels_smaller[i]] )
    return ret

f = check_mel_lengths( mels1, mels2  )
print( len(f) )
pickle.dump( f, open("mel_lengths.pickle","w")  )
print( f[5:10]  )
