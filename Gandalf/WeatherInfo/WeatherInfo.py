#Imports
import requests
import json
import os
#Variables
wInf_globals = {'api_key': None}
#Functions
def _get_api_key():
    keyDir = './_config/owm_api_key.txt'
    if not os.path.exists(keyDir):
        raise Exception('key_file_404')
    key = open(keyDir, 'r').read()
    if key == 'api_key':
        raise Exception('default_key')
    if key == '':
        raise Exception('no_key')
    return key
def _request_weather(city, apiKey):
    urlStart = 'http://api.openweathermap.org/data/2.5/weather'
    urlArgs = 'q='+city+'&appid='+apiKey
    url = urlStart+'?'+urlArgs
    response = requests.get(url)
    contents = response.content
    response.close()
    return json.loads(contents)
def _return_weather(weather):
    return weather['weather'][0]['description']
def _return_temp(contents):
    main = contents['main']
    return main['temp'],main['feels_like']
#Main
def handle_weather(query, place, output, tempUnit='c', apiKey=None):
    global wInf_globals
    if apiKey == None:
        if wInf_globals['api_key'] == None:
            output('Getting API key from file')
            try:
                apiKey = _get_api_key()
            except Exception as e:
                e = str(e)
                print (e)
                if e == 'key_file_404':
                    output('No API key file found')
                    print ('No API key file found (_config/owm_api_key.txt)')
                    return
                elif e == 'default_key' or e == 'no_key':
                    output('Please set the OWM API key')
                    print ('Please set the OWM API key in (_config.owm_api_key.txt)')
                else:
                    output('An error occured while fetching API key from file')
                    print (e)
                    return
            wInf_globals['api_key'] = apiKey
        else:
            apiKey = wInf_globals['api_key']
    try:
        response = _request_weather(place, apiKey)
    except Exception as e:
        print (e)
        output('Cannot reach OWM')
        return
    if response['cod'] == 404:
        output('Cannot find city')
        return
    elif response['cod'] == 401:
        output('API key is invalid or unactivated')
        return
    if query == 'weather':
        output('Weather in '+place+': '+_return_weather(response))
    elif query == 'temperature':
        temp,feelsTemp = _return_temp(response)
        if tempUnit.lower() == 'k':
            add = 'degrees Kelvin'
        elif tempUnit.lower() == 'c':
            add = 'degrees Celsius'
            temp = temp-273.15
            feelsTemp = feelsTemp-273.15
        elif tempUnit.lower() == 'f':
            print ('bad')
            add = 'degrees Fahrenheit'
            temp = 1.8*(temp-273.15)+32
            feelsTemp = 1.8*(feelsTemp-273.15)+32
        temp = round(temp)
        feelsTemp = round(feelsTemp)
        output('It is '+str(temp)+' '+add+' in '+place)
        output('Feels like '+str(temp)+' '+add)
