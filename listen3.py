import pyaudio
import wave
import os
from datetime import datetime
import numpy as np
import soundfile as sf
import socket
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import requests
import gc
import subprocess
import fcntl

audio_format = pyaudio.paInt16
number_of_channels = 1
sample_rate = 48000
chunk_size = 4096
duration = 60                        # should be set to 60
recording_hours = 1
iterations = 10  #recording_hours * duration
data_dir = "data"

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
    gc.collect() 

def add_to_pending(filename):
    # this should use locking !
    pending = open("pending.txt", "a")    
    pending.write(f"{filename}\n")
    pending.close()
 
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

    write_flac(filename=os.path.join(data_dir, fname_flac),
               data=data,
               sample_rate=sample_rate,
               dtype=np.int16)
    
    # upload the file

    add_to_pending(os.path.join(data_dir, fname_flac))

    # start the uploader as a separate process in the background
    subprocess.Popen(["python","gdrive-upload.py","&","disown"])
    
print('Finished recording')

stream.stop_stream()
stream.close()
audio.terminate()                  
