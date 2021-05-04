#Imports
import google_trans_new
import wikipedia
import os
#Functions
##Ping
def isOnline(output, URL):
    output('Checking if '+URL+' is online')
    amount = '2'
    if os.name == 'nt':
        option = '-n '+amount
    else:
        option = '-c '+amount
    command = 'ping '+option+' '+URL
    print (command)
    online = os.system(command)
    if online == 0:
        output(URL+' is online')
    else:
        output(URL+' is not online')
##Translate
def translate(output, text, langRaw):
    translator = google_trans_new.google_translator()
    print ('Translating "'+text+'" to '+langRaw)
    try:
        lang = list(google_trans_new.LANGUAGES.keys())[list(google_trans_new.LANGUAGES.values()).index(langRaw)]
        print ('Language ID: '+lang)
        result = translator.translate(text, lang_tgt=lang)
        output(result)
    except:
        output('Unknown language')
##Wikipedia
def searchWiki(output, sqry):
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
