#Imports
import spotipy #https://spotipy.readthedocs.io/en/2.18.0/
#Globals
spGlobals = {
    'logged_in': False,
    'spotify_client': None,
}
#Functions
def censor(text, keep=2, symbol='*'):
    newText = text[0:2]
    for i in range(len(text[2:])):
        newText += '*'
    return newText
def _getLogin():
    username = ''
    password = ''
    print (username)
    print (censor(password))
    return username,password
def _login():
    usr,pas = _getLogin()
    
