import pyaudio
import wave
from datetime import datetime
import socket

# adapted from script on AudioMoth USB Microphone site
#
#  TODO:  Init(), Close() etc..
#         ntp sync
#         heartbeat?
#         crash recover?
#         builtin scheduler or Cron job
#         exceptions around writing files/opening closing hw
#         how to stream on demand and record in same thread 
#         poss do recording in worker thread
#         push or pull data / REST API or http front end?


audio_format = pyaudio.paInt16
number_of_channels = 1
sample_rate = 48000
chunk_size = 4096
duration = 55


#filename = 'testxxx.wav'


## move to init method

#create pyadio instance and search for the audiomoth
device_index = None

audio = pyaudio.PyAudio()

for i in range(audio.get_device_count()):
    if 'AudioMoth' in audio.get_device_info_by_index(i).get('name'):
        device_index = i
        break

if device_index == None:
    print('No AudioMoth found')
    exit()

# generate filename
now = datetime.now()
filename = now.strftime("%Y-%m-%dT%H%M%S") + "-" + socket.gethostname() + ".wav"
print(filename)

    
    
# create pyaudio stream
stream = audio.open(format=audio_format, rate=sample_rate, channels=number_of_channels, input_device_index=device_index, input=True, frames_per_buffer=chunk_size)

# append audio chunks to array until enough samples have been acquired

print('Start Recording')

# probably better using numpy here?
data = []

total_samples = sample_rate * duration

while total_samples > 0:
    samples = min(total_samples, chunk_size)
    data.append(stream.read(samples))
    total_samples -= samples


# save the audio data as a wav file,
# -- could loop this yay many times, eg 60 for an hour?
# -- and maintain state
# -- or a script that could be run once a minute through cron?

wav = wave.open(filename, 'wb')
wav.setnchannels(number_of_channels)
wav.setsampwidth(audio.get_sample_size(audio_format))
wav.setframerate(sample_rate)
wav.writeframes(b''.join(data))
wav.close()



print('Finished recording')

stream.stop_stream()
stream.close()
audio.terminate()                  
