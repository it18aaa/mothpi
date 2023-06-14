import pyaudio
import wave
from datetime import datetime
import numpy as np
import soundfile as sf
import socket
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import gc

# adapted from script on AudioMoth USB Microphone site
#
#  TODO:  Init(), Close() etc..
#         ntp sync?
#         heartbeat?
#         crash recover?
#         flac ->  
#         builtin scheduler or Cron job
#         exceptions around writing files/opening closing hw
#         how to stream on demand and record in same thread 
#         poss do recording in worker thread
#         push or pull data / REST API or http front end?

audio_format = pyaudio.paInt16
number_of_channels = 1
sample_rate = 48000
chunk_size = 4096
duration = 60                        # should be set to 60
recording_hours = 3
iterations = recording_hours * duration
data_dir = "data/"

#create pyadio instance and search for the audiomoth

audio = pyaudio.PyAudio()

def get_audiomoth_index() :
    device_index = None
    for i in range(audio.get_device_count()):
        if 'AudioMoth' in audio.get_device_info_by_index(i).get('name'):
            device_index = i
            break
    return device_index

def get_filename():
    now = datetime.now()
    return socket.gethostname() + "-" + now.strftime("%Y-%m-%dT%H%M%S")


def write_flac(filename, data, sample_rate, dtype):
    #  convert data to np array
    npdata = np.frombuffer(b''.join(data), dtype=dtype)
    
    sf.write(filename, npdata, sample_rate)
    # kludge to close the sf.file handle
    # might as well use it to clear
    gc.collect() 


def write_wav(filename, data, num_channels, sample_rate, audio_format):
    # save the audio data as a wav file,
    # -- could loop this yay many times, eg 60 for an hour?
    # -- and maintain state
    # -- or a script that could be run once a minute through cron?
    wav = wave.open(fname_wav, 'wb')
    wav.setnchannels(number_of_channels)
    wav.setsampwidth(audio.get_sample_size(audio_format))
    wav.setframerate(sample_rate)
    wav.writeframes(b''.join(data))
    wav.close()

device_index = get_audiomoth_index()

if device_index == None:
    print('Cannot find AudioMoth')
    exit()

print(f"AudioMoth device found at index {device_index}")   

print("Opening pyaudio stream")

# create pyaudio stream, but dont start it
stream = audio.open(format=audio_format,
                    rate=sample_rate,
                    channels=number_of_channels,
                    input_device_index=device_index,
                    input=True,
                    frames_per_buffer=chunk_size,
                    start=False)

for i in range(1, iterations):

    fname = get_filename()
    fname_wav = fname  + ".wav"
    fname_flac = fname + ".flac"

    print(f"Recording {fname_flac}")

    # append audio chunks to array until
    # enough samples have been acquired

    data = []
    total_samples = sample_rate * duration

    stream.start_stream()
    
    while total_samples > 0:
        samples = min(total_samples, chunk_size)
        data.append(stream.read(samples))
        total_samples -= samples

    stream.stop_stream()

    write_wav(filename=fname_wav,
              data=data,
              num_channels=number_of_channels,
              sample_rate=sample_rate,
              audio_format=audio_format) 

    write_flac(filename=fname_flac,
               data=data,
               sample_rate=sample_rate,
               dtype=np.int16)
    
    # upload the file
    # maybe this can be farmed out to a callback

    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)

    folder = '1oQYJ_aOY3MCzdMNNrJnt43SLuASKF19S'

    file1 = drive.CreateFile()
    file1.SetContentFile(fname_flac)
    file1.Upload()

print('Finished recording')

stream.stop_stream()
stream.close()
audio.terminate()                  
