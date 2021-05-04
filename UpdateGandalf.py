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
    if input('Install pip requirements? (Y/n) >') != 'n':
        print ('Installing required modules...')
        os.chdir(dest+'Gandalf')
        os.system('pip3 install -r requirements.txt')
        print ('Done')
def installAptRequirements(dest):
    if input('Install apt packages? (Y/n) >') != 'n':
        print ('Attempting to install required apt packages...')
        packDir = dest+'Gandalf/required-apt-installs.txt'
        requirements = open(packDir, 'r').read()
        print ('Installing apt packages:\n'+requirements)
        requirements = ' '.join(requirements.split('\n'))
        print ('sudo apt-get update')
        os.system('sudo apt-get update')
        print ('sudo apt-get upgrade')
        os.system('sudo apt-get upgrade')
        command = 'sudo apt-get install '+requirements
        print (command)
        print ('Return code: '+str(os.system(command)))
        print ('Done')
def checksumDir0(path, ignoreDirs=[], forEach=True):
    curH = ''
    hashesTotal = {}
    dirs = os.listdir(path)
    dirs.sort()
    for i in dirs:
        if os.path.isdir(path+'/'+i):
            if i in ignoreDirs:
                print ('Skipping dir '+i)
            else:
                print ('Recursively hashing dir '+i)
                newHash = checksumDir0(path+'/'+i, ignoreDirs, forEach)
                curH += newHash[0]
                hashesTotal[i] = newHash[1]
        else:
            if i in ignoreDirs:
                print ('Skipping file '+i)
            else:
                print ('Hashing file '+i)
                try:
                    curF = open(path+'/'+i, 'r', encoding='UTF-8', errors='ignore')
                    while True:
                        buffer = curF.read(4096).encode('UTF-8')
                        if not buffer:
                            break
                        try:
                            newHash = hashlib.md5(buffer).hexdigest()
                            hashesTotal[i] = newHash
                            curH += newHash
                        except Exception as e:
                            print ('An error occured')
                            print (e)
                except Exception as e:
                    print ('An error occured')
                    print (e)
                curF.close()
    totalHash = hashlib.md5(curH.encode('UTF-8')).hexdigest()
    if forEach:
        return [totalHash, hashesTotal]
    return totalHash
def displayForEachChecksum(checksums):
    retString = []
    for i in checksums:
        if type(checksums[i]) == dict:
            retString.append('Checksums of files in dir "'+str(i)+'":')
            retString.append(displayForEachChecksum(checksums[i]))
        else:
            retString.append('Checksum of file "'+str(i)+'": '+checksums[i])
    return '\n'.join(retString)
def checksumDir(path, ignoreDirs=[], forEach=True):
    totalHash,checksums = checksumDir0(path, ignoreDirs, forEach)
    retString = ['Total combined hash: '+totalHash, 'Individual file and directory hashes:']
    retString.append(displayForEachChecksum(checksums))
    return '\n'.join(retString)
#Main
##Folders & Files To Ignore During Checksum Calculation
checksumIgnore = ['_config', '__pycache__']
##Find Source & Destination
source = fixDir(input('Enter source directory (Without /Gandalf) >'))
dest = fixDir(input('Enter destination directory (Without /Gandalf) >'))
##Get Size
sourceSize = shutil.disk_usage(source)
destSize = shutil.disk_usage(dest)
print ('Source space used: '+str(sourceSize.used)+'/'+str(sourceSize.total))
print ('Destination space availiable: '+str(destSize.free)+'/'+str(destSize.total))
##Continue
input('Press enter to continue')
##Check If Already Exists
if not os.path.exists(dest+'Gandalf'):
    print ('No installation found. Installing...')
    shutil.copytree(source+'Gandalf', dest+'Gandalf')
    print ('Done')
    ##Install Modules
    ###Install Ubuntu Packages
    if os.name != 'nt':
        try:
            installAptRequirements(dest)
        except Exception as e:
            print ('An error occured while installing apt packages')
            print (e)
    ###Install Python Modules W/ PIP
    installRequirements(dest)
    ###Ubuntu Dist-Upgrade & Autoremove
    if os.name != 'nt':
        if input('Do a full apt dist-upgrade? (Y/n) >').lower() != 'n':
            try:
                print ('sudo apt-get dist-upgrade')
                os.system('sudo apt-get dist-upgrade')
            except Exception as e:
                print ('An error occured while running dist-upgrade')
                print (e)
        if input('Auto-remove un-needed apt packages? (Y/n) >').lower() != 'n':
            try:
                print ('sudo apt-get autoremove')
                os.system('sudo apt-get autoremove')
            except Exception as e:
                print ('An error occured while auto-removing packages')
                print (e)
    print ('Comparing checksums of files...')
    print ('Generating source checksum...')
    #sCheck = hashlib.md5(open(source+'Gandalf/VoiceControl.py', 'rb').read()).hexdigest()
    sCheck = checksumDir(source+'Gandalf', checksumIgnore)
    print ('Generating destination checksum...')
    #dCheck = hashlib.md5(open(dest+'Gandalf/VoiceControl.py', 'rb').read()).hexdigest()
    dCheck = checksumDir(dest+'Gandalf', checksumIgnore)
    print ('Checksums (source is first, destination is second):')
    print (sCheck)
    print (dCheck)
    if sCheck == dCheck:
        print ('Checksum validated!')
    else:
        print ('Checksums do not mach. An error may have occured. If you encounter any errors, please run the installation program again.')
else:
##Get Configuration
    resetConfig = input('Reset configuration to defaults? (y/N) >').lower()
    configFound = []
    if resetConfig == 'y':
        print ('Resetting config...')
        configFound = []
    else:
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
    dProp = open(dPropDir, 'r').read().split('\n')
    sProp = open(sPropDir, 'r').read().split('\n')
    properties = {}
    if sProp[-1] == '\n':
        del sProp[-1]
        print ('Removed newline from end of source properties')
    if dProp[-1] == '\n':
        del dProp[-1]
        print ('Removed newline from end of destination properties')
    commentNum = 0
    for i in dProp:
        try:
            if i[0] == '#':
                nam,value = ['comment_'+str(commentNum), i]
                properties[nam] = value
                commentNum += 1
            else:
                try:
                    nam,value = i.split(':')
                    print ('Read property '+nam+' from destination')
                    properties[nam] = value
                except:
                    print ('Cannot parse line '+i+'\nIgnoring...')
        except Exception as e:
            print (e)
    print ('Read properties:\n'+str(properties))
    print ('Reading source properties.txt')
    commentNum = 0
    for i in sProp:
        try:
            if i[0] == '#':
                nam,value = ['comment_'+str(commentNum), i]
                commentNum += 1
            else:
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
        except Exception as e:
            print (e)
    #print ('Destroying original properties.txt (DO NOT CLOSE PROGRAM NOW, OR YOU WILL LOSE ALL SAVED CONFIGURATION IN properties.txt!)...')
    #os.remove(dPropDir)
    print ('Parsing new properties.txt contents...')
    cont = []
    for i in properties:
        print ('Parsing '+i+'...')
        if i.startswith('comment_'):
            #cont = cont+properties[i]+'\n'
            cont.append(properties[i])
        else:
            #cont = cont+i+':'+properties[i]+'\n'
            cont.append(i+':'+properties[i])
    cont = '\n'.join(cont)
    print ('Writing new properties to properties.txt:')
    print (cont)
    open(dPropDir, 'w').write(cont)
    print ('Done repairing properties.txt')
##Fix audio_config.txt
    print ('Reading destination audio config')
    dAudDir = dest+'Gandalf/_config/audio_config.txt'
    sAudDir = source+'Gandalf/_config/audio_config.txt'
    dAud = open(sAudDir, 'r').read().split('\n')
    sAud = open(sAudDir, 'r').read().split('\n')
    audConf = {}
    if sAud[-1] == '\n':
        del sAud[-1]
        print ('Removed newline from end of source audio configuration')
    if dAud[-1] == '\n':
        del dAud[-1]
        print ('Removed newline from end of destination audio configuration')
    for i in dAud:
        nam,val = i.split(':')
        print ('Read audio configuration '+nam+' from destination')
        audConf[nam] = val
    print ('Read source audio configuration:')
    print (audConf)
    for i in sAud:
        nam,val = i.split(':')
        print ('Found audio configuration '+nam+' in source')
        try:
            audConf[nam]
            print ('Audio configurarion '+nam+' already exists')
        except:
            print ('Audio configurarion '+nam+' does not exist. Repairing...')
            audConf[nam] = val
    print ('Parsing new audio_config.txt contents...')
    cont = []
    for i in audConf:
        print ('Parsing '+i+'...')
        cont.append(i+':'+audConf[i])
    cont = '\n'.join(cont)
    print ('Writing new audio configuration to audio_config.txt:')
    print (cont)
    open(dAudDir, 'w').write(cont)
    print ('Done repairing audio_config.txt')
##Done With Config
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
        if i == '_config':
            print ('Skipping _config as it is configuration...')
        else:
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
###Install Ubuntu Packages
    if os.name != 'nt':
        try:
            installAptRequirements(dest)
        except Exception as e:
            print ('An error occured while installing apt packages')
            print (e)
###Install Python Modules W/ PIP
    installRequirements(dest)
###Ubuntu Dist-Upgrade & Autoremove
    if os.name != 'nt':
        if input('Do a full apt dist-upgrade? (Y/n) >').lower() != 'n':
            try:
                print ('sudo apt-get dist-upgrade')
                os.system('sudo apt-get dist-upgrade')
            except Exception as e:
                print ('An error occured while running dist-upgrade')
                print (e)
        if input('Auto-remove un-needed apt packages? (Y/n) >').lower() != 'n':
            try:
                print ('sudo apt-get autoremove')
                os.system('sudo apt-get autoremove')
            except Exception as e:
                print ('An error occured while auto-removing packages')
                print (e)
##Finish Installation
    print ('Installation complete!')
##Find Checksums
    print ('Comparing checksums of files...')
    print ('Generating source checksum...')
    #sCheck = hashlib.md5(open(source+'Gandalf/VoiceControl.py', 'rb').read()).hexdigest()
    sCheck = checksumDir(source+'Gandalf', checksumIgnore)
    print ('Generating destination checksum...')
    #dCheck = hashlib.md5(open(dest+'Gandalf/VoiceControl.py', 'rb').read()).hexdigest()
    dCheck = checksumDir(dest+'Gandalf', checksumIgnore)
    print ('Checksums (source is first, destination is second):')
    print (sCheck)
    print (dCheck)
    if sCheck == dCheck:
        print ('Checksum validated!')
    else:
        print ('Checksums do not mach. An error may have occured. If you encounter any errors, please run the installation program again.')
