#Imports
import os
import shutil
import hashlib
#Functions
def fixDir(dir_path):
    dir_path = dir_path.replace('\\', '/')
    if not os.path.exists(dir_path):
        print ('Error! Path does not exist')
        print (dir_path)
        raise FileNotFoundError(dir_path)
    if not dir_path.endswith('/'):
        return dir_path+'/'
    return dir_path
def installRequirements(dest):
    print ('Installing required modules...')
    os.chdir(dest+'Gandalf')
    os.system('pip3 install -r requirements.txt')
    print ('Done')
def checksumDir(path, ignoreDirs=[]):
    curH = ''
    for i in os.listdir(path):
        if os.path.isdir(path+'/'+i):
            if i in ignoreDirs:
                print ('Skipping dir '+i)
            else:
                print ('Recursively hashing dir '+i)
                curH += checksumDir(path+'/'+i, ignoreDirs)
        else:
            if i in ignoreDirs:
                print ('Skipping file '+i)
            else:
                print ('Hashing file '+i)
                try:
                    curF = open(path+'/'+i, 'r', encoding='UTF-8')
                    while True:
                        buffer = curF.read(4096).encode('UTF-8')
                        if not buffer:
                            break
                        try:
                            curH += hashlib.md5(buffer).hexdigest()
                        except Exception as e:
                            print ('An error occured')
                            print (e)
                except:
                    pass
                curF.close()
    return hashlib.md5(curH.encode('UTF-8')).hexdigest()
#Main
##Find Source & Destination
source = fixDir(input('Enter Source Directory (Without /Gandalf) >'))
dest = fixDir(input('Enter Destination Directory (Without /Gandalf) >'))
##Check If Already Exists
if not os.path.exists(dest+'Gandalf'):
    print ('No installation found. Installing...')
    shutil.copytree(source+'Gandalf', dest+'Gandalf')
    print ('Done')
    installRequirements(dest)
    print ('Comparing checksums of files...')
    print ('Generating source checksum...')
    #sCheck = hashlib.md5(open(source+'Gandalf/VoiceControl.py', 'rb').read()).hexdigest()
    sCheck = checksumDir(source+'Gandalf', ['_config'])
    print ('Generating destination checksum...')
    #dCheck = hashlib.md5(open(dest+'Gandalf/VoiceControl.py', 'rb').read()).hexdigest()
    dCheck = checksumDir(dest+'Gandalf', ['_config'])
    print ('Checksums (source is first, destination is second):')
    print (sCheck)
    print (dCheck)
    if sCheck == dCheck:
        print ('Checksum validated!')
    else:
        print ('Checksums do not mach. An error may have occured. If you encounter any errors, please run the installation program again.')
    exit()
##Get Configuration
configFound = []
print ('Finding configuration in destination...')
for file in os.listdir(dest+'Gandalf/_config'):
    print ('Found '+file)
    configFound.append(file)
print ('Found configuration files')
print (configFound)
print ('Checking source configuration...')
filesRestored = 0
for file in os.listdir(source+'Gandalf/_config'):
    if not file in configFound:
        print ('Missing configuration found')
        print (file)
        shutil.copy(source+'Gandalf/_config/'+file, dest+'Gandalf/_config/')
        print ('Repaired missing configuration '+file)
        filesRestored += 1
print ('Repaired '+str(filesRestored)+' missing configuration files')
###Fix properties.txt
print ('Reading destination properties.txt ...')
dPropDir = dest+'Gandalf/_config/properties.txt'
sPropDir = source+'Gandalf/_config/properties.txt'
dProp = open(dPropDir, 'r').read()
sProp = open(sPropDir, 'r').read()
properties = {}
for i in dProp.split('\n'):
    try:
        nam,value = i.split(':')
        print ('Read property '+nam+' from destination')
        properties[nam] = value
    except:
        print ('Cannot parse line '+i+'\nIgnoring...')
print ('Read properties:\n'+str(properties))
print ('Reading source properties.txt')
for i in sProp.split('\n'):
    try:
        nam,value = i.split(':')
    except:
        print ('Cannot parse line '+i+'\nIgnoring')
    print ('Read property '+nam+' from source')
    try:
        properties[nam]
        print ('Property '+nam+' already exists')
    except:
        print ('Property '+nam+' does not exist. Repairing...')
        properties[nam] = value
print ('Destroying original properties.txt (DO NOT CLOSE PROGRAM NOW, OR YOU WILL LOSE ALL SAVED CONFIGURATION IN properties.txt!)...')
os.remove(dPropDir)
print ('Parsing new properties.txt contents...')
cont = ''
for i in properties:
    print ('Parsing '+i+'...')
    cont = cont+i+':'+properties[i]+'\n'
print ('Writing new properties to properties.txt:')
print (cont)
open(dPropDir, 'w').write(cont)
print ('Done repairing properties.txt')
print ('Done copying configuration')
##Remove Old
print ('Updating files...')
print ('Removing old version...')
dirs = os.listdir(dest+'Gandalf')
for i in dirs:
    if i == '_config':
        print ('Skipping _config as it is configuration...')
    else:
        if os.path.isdir(dest+'Gandalf/'+i):
            print ('Removing directory '+i)
            shutil.rmtree(dest+'Gandalf/'+i)
            print ('Done')
        else:
            print ('Removing file '+i)
            os.remove(dest+'Gandalf/'+i)
            print ('Done')
print ('Done removing old version')
##Copy New
print ('Copying new version...')
dirs = os.listdir(source+'Gandalf')
for i in dirs:
    cur = source+'Gandalf/'+i
    if os.path.isdir(cur):
        print (i+' is directory. Copying...')
        shutil.copytree(cur, dest+'Gandalf/'+i, dirs_exist_ok=True)
        print ('Done copying '+i)
    else:
        print (i+' is file. Copying...')
        shutil.copy(cur, dest+'Gandalf/')
        print ('Done copying '+i)
print ('Done copying new version')
##Install Modules
installRequirements(dest)
##Finish Installation
print ('Installation complete!')
##Find Checksums
print ('Comparing checksums of files...')
print ('Generating source checksum...')
#sCheck = hashlib.md5(open(source+'Gandalf/VoiceControl.py', 'rb').read()).hexdigest()
sCheck = checksumDir(source+'Gandalf', ['_config'])
print ('Generating destination checksum...')
#dCheck = hashlib.md5(open(dest+'Gandalf/VoiceControl.py', 'rb').read()).hexdigest()
dCheck = checksumDir(dest+'Gandalf', ['_config'])
print ('Checksums (source is first, destination is second):')
print (sCheck)
print (dCheck)
if sCheck == dCheck:
    print ('Checksum validated!')
else:
    print ('Checksums do not mach. An error may have occured. If you encounter any errors, please run the installation program again.')
##Exit
exit()
