import numpy as np
import librosa
from scipy import signal
import scipy.ndimage as ndi
import noisereduce

def spectro_vor(data, cfg):
    sr = cfg.PROCESSING.SR
    if not cfg.EXTRACTION.METHOD: 
        data = noisereduce.reduce_noise(data, sr)
    f, t, stft = signal.spectrogram(data, fs=sr, nfft=cfg.STFT.NFFT,
						            noverlap=cfg.STFT.NOVERLAP, 
                                    nperseg=cfg.STFT.NPERSEG)
    stft = librosa.amplitude_to_db(np.abs(stft), ref=np.max)
    stft = np.nan_to_num(stft)
    # Normalize [0;1]
    stft = (stft - np.min(stft)) / (np.max(stft) - np.min(stft))
    return(stft, t, f)


def butter_bandpass_filter(data, cfg, order=5):
    nyq = 0.5 * cfg.PROCESSING.SR 
    low = cfg.PROCESSING.LOWCUT / nyq
    high = cfg.PROCESSING.HIGHCUT / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    y = signal.lfilter(b, a, data)
    return y

def detect_peaks_fixed(threshold, stft, t):
    # get local maxima in stft
    min_distance = 2
    size = 2 * min_distance + 1
    footprint = np.ones((size, ) * stft.ndim, dtype=bool)
    max_filter = ndi.maximum_filter(stft, footprint=footprint, mode='constant')
    local_max = max_filter == stft
    local_max &= stft > 0
    local_max_idx = np.nonzero(local_max) #peak coordinates
    local_max_val = stft[local_max_idx]
    local_max_idx = np.transpose(local_max_idx)
    local_max_t = t[local_max_idx[:, 1]]
    mask = local_max_val > threshold
        
    # get and sort peak time stamps
    time_stamps = np.sort(local_max_t[mask])

    # group time stamps if delta in between < 0.03
    delta = np.diff(time_stamps)
    idx = np.where(delta > 0.03)[0] + 1
    groups = np.split(time_stamps, idx)

    # compute mean of groups
    stamps = np.array([np.mean(group) for group in groups])
    return stamps

def detect_peaks(duration, stft, t):
    """
    Finds peaks in the spectrogram with an optimal threshold,
    so that cutting out noise is avoided.
    """
    # get local maxima in stft
    min_distance = 2
    size = 2 * min_distance + 1
    footprint = np.ones((size, ) * stft.ndim, dtype=bool)
    max_filter = ndi.maximum_filter(stft, footprint=footprint, mode='constant')
    local_max = max_filter == stft
    local_max &= stft > 0
    local_max_idx = np.nonzero(local_max) #peak coordinates
    local_max_val = stft[local_max_idx]
    local_max_idx = np.transpose(local_max_idx)
    local_max_t = t[local_max_idx[:, 1]]
    # get optimal threshold
    max_delta = duration / 4
    thresholds = np.arange(0.1, 1.0, 0.05)[::-1]

    for i, threshold in enumerate(thresholds):
        # get peak coordinates with threshold
        mask = local_max_val > threshold
        
        # get and sort peak time stamps
        time_stamps = np.sort(local_max_t[mask])

        # group time stamps if delta in between < 0.03
        delta = np.diff(time_stamps)
        idx = np.where(delta > 0.03)[0] + 1
        groups = np.split(time_stamps, idx)

        # compute mean of groups
        search_time = np.array([np.mean(group) for group in groups])

        # compute delta
        n_calls = len(search_time)
        delta = 0 if i == 0 else n_calls - len(stamps)
        if delta > max_delta:
            break
        stamps = search_time

    return stamps, threshold
    

def get_images(element, stamps, neg_offset, pos_offset):
    """
    Cuts out neg_offset + pos_offset samples around each time stamp.
    """
    peaks = (stamps *44100).astype(int)
    mask = ((peaks-neg_offset > 0) & (peaks+pos_offset < len(element)))
    peaks = peaks[mask]
    pot_calls = [element[p-neg_offset:p+pos_offset] for p in peaks]
    return pot_calls
