from yacs.config import CfgNode as CN

_C = CN()
_C.DBPATH = '/' # path to database file, if not existing new db is created

# import data related params
_C.IMPORT = CN()
# folder containing wav files to be analyzed
_C.IMPORT.FOLDER = "/mnt/c/Users/nicop/bachelorarbeit/daten/Fledermausrufe/Auswahl_Skiba/"
_C.IMPORT.NAME = "skiba" # name of the source to be used in database
_C.IMPORT.CSVPATH = "descriptions/skiba.csv" # csv file containing filename species mappings
_C.IMPORT.SKIP = "skip" # string in description file to indicate file should be skipped

# processing related params
_C.PROCESSING = CN()
_C.PROCESSING.METHOD = 0 # 0: extract single calls, 1: cut spec in equal parts
_C.PROCESSING.SR = 44100 # target sampling rate of the signals
_C.PROCESSING.BANDPASS = True
# high and low cut frequencies for butter bandpass filter. 
# Default bandpass 1.5 to 12 khZ ~ 15 khZ to 120 khZ considering the time expansion
_C.PROCESSING.LOWCUT = 1500
_C.PROCESSING.HIGHCUT = 12000
_C.PROCESSING.TARGETLENGTH = 10 # target length for processing without extraction in seconds
_C.PROCESSING.ROUND = True # round final audio data to safe space

# call extraction related params
_C.EXTRACTION = CN()
_C.EXTRACTION.METHOD = 0 # 0: noise reduce, 1: iterative
_C.EXTRACTION.THRESHOLD = 0.1 # fixed threshold for noise reduction method
# around each extracted call the intervall [neg_offset, pos_offset] is cut out
# defaults to [2000, 2410] / 4410 samples ~ 10 ms with SR=44100
_C.EXTRACTION.POS_OFFSET = 2410
_C.EXTRACTION.NEG_OFFSET = 2000
_C.EXTRACTION.ANALENGTH = 30

# parameters used in STFT
_C.STFT = CN()
_C.STFT.NFFT = 512
_C.STFT.NOVERLAP = 480
_C.STFT.NPERSEG = 512

def get_cfg_defaults():
	return _C.clone()

def _update_cfg_from_file(cfg, cfg_file):
	cfg.defrost()
	cfg.merge_from_file(cfg_file)
	cfg.freeze()
	return cfg

def get_cfg(cfg_file):
	cfg = get_cfg_defaults()
	cfg = _update_cfg_from_file(cfg, cfg_file)
	return cfg