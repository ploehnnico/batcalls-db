import pydub
import numpy as np
from batcalls_db import analysis
import warnings
from typing import List
import torchaudio

def process_file(filepath, cfg):
	"""
	Reads and processes a single wav file
	"""
	# read wav file
	sound = pydub.AudioSegment.from_wav(filepath)

	# preprocessing of soundfile
	data, duration, mean, std, = preprocessing(sound, cfg)

	# cut out calls
	calls = cut_calls(data, duration, cfg)

	# transform data back to non standardized scale
	calls = (calls + mean) * 32768.0 * std

	if cfg.PROCESSING.ROUND:
		calls = np.round(calls).astype(np.int16)
	return calls

def process_without_cut(filepath, cfg):
	"""
	Processes a single wav file without extracting the calls. 
	The file is split into equal sized parts with maximal length,
	that is not longer as the target length.
	"""
	waveform, sr = torchaudio.load(filepath)
	if sr != cfg.PROCESSING.SR:
		resample = torchaudio.transforms.Resample(orig_freq=sr, 
				   new_freq=cfg.PROCESSING.SR)
		waveform = resample(waveform)
		sr = cfg.PROCESSING.SR
	
	# remove mean
	waveform = (waveform - waveform.mean()).numpy()

	# divide into equal parts
	samples = waveform.shape[1]
	nparts = np.ceil(samples / (cfg.PROCESSING.TARGETLENGTH * sr))
	n = np.floor(samples / nparts).astype(np.int)
	parts = [waveform.ravel()[i-1:i+n -1] for i in range(1, int(n*nparts), n)]
	assert len(parts) == nparts, "Fuck"
	return parts

def preprocessing(sound, cfg):
	"""
	Preprocessing of a sound signal for analysis: 
	resampling -> bandpass filter -> standardization
	"""
	# Resample sound to 44 khz / 16 bit
	sr = cfg.PROCESSING.SR
	sound = sound.set_frame_rate(sr)
	sound = sound.set_sample_width(2)

	duration = sound.duration_seconds
	assert duration != 0, 'Duration is 0, Memory error !' # TODO: catchable exception...

	# Get samples and transform to float32
	data = np.asarray(sound.get_array_of_samples())
	data = data.astype(np.float32, order='C') / 32768.0

	# Apply bandpass filter
	if cfg.PROCESSING.BANDPASS:
		data = analysis.butter_bandpass_filter(data, cfg, 5)

	# Standardize data
	mean = np.mean(data)
	std = np.std(data)
	data = (data -mean) / std

	return data, duration, mean, std

def cut_calls(data : np.ndarray, duration: float, cfg) -> List: 
	"""
	Returns list of calls a 4410 samples around each local peak
	"""
	sr = cfg.PROCESSING.SR
	len_ana = cfg.EXTRACTION.ANALENGTH
	pos_offset = cfg.EXTRACTION.POS_OFFSET
	neg_offset = cfg.EXTRACTION.NEG_OFFSET

	# If duration > analysis window cut data in parts
	n =  len_ana * sr
	cuts = [data[i:i+n] for i in range(0, len(data), n)]

	result = []

	for element in cuts:
		# Compute spectrogram then get peak locations
		stft, t, _ = analysis.spectro_vor(element, cfg)
		if cfg.EXTRACTION.METHOD:
			stamps, _ = analysis.detect_peaks(duration, stft, t)
		else:
			stamps = analysis.detect_peaks_fixed(cfg.EXTRACTION.THRESHOLD,
												 stft, t)
		if np.isnan(stamps[0]): 
			length = len(element) / sr
			warnings.warn('''Peak array was NaN. Cut was probably to short 
						  to compute STFT. Cut length: %f''' %(length))
			continue
		
		# Cut out peaks
		pot_calls = analysis.get_images(element, stamps, neg_offset, 
										pos_offset)
		result.extend(pot_calls)
		
	result = np.array(result)

	return result