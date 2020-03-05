import librosa
import os
import numpy as np
from tqdm import tqdm

infilename = "/home/kiwiuser/sgupta/unet/glow/dataset/train_filtered-lambda.txt"
outdir = "/home/kiwiuser/sgupta/unet/data/npy_wavs"

infile_data = open(infilename,"r").read().split("\n")
wavs = [ i.strip() for i in infile_data]

for wav in wavs:
    x,_ = librosa.core.load(wav)
    npy_filename = "_".join( wav.split("/")[-2:] ).replace(".wav",".npy")
    np.save( os.path.join(outdir, npy_filename), x  )

