import os
import sys
import numpy as np
import pickle

#wav_location = "/home/sdevgupta/mine/data/npy_wavs"

#mel_files = [ i for i in open("/home/sdevgupta/mine/waveglow/dataset/new_gta_list.txt").read().split("\n") if i.strip()!=""]

#lengths = [ [os.path.basename(i), np.load(i).shape[0], np.load(os.path.join(wav_location, os.path.basename(i))).shape[0]] for i in mel_files ]

#mel_lengths = [ i[:2] for i in lengths ]
#pickle.dump(lengths, open("mel_wav_lengths.pickle","wb"))

gg = []

lengths= pickle.load(open( "mel_wav_lengths.pickle","rb") )
for i in lengths:
    if -int( (i[1]*256 - i[2])/256) >=4:
        gg.append(i)

print(len(gg))
for i in gg[:20]:
    print( i )

pickle.dump( gg, open("less_mel_than_wavs.pickle","wb") )
