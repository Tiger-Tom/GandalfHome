#Imports
import pydub
import simpleaudio
import time
#Main
def playsound(soundDir):
    print ('Playing sound '+soundDir)
    sound = pydub.AudioSegment.from_wav(soundDir)
    wavObject = simpleaudio.WaveObject(sound.raw_data, sound.channels, sound.sample_width, sound.frame_rate)
    playback = wavObject.play()
    time.sleep(round(len(sound)/1000))
