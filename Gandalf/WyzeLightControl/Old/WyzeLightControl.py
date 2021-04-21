def output(txt):
    print ('[OUTPUT] < '+txt+' >')

#Imports
from wyzeapy import client
#Functions
##Login
def login(email, password): #Returns client
    return client.Client(email, password)
def reauth(wyze_client):
    wyze_client.reauthenticate()
##Get Devices
def get_devices(wyze_client):
    devices = {}
    groups = {'No Group': {}}
    devicesRaw = wyze_client.get_devices()
    for i in devicesRaw:
        if type(i) == list:
            for j in i:
                groups[i.nickname][j.nickname] = j
        else:
            groups['No Group'][i.nickname] = i
    return groups
##Change Device States
def set_properties(wyze_client, device, enabled=None, color=None, brightness=None):
    if device.product_type == 'Light':
        if enabled != None:
            if enabled:
                wyze_client.turn_on(device)
            else:
                wyze_client.turn_off(device)
        if color != None:
            try:
                wyze_client.set_color(color)
            except:
                return 'Error: Cannot set color'
        if brightness != None:
            try:
                wyze_client.set_brightness(brightness)
            except:
                return 'Error: Cannot set brightness'
    else:
        return 'Error: Device is not of type light'


#Testing
def test():
    global wC
    wC = login('##', '##')
    devices = get_devices(wC)
    global target
    target = devices['TV Right']
    print ('Set variable "target" to target')
