from scipy import signal
from scipy.io import wavfile
from pydub import AudioSegment

#####################################################################
#  PURPOSE:   PRODUCES THE SPECTROGRAM OF THE SPECIFIED .WAV FILE   #
#       PARAMS:    WAV_FILE    STR     PATH TO THE .WAV FILE        #
# RETURNS:   NDARRAY OF FLOAT32 - SPECTROGRAM OF INPUTTED .WAV FILE #
#####################################################################

def wav_to_spectrogram(wav_file):
    sample_rate, samples = wavfile.read(wav_file)
    frequencies, times, spectrogram = signal.spectrogram(samples, sample_rate, nfft=1024)
    return spectrogram

def __match_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

#def normalize_wav_file(wav_file, target_dBFS=0):
#    sound = AudioSegment.from_wav(wav_file)
#    sound = __match_amplitude(sound, target_dBFS)
#    sound.export(wav_file, format="wav")
    
    
