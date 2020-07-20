# *****************************************************************************
#  Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#      * Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#      * Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#      * Neither the name of the NVIDIA CORPORATION nor the
#        names of its contributors may be used to endorse or promote products
#        derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL NVIDIA CORPORATION BE LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# *****************************************************************************\
import os
import sys
import json
import torch
import random
import librosa
import argparse
import numpy as np
import torch.utils.data

import speech_utils

from tacotron2_layers import TacotronSTFT

MAX_WAV_VALUE = 32768.0

def files_to_list(filename):
	"""
	Takes a text file of filenames and makes a list of filenames
	"""
	with open(filename, encoding='utf-8') as f:
		files = f.readlines()

	files = [f.rstrip() for f in files]
	return files

def load_wav_to_torch(full_path, sampling_rate_param):
	"""
	Loads wavdata into torch array
	"""
	data, sampling_rate = librosa.core.load( full_path, sr=sampling_rate_param )
	return torch.from_numpy(data).float(), sampling_rate


class Mel2Samp(torch.utils.data.Dataset):
	"""
	This is the main class that calculates the spectrogram and returns the
	spectrogram, audio pair.
	"""
	def __init__(self, training_files, segment_length, filter_length,
				 hop_length, win_length, sampling_rate, mel_fmin, mel_fmax):
		self.audio_files = files_to_list(training_files)
		self.mel_segment_length = 63
		self.npy_wav_dir = "/home/sdevgupta/mine/data/npy_wavs"

		# Fix to remove files smaller than sample length
		# for file in self.audio_files:
		# 	audio_data, sample_r = load_wav_to_torch(file, sampling_rate)
		# 	if audio_data.size(0) < segment_length:
		# 		self.audio_files.remove(file)

		random.seed(1234)
		random.shuffle(self.audio_files)
		self.segment_length = segment_length
		self.sampling_rate = sampling_rate

	# Get mel in OpenSeq2Seq format
	def get_mel(self, audio):
		return speech_utils.get_speech_features( 
								audio,
								self.sampling_rate,
								80, 
								features_type="mel",
								n_fft=1024,
								hop_length=256,
								mag_power=1,
								feature_normalize=False,
								mean=0.,
								std=1.,
								data_min=1e-5,
								mel_basis=self.mel_basis_p).T


	def get_mel_waveglow(self, audio):
		audio_norm = audio 
		audio_norm = audio_norm.unsqueeze(0)
		audio_norm = torch.autograd.Variable(audio_norm, requires_grad=False)
		melspec = self.stft.mel_spectrogram(audio_norm)
		melspec = torch.squeeze(melspec, 0)
		return melspec


	def __getitem__(self, index):
		filename = self.audio_files[index]
		audio = torch.from_numpy(np.load( os.path.join(self.npy_wav_dir, os.path.basename(filename)) ))
		mel = np.load(filename).T
		
		# Take segment
		mel_length = mel.shape[1]
		if mel_length >= self.mel_segment_length:
			max_mel_start = max( 0, mel_length - self.mel_segment_length - 1 )
			mel_start = random.randint(0, max_mel_start)
			mel = torch.from_numpy(mel[ :,mel_start:mel_start+self.mel_segment_length ])

			audio_start = mel_start*256
			audio_end = audio_start + self.segment_length
			audio = audio[ audio_start:audio_end ]

		else:
			mel = torch.from_numpy( mel )
			mel = torch.nn.functional.pad( mel, (-11.512925, self.mel_segment_length - mel_length), 'constant' ).data

		audio = audio/abs(audio).max() * 0.5
		audio = torch.nn.functional.pad( audio, (0, self.segment_length - audio.size(0)), 'constant' ).data
		return ( mel, audio )

	def __len__(self):
		return len( self.audio_files )

# ===================================================================
# Takes directory of clean audio and makes directory of spectrograms
# Useful for making test sets
# ===================================================================
if __name__ == "__main__":
	# Get defaults so it can work with no Sacred
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', "--filelist_path", required=True)
	parser.add_argument('-c', '--config', type=str, help='JSON file for configuration')
	parser.add_argument('-o', '--output_dir', type=str, help='Output directory')
	parser.add_argument('-s', '--sample_rate', type=int, help='sample rate')
	args = parser.parse_args()

	with open(args.config) as f:
		data = f.read()
	data_config = json.loads(data)["data_config"]
	mel2samp = Mel2Samp(**data_config)

	filepaths = files_to_list(args.filelist_path)

	# Make directory if it doesn't exist
	if not os.path.isdir(args.output_dir):
		os.makedirs(args.output_dir)
		os.chmod(args.output_dir, 0o775)

	for filepath in filepaths:
		audio, sr = load_wav_to_torch(filepath, sampling_rate_param=args.sample_rate)
		melspectrogram = mel2samp.get_mel(audio)
		filename = os.path.basename(filepath)
		new_filepath = os.path.join( args.output_dir, filename.replace(".wav", ".npy") ) 
		np.save( new_filepath, melspectrogram.numpy() )
