#Imports
from wyzeapy import client
import time
#Properties
wLCProp = {'logged_in': False, 'client': None}
#Other Functions
def censor(text, keep=2, symbol='*'):
    newText = text[0:2]
    for i in range(len(text[2:])):
        newText += '*'
    return newText
#Main Functions
##Login
def _get_credentials():
    try:
        credFile = open('_config/wyze_credentials.txt', 'r')
        ePass = credFile.read()
        credFile.close()
    except Exception as e:
        print (e)
        raise Exception('noLogin')
    try:
        email = ePass.split('\n')[0]
        password = ePass.split('\n')[1]
    except Exception as e:
        print (e)
        raise Exception('wrongFormat')
    if email == 'email':
        raise Exception('defaultLogin')
    elif password == 'password':
        raise Exception('defaultLogin')
    print (email)
    print (censor(password))
    return email,password
def _login():
    email,password = _get_credentials()
    return client.Client(email, password)
def _reauthenticate(wC):
    try:
        wC.reauthenticate()
        return True
    except Exception as e:
        print (e)
        return False
##Get Devices
def _get_devices(wC):
    devices = {}
    groups = {}
    groupsTemp = {}
    devicesRaw = wC.get_devices()
    groupsRaw = wC.client.get_object_list()['data']['device_group_list']
    for i in devicesRaw:
        devices[i.nickname.lower()] = i
    for i in groupsRaw:
        nam = i['group_name'].lower()
        group_devs = i['device_list']
        groupsTemp[nam] = []
        groups[nam] = []
        for j in group_devs:
            groupsTemp[nam].append(j['device_mac'])
    for i in groupsTemp:
        for j in devices:
            if devices[j].mac in groupsTemp[i]:
                groups[i].append(devices[j])
    return devices,groups
##Toggle Light or Group
def _enable_light(wC, device, enabled):
    if enabled:
        wC.turn_on(device)
    else:
        wC.turn_off(device)
def _enable_light_group(wC, group, enabled):
    if enabled:
        for i in group:
            wC.turn_on(i)
            time.sleep(0.2)
    else:
        for i in group:
            wC.turn_off(i)
            time.sleep(0.2)
def _disco_mode(wC, group):
    for tick in range(round(round(300/len(group))/2)):
        _enable_light_group(wC, group, True)
        _enable_light_group(wC, group, False)
##Change Brightness of Light or Group
def _change_brightness(wC, device, brightness):
    wC.set_brightness(device, brightness)
def _change_brightness_group(wC, group, brightness):
    for i in group:
        wC.set_brightness(i, brightness)
        time.sleep(0.2)
#Handle Query
def handle_query(query, output):
    global wLCProp
    if wLCProp['logged_in'] == False:
        try:
            wC = _login()
            wLCProp['logged_in'] = True
        except Exception as e:
            err = str(e)
            print (err)
            correctFormat = 'email\npassword'
            if err == 'noLogin':
                output('No credentials file found')
                print ('No credentials file (_config/wyze_credentials.txt) found\nCorrect formatting:\n'+correctFormat)
            elif err == 'wrongFormat':
                output('Credentials file incorrectly formatted')
                print ('Credentials file (_config/wyze_credentials.txt) incorrectly formatted. Proper formatting:\n'+correctFormat)
            elif err == 'defaultLogin':
                output('No credentials stored in file')
                print ('Default "template" login stored in file (_config/wyze_credentials.txt). Please change to login information')
            return
        wLCProp['client'] = wC
    else:
        wC = wLCProp['client']
    if query[0] == 'reauthenticate':
        output('Reauthenticating...')
        success = _reauthenticate(wC)
        if success:
            output('Success')
        else:
            output('An error occured')
    elif query[0] == 'turn':
        if len(query) < 2:
            output('Not enough arguments')
            return
        if query[1] == 'off':
            enable = False
        elif query[1] == 'on':
            enable = True
        else:
            output('Unknown command')
            return
        devices,groups = _get_devices(wC)
        if query[2] == 'group':
            if len(query) < 3:
                output('Not enough arguments')
                return
            try:
                groupName = ' '.join(query[3:]).lower()
                _enable_light_group(wC, groups[groupName], enable)
            except KeyError:
                output('Group does not exist')
        else:
            try:
                name = ' '.join(query[2:]).lower()
                _enable_light(wC, devices[name], enable)
            except KeyError:
                output('Device does not exist')
    elif query[0] in ['dim', 'brighten']:
        if query[0] == 'dim':
            brightness = 1
        elif query[0] == 'brighten':
            brightness = 100
        else:
            output('Unknown command')
            return
        devices,groups = _get_devices(wC)
        if len(query) < 1:
            output('Not enough arguments')
            return
        if query[1] == 'group':
            if len(query) < 2:
                output('Not enough arguments')
                return
            try:
                groupName = ' '.join(query[2:]).lower()
                print (groupName)
                _change_brightness_group(wC, groups[groupName], brightness)
            except KeyError:
                output('Group does not exist')
        else:
            try:
                name = ' '.join(query[1:]).lower()
                print (name)
                _change_brightness(wC, devices[name], brightness)
            except KeyError:
                output('Device does not exist')
    elif query[0] == 'disco':
        if len(query) < 2:
            output('Not enough arguments')
            return
        devices,groups = _get_devices(wC)
        try:
            groupName = ' '.join(query[2:]).lower()
            print (groupName)
            output('Running disco mode for one minute')
            _disco_mode(wC, groups[groupName])
        except KeyError:
            output('Group does not exist')
