#Imports
import speech_recognition as sr
import time
import os
import simpleeval
import google_trans_new
import wikipedia
import random
import pyjokes
import pyttsx3
import sounddevice
import simpleaudio
import pydub
import pyaudio
#Setup Imported
spR = sr.Recognizer()
try:    
    ttsEngine = pyttsx3.init('espeak') #Always try to use ESpeak for cross-platform consistance
except:
    ttsEngine = pyttsx3.init() #In case ESpeak is not availiable
#Variables & Config
try:
    propF = open('_config/properties.txt', 'r')
    propsRaw = propF.read().split('\n')
    propF.close()
    properties = {}
    for i in propsRaw:
        try:
            key,value = i.split(':')
            properties[key] = value.split(' #')[0]
            print (key+' = '+value)
        except Exception as e:
            print (e)
except Exception as e:
    print ('Error: Unable to load properties file')
    print (e)
    exit()
triggerWord = properties['triggerWord']
voices = ttsEngine.getProperty('voices')
ttsEngine.setProperty('voice', voices[int(properties['voiceIndex'])].id)
ttsEngine.setProperty('rate', int(properties['voiceRate']))
overrideInput = bool(int(properties['overrideInput']))
muteBootupStart = int(properties['muteBootupBetween'].split('-')[0])
muteBootupEnd = int(properties['muteBootupBetween'].split('-')[1])
#ignoredMicNames = properties['ignoredMicNames'].split(',')
#confirmedMicNameParts = properties['confirmedMicNameParts'].split(',')
#micIDSettings = [properties['micName'], properties['micIndex'], properties['micIDMode']]
micName = properties['micName']
if properties['micSpeechRecognizeThreshold'] != '':
    spR.energy_threshold = int(properties['micSpeechRecognizeThreshold'])
#In/Out Handler
def mainInput():
    global spR
    global overrideInput
    global micIndex
    if overrideInput:
        return input('>')
    else:
        try:
            with sr.Microphone(micIndex) as source:
                print ('Getting input')
                audio = spR.listen(source)
            return audio
        except:
            print ('Error: cannot record audio. Try "sudo apt-get install python3-pyaudio" or "pip3 install pyaudio"')
def output(txt):
    global ttsEngine
    print ('[Output] < '+str(txt)+' >')
    ttsEngine.say(str(txt))
    ttsEngine.runAndWait()
def bootOutput(txt):
    global muteBootupStart
    global muteBootupStop
    hr = time.localtime().tm_hour
    mn = time.localtime().tm_min
    if hr > muteBootupStart or hr < muteBootupEnd:
        print ('Suppressed bootup text:\n'+txt)
    else:
        output(txt)
#Import Modules
try:
    import WyzeLightControl.WyzeLightControl as module_WLC
    import ServerMode.ServerMode as server
    #import RokuControl.RokuControl as rokuCtrl
except:
    print (e)
    output('Fatal: Unable to connect to required modules')
    quit()
#Playsound
def playSound(soundDir):
    sound = pydub.AudioSegment.from_wav(soundDir)
    wavObject = simpleaudio.WaveObject(sound.raw_data, sound.channels, sound.sample_width, sound.frame_rate)
    #playback  = simpleaudio.play_buffer(sound.raw_data, num_channels=sound.channels, bytes_per_sample=sound.sample_width, sample_rate=sound.frame_rate)
    #playback.
    playback = wavObject.play()
    time.sleep(round(len(sound)/1000))
    #return playback
    #playback.run_wait()
    #signal,sr = librosa.load(soundDir, sr=None)
    #data,fs = soundfile.read(soundDir, dtype='float32')
    #sounddevice.play(data, fs)
    #print (sounddevice.wait())
    #playsound.playsound(soundDir)
    #app = wx.App()
    #aud = wx.adv.Sound(soundDir)
    #try:
    #    aud.Play(wx.adv.SOUND_SYNC)
    #except KeyboardInterrupt:
    #    aud.Stop()
    #del app
    #time.sleep(1)
#Handler
def speech_handler():
    global sPr
    global overrideInput
    #playSound('./Audio/ready.wav')
    playSound('./Audio/let-the-ring-bearer-decide.wav')
    audio = mainInput()
    if overrideInput:
        queryRaw = audio.split(' ')
    else:
        try:
            queryRaw = spR.recognize_google(audio).split(' ')
        except:
            playSound('./Audio/gandalf_shallnotpass.wav')
            return
    query = queryRaw[0].lower()
    args = queryRaw[1:]
    print ('Query: '+query)
    print ('Arguments:\n'+','.join(args))
    if query in ['exit', 'quit']:
        playSound('./Audio/fly-you-fools.wav')
        return True
    elif query == 'turn':
        if args[0].lower() == 'on':
            audFile = './Audio/let-me-risk-a-little-more-light.wav'
        elif args[0].lower() == 'off':
            audFile = './Audio/go-back-to-the-shadow.wav'
        else:
            audFile = './Audio/dont-follow-the-lights.wav'
        playSound(audFile)
        args.insert(0, 'turn')
        module_WLC.handle_query(args, output)
    elif query == 'dim':
        playSound('./Audio/dont-follow-the-lights.wav')
        args.insert(0, 'dim')
        module_WLC.handle_query(args, output)
    elif query == 'brighten':
        playSound('./Audio/let-me-risk-a-little-more-light.wav')
        args.insert(0, 'brighten')
        module_WLC.handle_query(args, output)
    elif query == 'reauthenticate':
        module_WLC.handle_query(['reauthenticate'], output)
    elif query == 'test':
        output('Test')
    elif query == 'server':
        server.run_server(output)
    #elif query in ['pause', 'play']:
    #    rokuCtrl.parse('pause/play')
    #elif ' '.join(queryRaw).lower() == 'find remote':
    #    rokuCtrl.parse('find remote')
    #elif query == 'type':
    #    rokuCtrl.parse('type', args)
    #elif query == 'search':
    #    rokuCtrl.parse('search', args)
    elif queryRaw[0].lower() == 'time' or ' '.join(queryRaw).lower() == 'what time is it':
        lt = time.localtime()
        if lt.tm_min == 0:
            timeFormat = 'It is currently '+str(lt.tm_hour)+' o clock'
        else:
            timeFormat = 'It is currently '+str(lt.tm_hour)+':'+str(lt.tm_min)
        output(timeFormat)
    elif queryRaw[0].lower() == 'date' or ' '.join(queryRaw).lower() == 'what is the date' or ' '.join(queryRaw).lower() == 'what day is it':
        lt = time.localtime()
        if lt.tm_min == 0:
            timeFormat = str(lt.tm_hour)+' o clock'
        else:
            timeFormat = str(lt.tm_hour)+':'+str(lt.tm_min)
        months = ['January', 'Febuary', 'March', 'April', 'May', 'June', 'July', 'Augest', 'September', 'October', 'November', 'December']
        month = months[lt.tm_mon]
        weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        weekday = weekdays[lt.tm_wday]
        if lt.tm_mday > 3:
            day = str(lt.tm_mday)+'th'
        elif lt.tm_mday == 3:
            day = '3rd'
        elif lt.tm_mday == 2:
            day = '2nd'
        elif lt.tm_mday == 1:
            day = '1st'
        else:
            day = 'unknown'
        dateFormat = 'It is currently '+timeFormat+', on '+weekday+', '+month+' '+day+', '+str(lt.tm_year)
        output(dateFormat)
    elif queryRaw[0].lower() == 'is' and queryRaw[-1].lower() == 'online':
        URL = ''.join(queryRaw[1:-1]).lower().replace('dot', '.')
        online = os.system('ping '+URL)
        if online == 0:
            output(URL+' is online')
        else:
            output(URL+' is not online')
    elif query == 'calculate':
        calc = ' '.join(args)
        calc = calc.replace('plus', '+').replace('minus', '-').replace('times', '*')
        calc = calc.replace('divided by', '/').replace('to the power of', '**')
        calc = calc.replace('point', '.').replace('dot', '.')
        calc = calc.replace(' ', '')
        output('Calculating '+calc)
        answer = simpleeval.simple_eval(calc)
        output(answer)
    elif (query == 'what' and queryRaw[1].lower() == 'is') or query == 'translate':
        translator = google_trans_new.google_translator()
        if query == 'translate':
            text = ' '.join(queryRaw[1:-2]).lower()
        else:
            text = ' '.join(queryRaw[2:-2]).lower()
        langRaw = queryRaw[-1].lower()
        print ('Translating "'+text+'" to '+langRaw)
        try:
            lang = list(google_trans_new.LANGUAGES.keys())[list(google_trans_new.LANGUAGES.values()).index(langRaw)]
            print ('Language ID: '+lang)
            result = translator.translate(text, lang_tgt=lang)
            output(result)
        except:
            output('Incorrect language')
    elif query == 'search':
        if len(args) > 2:
            if args[-2].lower() == 'on':
                del args[-2]
            if args[-1].lower() == 'wikipedia':
                del args[-1]
        sqry = ' '.join(args).lower()
        try:
            out = wikipedia.summary(sqry)
        except:
            srch = wikipedia.search(sqry)
            try:
                output('Reading first result')
                out = wikipedia.summary(srch[0])
                sqry = srch[0]
            except:
                try:
                    output('Failed. Reading second result')
                    out = wikipedia.summary(srch[1])
                    sqry = srch[1]
                except:
                    out = 'The first two search results all either didn\'t exist, or were disambiguation pages'
                    sqry = None
        if sqry != None:
            output('Summary of page '+sqry+' on Wikipedia')
        output(out)
    elif ' '.join(queryRaw[0:6]).lower() == 'give me a random number between':
        try:
            x = int(queryRaw[6])
        except:
            output('Cannot convert '+queryRaw[6]+' to integer')
            x = None
        try:
            y = int(queryRaw[8])
        except:
            output('Cannot convert '+queryRaw[8]+' to integer')
            y = None
        if (x != None) and (y != None):
            output(str(random.randint(x, y)))
    elif ' '.join(queryRaw).lower() == 'tell me a joke':
        output(pyjokes.get_joke())
    elif ' '.join(queryRaw[0:2]).lower() == 'tell me' and queryRaw[-1].lower() == 'jokes':
        try:
            rang = int(queryRaw[2])
            for i in range(rang):
                output('Joke '+str(i+1)+' of '+str(rang)+': '+pyjokes.get_joke())
        except:
            output('Cannot convert '+queryRaw[2]+' to integer')
    elif ' '.join(queryRaw[0:2]).lower() == 'never mind' or query == 'cancel':
        playSound('./Audio/all-right-then-keep-your-secrets.wav')
    else:
        playSound('./Audio/do-not-take-me.wav')
#Find Microphone
'''micNames = enumerate(sr.Microphone.list_microphone_names())
micIndex = None
for index,name in micNames:
    for i in confirmedMicNameParts:
        if i.lower() in name.lower():
            micIndex = index
            break
if micIndex == None:
    for index,name in micNames:
        allowed = True
        for i in ignoredMicNames:
            if name.lower() in i.lower():
                allowed = False
        if allowed:
            micIndex = index
            output('Selected microphone '+name+' at index '+str(index))
            break
    if index == None:
        output('Error: No microphone find. Check connections and properties.txt')
        exit()'''
'''if micIDSettings[2] == '2':
    micIndex = None
elif micIDSettings[2] == '1':
    micIndex = int(micIDSettings[1])
elif micIDSettings[2] == '0':
    micNames = enumerate(sr.Microphone.list_microphone_names())
    micIndex = -1
    for index,name in micNames:
        if name.lower() == micIDSettings[1].lower():
            micIndex = index
            break
    if micIndex == -1:
        output('No microphone matching name. Using first result')
        micIndex = 0'''
if micName == 'default-win':
    if os.name == 'nt':
        micName = 'default'
    else:
        micName = ''
foundMicName = None
if micName == '':
    p = pyaudio.PyAudio()
    rang = p.get_device_count()
    for i in range(rang):
        if p.get_device_info_by_index(i)['maxInputChannels'] > 0:
            foundMicName = p.get_device_info_by_index(i)['name']
            bootOutput('Using microphone '+p.get_device_info_by_index(i)['name'])
            break
    if foundMicName == None:
        bootOutput('No microphone found')
        exit()
elif micName == 'default':
    micIndex = None
else:
    p = pyaudio.PyAudio()
    rang = p.get_device_count()
    micIndex = -1
    for i in range(rang):
        if micName.lower() in p.get_device_info_by_index(i)['name'].lower():
            foundMicName = p.get_device_info_by_index(i)['name']
if foundMicName != None:
    for index,name in enumerate(sr.Microphone.list_microphone_names()):
        if (name.lower() in foundMicName.lower()) or (foundMicName.lower() in name.lower()):
            micIndex = index
            break
#Main
bootOutput('Boot successful. Awaiting input')
while True:
    audio = mainInput()
    try:
        text = spR.recognize_google(audio)
        print ('Text recognized')
    except:
        print ('Failed to recognize')
        text = ''
    if triggerWord.lower() in text.lower():
        print ('Trigger word recognized')
        if speech_handler():
            break
    else:
        print ('Recieved text is not trigger word')
    if overrideInput:
        if speech_handler():
            break
