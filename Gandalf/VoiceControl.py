####################
version = '1.4'
print ('---- |'+version+'| ----')
####################
#Imports
import speech_recognition as sr
import time
import os
import random
import pyjokes
import pyttsx3
import sounddevice
import simpleaudio
import pydub
import pyaudio
import math
#Setup Imported
spR = sr.Recognizer()
try:    
    ttsEngine = pyttsx3.init('espeak') #Always try to use ESpeak for cross-platform consistance
except:
    ttsEngine = pyttsx3.init() #In case ESpeak is not availiable
#Setup PrintBuffer
printBuffer = []
oldPrint = print
def newPrint(out):
    global printBuffer
    oldPrint(out)
    printBuffer.append(out)
    while True:
        if len(printBuffer) > 100:
            del printBuffer[0]
        else:
            break
print = newPrint
#Retrieve Properties
try:
    propF = open('_config/properties.txt', 'r')
    propsRaw = propF.read().split('\n')
    propF.close()
    properties = {}
    if propsRaw[-1] == '\n':
        del propsRaw[-1]
        print ('Removed trailing newline of properties')
    #print (propsRaw)
    for i in propsRaw:
        #print (i)
        if i[0] == '#':
            #print ('Ignoring comment')
            pass
        else:
            try:
                key,value = [i.split(':')[0], i.split(':')[1]]
                if ' #' in value:
                    properties[key] = value.split(' #')[0]
                else:
                    properties[key] = value
                print (key+' = '+value)
            except Exception as e:
                print (e)
except Exception as e:
    print ('Error: Unable to load properties file')
    print (e)
    exit()
##VTT Input
triggerWord = properties['triggerWord']
overrideInput = bool(int(properties['overrideInput']))
adjustForAmbientNoise = properties['adjustForAmbientNoise']
if properties['micSpeechRecognizeThreshold'] != '':
    spR.energy_threshold = int(properties['micSpeechRecognizeThreshold'])
triggerWordPhraseTimeout = int(properties['triggerWordPhraseTimeout'])
##TTS Output
voices = ttsEngine.getProperty('voices')
if properties['voiceIndex'] != '':
    ttsEngine.setProperty('voice', voices[int(properties['voiceIndex'])].id)
ttsEngine.setProperty('rate', int(properties['voiceRate']))
muteBootupStart = int(properties['muteBootupBetween'].split('-')[0])
muteBootupEnd = int(properties['muteBootupBetween'].split('-')[1])
micName = properties['micName']
##Other Config
tempUnits = properties['temperatureUnits'].lower()
serverModePass = properties['serverModePass']
##Audio Config
try:
    audCF = open('_config/audio_config.txt', 'r')
    audCRaw = audCF.read().split('\n')
    audCF.close()
    audio_dirs = {}
    if audCRaw[-1] == '\n':
        del audCRaw[-1]
        print ('Removed trailing newline of audio configurarion')
    for i in audCRaw:
        try:
            key,value = i.split(':')
            audio_dirs[key] = value
            print (key+' = '+value)
        except Exception as e:
            print (e)
except Exception as e:
    print ('Error: Unable to load audio configuration file')
    print (e)
    exit()
#In/Out Handler
def mainInput(phrase_time_limit=None):
    global spR
    global overrideInput
    global micIndex
    if overrideInput:
        return input('>')
    else:
        try:
            mic = sr.Microphone(micIndex)
            with mic as source:
                print ('Getting input')
                if adjustForAmbientNoise == '1':
                    spR.adjust_for_ambient_noise(mic)
                if phrase_time_limit == None:
                    audio = spR.listen(source)
                else:
                    audio = spR.listen(source, phrase_time_limit=phrase_time_limit)
            return audio
        except KeyboardInterrupt:
            print ('Killed')
            raise KeyboardInterrupt
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
    print ('Importing modules')
    #Command Libs
    print ('Importing command libraries')
    print ('Importing WyzeLightControl')
    import command_lib.WyzeLightControl as module_WLC
    print ('Importing ServerMode')
    import command_lib.ServerMode as server
    print ('Importing WeatherInfo')
    import command_lib.WeatherInfo as module_OWM_W
    print ('Importing Internet_Information')
    import command_lib.Internet_Information as module_II
    print ('Importing Math_Numbers')
    import command_lib.Math_Numbers as module_NumMath
    print ('Importing Other')
    import command_lib.OtherCommands as module_Other
    #Other Libs
    print ('Importing other libraries')
    print ('Importing playsound library')
    import lib.playsound
    def playSound(soundIndx):
        global audio_dirs
        print ('Audio '+soundIndx+' requested')
        try:
            audDir = audio_dirs[soundIndx]
            print ('Audio '+soundIndx+': '+audDir)
        except Exception as e:
            print ('Sound '+soundIndx+' does not exist')
            print (e)
            output(soundIndx)
            return False
        if audio_dirs[soundIndx].startswith('[%SPEECH_SYNTHESIZER%]'):
            toPlay = ' '.join(audio_dirs[soundIndx].split(' ')[1:])
            output(toPlay)
            return
        try:
            lib.playsound.playsound(audio_dirs[soundIndx])
        except Exception as e:
            print ('Unable to play sound '+soundIndx)
            print (e)
            output(soundIndx)
            return False
except Exception as e:
    print (e)
    output('Fatal: Unable to connect to required modules')
    quit()
#Handler
def speech_handler():
    global sPr
    global overrideInput
    global version
    global tempUnits
    global serverModePass
    global printBuffer
    #playSound('./Audio/ready.wav')
    playSound('ready_for_input')
    #playSound('./Audio/let-the-ring-bearer-decide.wav')
    audio = mainInput()
    if overrideInput:
        queryRaw = audio.split(' ')
    else:
        try:
            queryRaw = spR.recognize_google(audio).split(' ')
        except:
            #playSound('./Audio/gandalf_shallnotpass.wav')
            playSound('unrecognized_input')
            return
    query = queryRaw[0].lower()
    args = queryRaw[1:]
    print ('Query: '+query)
    print ('Arguments:\n'+','.join(args))
    ## Exit Command ##
    if query in ['exit', 'quit', 'bye']:
        #playSound('./Audio/fly-you-fools.wav')
        playSound('exit')
        return True
    ## Wyze Light Control
    elif query == 'turn':
        if args[0].lower() == 'on':
            audFile = 'wyze_light_on'
            #audFile = './Audio/let-me-risk-a-little-more-light.wav'
        elif args[0].lower() == 'off':
            audFile = 'wyze_light_off'
            #audFile = './Audio/go-back-to-the-shadow.wav'
        else:
            audFile = 'wyze_light_incorrect_option'
            #audFile = './Audio/dont-follow-the-lights.wav'
        playSound(audFile)
        args.insert(0, 'turn')
        module_WLC.handle_query(args, output)
    elif query == 'dim':
        #playSound('./Audio/dont-follow-the-lights.wav')
        playSound('wyze_light_dim')
        args.insert(0, 'dim')
        module_WLC.handle_query(args, output)
    elif query == 'brighten':
        #playSound('./Audio/let-me-risk-a-little-more-light.wav')
        playSound('wyze_light_brighten')
        args.insert(0, 'brighten')
        module_WLC.handle_query(args, output)
    elif query == 'reauthenticate':
        module_WLC.handle_query(['reauthenticate'], output)
    ## Test Command ##
    elif query == 'test':
        module_Other.test(output)
    ## Remote Administration Server Command ##
    elif query == 'server':
        server.run_server(output, serverModePass, printBuffer)
    ## Time & Date Query Commands ##
    elif queryRaw[0].lower() == 'time' or ' '.join(queryRaw).lower() == 'what time is it':
        module_Other.get_time(output)
    elif queryRaw[0].lower() == 'date' or ' '.join(queryRaw).lower() == 'what is the date' or ' '.join(queryRaw).lower() == 'what day is it':
        module_Other.get_date(output)
    ## Information & Internet ##
    elif queryRaw[0].lower() == 'is' and queryRaw[-1].lower() == 'online':
        URL = ''.join(queryRaw[1:-1]).lower().replace('dot', '.')
        module_II.isOnline(output, URL)
    elif (query == 'weather' or (' '.join(queryRaw[0:5]).lower() == 'what is the weather in')) or (query == 'temperature' or (' '.join(queryRaw[0:5]).lower() == 'what is the temperature in')):
        if query == 'weather' or query == 'temperature':
            place = ' '.join(queryRaw[1:])
        else:
            place = ' '.join(queryRaw[5:])
        if 'temperature' in queryRaw:
            output('Checking temperature in '+place)
            module_OWM_W.handle_weather('temperature', place, output, tempUnits)
        else:
            output('Checking weather in '+place)
            module_OWM_W.handle_weather('weather', place, output)
    elif (query == 'what' and queryRaw[1].lower() == 'is' and queryRaw[-2].lower() == 'in') or query == 'translate':
        if query == 'translate':
            text = ' '.join(queryRaw[1:-2]).lower()
        else:
            text = ' '.join(queryRaw[2:-2]).lower()
        langRaw = queryRaw[-1].lower()
        module_II.translate(output, text, langRaw)
    elif query == 'search':
        if len(args) > 2:
            if args[-2].lower() == 'on':
                del args[-2]
            if args[-1].lower() == 'wikipedia':
                del args[-1]
        sqry = ' '.join(args).lower()
        module_II.searchWiki(output, sqry)
    ## Numbers
    elif query == 'calculate':
        if ' '.join(queryRaw[:5]).lower() == 'calculate the square root of':
            if len(queryRaw) < 5:
                output('Not enough arguments')
            else:
                module_NumMath.calculateSqrt(output, ' '.join(queryRaw[5:]))
        else:
            if len(args) < 1:
                output('Not enough arguments')
            else:
                try:
                    module_NumMath.calculate(output, ' '.join(args))
                except Exception as e:
                    output('An error occured while calculating')
                    output(e)
    elif ' '.join(queryRaw[:6]).lower() == 'what is the square root of':
        if len(queryRaw) < 6:
            output('Not enough arguments')
        else:
            module_NumMath.calculateSqrt(output, ' '.join(queryRaw[6:]))
    elif ' '.join(queryRaw[0:6]).lower() == 'give me a random number between':
        if len(queryRaw) > 8:
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
        else:
            output('Not enough arguments')
    ## Fun ##
    elif ' '.join(queryRaw).lower() == 'tell me a joke':
        output(pyjokes.get_joke())
    elif ' '.join(queryRaw[0:2]).lower() == 'tell me' and queryRaw[-1].lower() == 'jokes':
        try:
            rang = int(queryRaw[2])
            for i in range(rang):
                output('Joke '+str(i+1)+' of '+str(rang)+': '+pyjokes.get_joke())
        except:
            output('Cannot convert '+queryRaw[2]+' to integer')
    elif query == 'disco':
        groupName = ' '.join(queryRaw[2:]).lower()
        module_WLC.handle_query(['disco', 'mode', groupName], output)
    ## Other ##
    elif query == 'version':
        output('Running version '+version)
    elif ' '.join(queryRaw[0:2]).lower() == 'never mind' or query == 'cancel' or query == 'nevermind':
        #playSound('./Audio/all-right-then-keep-your-secrets.wav')
        playSound('query_cancelled')
    else:
        playSound('unknown_query')
        #playSound('./Audio/do-not-take-me.wav')
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
def mainRun():
    global triggerWord
    global overrideInput
    playSound('boot_successful')
    while True:
        if overrideInput:
            speech_handler()
        else:
            audio = mainInput()
            try:
                text = spR.recognize_google(audio)
                print ('Text recognized')
            except KeyboardInterrupt:
                print ('Killed')
                raise KeyboardInterrupt
            except:
                print ('Failed to recognize')
                text = ''
            if triggerWord.lower() in text.lower():
                print ('Trigger word recognized')
                try:
                    if speech_handler():
                        break
                except KeyboardInterrupt:
                    print ('Killed')
                    raise KeyboardInterrupt
                except Exception as e:
                    print (e)
                    output('A fatal exception has occured')
            else:
                print ('Recieved text is not trigger word')
            if overrideInput:
                if speech_handler():
                    break
devMode = True ########
if __name__ == '__main__' and not devMode:
    mainRun()
elif devMode:
    print ('devMode')
    output = print
    overrideInput = True
    playSound = print
    mainRun()
