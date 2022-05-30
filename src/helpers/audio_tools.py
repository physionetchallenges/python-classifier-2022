from scipy import signal
from scipy.io import wavfile
from pydub import AudioSegment
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

#####################################################################
#  PURPOSE:   PRODUCES THE SPECTROGRAM OF THE SPECIFIED .WAV FILE   #
#       PARAMS:    WAV_FILE    STR     PATH TO THE .WAV FILE        #
# RETURNS:   NDARRAY OF FLOAT32 - SPECTROGRAM OF INPUTTED .WAV FILE #
#####################################################################
#TODO: do we still need this function?
def wav_to_spectrogram(wav_file):
    y, sr = librosa.load(wav_file)
    # get window size
    win = signal.get_window(sr ,window='hann')
    S = librosa.feature.melspectrogram(y, sr=sr, n_fft=win)
    return S

#TODO: do we still need this function?
def __match_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

#def normalize_wav_file(wav_file, target_dBFS=0):
#    sound = AudioSegment.from_wav(wav_file)
#    sound = __match_amplitude(sound, target_dBFS)
#    sound.export(wav_file, format="wav")

#PURPOSE:   load the spectrogram of a .wav audio file(s)
#PARAMS:    sample_rate         int     sample rate of the wav file (must be the same for all wav files inputted)
#           *wav_file           str     path(s) to the wav file(s)
#           print_spectrogram   Bool    [OPTIONAL] print the spectrogram: True OR False, default=False
#           title               str     [OPTIONAL] (if print_spectro=True) title of the printed spectrogram: str, default=None
#           y_type              str     [OPTIONAL] (if print_spectro=True) scale to use for the y axis: 'log' OR 'linear', default='log'
#RETURN:    ndarray     spectrogram of the wav file
def wav_to_spectro(sample_rate, *wav_file, print_spectrogram=False, title=None, y_type='log'):
    spectrograms = []
    for f in wav_file:
        waveform, sr = librosa.load(f, sr=sample_rate)
        x = librosa.stft(waveform)  #STFT of waveform
        x_db = librosa.amplitude_to_db(np.abs(x))   #map the magnitudes of x to a decibel scale

        if print_spectrogram:
            print_spectro(x_db, sample_rate, title = title, y_type=y_type)

        spectrograms.append(x_db)

    return tuple(spectrograms)

#PURPOSE:   print a spectrogram
#PARAMS:    spectrogram     ndarray     spectrogram to print
#           sample_rate     int         sample rate of the wav file
#           title           str         [OPTIONAL] title of the printed spectrogram: str, default=None
#           y_type          str         [OPTIONAL] scale to use for the y axis: 'log' OR 'linear', default='log'
def print_spectro(spectrogram, sample_rate, title=None, y_type='log'):
    fig, ax = plt.subplots()
    img = librosa.display.specshow(spectrogram, sr=sample_rate, x_axis='time', y_axis=y_type, ax=ax)
    if not title==None:
        ax.set(title=title)
    fig.colorbar(img, ax=ax, format="%+2.f dB")