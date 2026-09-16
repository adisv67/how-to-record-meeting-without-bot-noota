import sounddevice as sd
import numpy as np

dev = None
for i, d in enumerate(sd.query_devices()):
    if 'BlackHole' in d['name'] and d['max_input_channels'] >= 1:
        dev = i

def callback(indata, frames, time_info, status):
    volume = np.linalg.norm(indata) * 10
    print(f'Volume: {volume:.2f} | ' + '#' * int(volume))

print('Listening for 5 seconds... Play your YouTube video NOW!')
with sd.InputStream(device=dev, samplerate=16000, channels=1, blocksize=512, dtype='float32', callback=callback):
    import time
    time.sleep(5)
print('Done.')
