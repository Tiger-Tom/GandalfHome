#Imports
import os
import hashlib
import json
import random
import shutil
import time
#Functions
def fixDir(dir_path, ignoreNotExists=False):
    dir_path = dir_path.replace('\\', '/')
    if (not os.path.exists(dir_path)) and (not ignoreNotExists):
        print ('Error! Path does not exist')
        print (dir_path)
        raise FileNotFoundError(dir_path)
    if not dir_path.endswith('/'):
        return dir_path+'/'
    return dir_path
def checksumDir(path, ignoreDirs=[], forEach=True):
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
                newHash = checksumDir(path+'/'+i, ignoreDirs, forEach)
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
            retString.append('Checksum of file "'+str(i)+'":\n'+checksums[i])
    return '\n'.join(retString)
def writeCSumsAsCSV0(checksums, base='', depth=0):
    lines = []
    for i in checksums:
        if base != '':
            cD = base+'/'+i
        else:
            cD = i
        if type(checksums[i]) == dict:
            #line = cD+','+writeCSumsAsCSV0(checksums[i], cD, depth+1)
            line = writeCSumsAsCSV0(checksums[i], cD, depth+1)
        else:
            line = cD+','+checksums[i]+','+str(depth)
        lines.append(line)
    return '\n'.join(lines)
def writeCSumsAsCSV(checksums):
    top = 'file,checksum,depth'
    lines = writeCSumsAsCSV0(checksums)
    csvTxt = top+'\n'+lines
    return csvTxt
##Commands
def listCommands(baseDir):
    global commands
    ret = []
    for i in commands:
        ret.append('"'+i+'": '+commands[i][0])
    return '\n'.join(ret)
def resetProperties(baseDir):
    print ('Warning: This will only work on the newest version of properties.txt, and might not work even on versions that have been upgraded from previous versions.')
    doReset = input('Attempt to reset properties.txt to defaults? (A backup will be made) (y/N) >').lower()
    if doReset != 'y':
        return
    propsDir = baseDir+'/_config/properties.txt'
    bkpDir = baseDir+'/_config/properties.backup.txt'
    print ('Reading original properties:')
    print (propsDir)
    try:
        file = open(propsDir, 'r')
        propsRaw = file.read()
        file.close()
    except Exception as e:
        print ('A fatal error occured while attempting to read '+propsDir)
        print (e)
        return
    print ('Writing backup:')
    print (bkpDir)
    try:
        file = open(bkpDir, 'w')
        file.write(bkpDir)
        file.close()
    except Exception as e:
        print ('A fatal error occured while attempting to write '+bkpDir)
        print (e)
        if input('Continue? (Y/n) >').lower() == 'n':
            return
    properties = []
    print ('Parsing')
    print (propsRaw)
    lastDefault = None
    comments = 0
    properties = []
    for i in propsRaw.split('\n'):
        line = ''
        if i.startswith('##'):
            print ('Ignoring double-# comment')
            line = i
            #properties['comment_'+str(comments)] = i
            #comments += 1
        elif i.startswith('#'):
            #properties['comment_'+str(comments)] = i
            #comments += 1
            line = i
            print ('Found single-# comment')
            print (i)
            if 'default' in i:
                print ('Default exists')
                lastDefault = i.split('[')[1].split(']')[0][8:]
                print ('Potential default found: '+lastDefault)
            else:
                print ('Comment does not have default')
        else:
            try:
                nam,val = i.split(':')
                if lastDefault == None:
                    print ('No default found for variable '+nam)
                    print ('Leaving at current value ('+val+')')
                    #properties[nam] = val
                    line = nam+':'+val
                else:
                    print ('Potential default found for variable '+nam)
                    print ('Current value: '+val)
                    print ('Potential default: '+lastDefault)
                    #properties[nam] = lastDefault
                    line = nam+':'+lastDefault
                    lastDefault = None
            except Exception as e:
                print ('Error: '+str(e))
        print (line)
        properties.append(line)
    properties = '\n'.join(properties)
    doWrite = input('Write new properties? (Y/n) >').lower()
    if doWrite != 'n':
        try:
            file = open(propsDir, 'w')
            file.write(properties)
            file.close()
            print ('Success')
        except Exception as e:
            print ('A fatal error occured when writing properties')
            print(e)
def checksum(baseDir):
    return checksumDir(baseDir, ['_config', '__pycache__'], False)
def checksumForEach(baseDir):
    totalHash,checksums = checksumDir(baseDir, ['_config', '__pycache__'], True)
    print ('Total combined hash: '+totalHash)
    print ('Individual file and directory hashes:')
    print (displayForEachChecksum(checksums))
    saveFile = input('Save results to file? (y/N) >').lower()
    if saveFile != 'y':
        return
    fileTypes = {
        'text': '.txt (raw TeXT)',
        'json': '.json (JavaScript Object Notation)',
        'csv': '.csv (Comma-Seperated Variables)',
    }
    supTyp = []
    for i in fileTypes:
        supTyp.append('"'+i+'": '+fileTypes[i])
    supTyp = '\n'.join(supTyp)
    while True:
        print ('Supported file types:\n'+supTyp)
        fileType = input('Enter file type, or type "exit" to exit >').lower()
        if fileType == 'exit':
            print ('Done')
            break
        elif fileType == 'text':
            toWrite = displayForEachChecksum(checksums)
            ext = '.txt'
        elif fileType == 'json':
            toWrite = json.dumps(checksums)
            ext = '.json'
        elif fileType == 'csv':
            toWrite = writeCSumsAsCSV(checksums)
            ext = '.csv'
        else:
            print ('Unknown format "'+fileType+'"')
            toWrite = None
        if toWrite != None:
            print ('Contents:\n'+toWrite)
            try:
                fileDir = fixDir(input('Enter file directory to write to >'))
            except:
                print ('Error parsing given directory. Using current directory...')
                fileDir = fixDir(os.getcwd())+'gandalf_checksum'+ext
                print (fileDir)
            if not fileDir.endswith(ext):
                print ('Using default filename "gandalf_checksum'+ext+'"')
                fileDir += 'gandalf_checksum'+ext
            print ('File directory to write to:\n'+fileDir)
            correct = input('Is this correct? (Y/n) >').lower()
            if correct != 'n':
                if os.path.exists(fileDir):
                    #aOrO = input('File already exists. Select an option\n[0] Cancel\n[1] Append\n[2] Overwrite')
                    #try:
                    #    aOrO = int(aOrO)
                    #except:
                    #    print (aOrO+' is not a correct option. Please enter a number.')
                    #    aOrO = 0
                    cont = input('File already exists. It will be overwritten. Continue? (y/N) >').lower()
                    if cont == 'y':
                        cont = True
                    else:
                        cont = False
                else:
                    cont = True
                if cont:
                    print ('Writing to file '+fileDir)
                    try:
                        file = open(fileDir, 'w')
                        file.write(toWrite)
                        file.close()
                        print ('Successful')
                    except Exception as e:
                        print ('Failure:')
                        print (e)
def listProperties(baseDir):
    props = {}
    propsDir = baseDir+'/_config/properties.txt'
    try:
        file = open(propsDir, 'r')
        propsRaw = file.read()
        file.close()
    except Exception as e:
        return 'A fatal exception has occured\n'+str(e)
    print ('Read file. Parsing...')
    propsRaw = propsRaw.split('\n')
    for i in propsRaw:
        if i.startswith('#'):
            print ('Ignoring comment:\n'+i)
        else:
            try:
                nam,val = i.split(':')
                print ('Found property '+nam)
                props[nam] = val
            except Exception as e:
                print ('Unable to parse line\n'+i)
                print (e)
    pStr = ['----------', '', str(props), '', '----------', '']
    for i in props:
        pStr.append(i+' = '+props[i])
    return '\n'.join(pStr)
def clean(baseDir):
    ruSure = input('Are you sure you want to do this? This will permanently delete the directory '+baseDir+' and everything in it. (y/N) >')
    if ruSure != 'y':
        return 'Cancelled'
    ruSure0 = str(random.randint(1000, 9999))
    if input('Please enter the 4-digit pin: "'+ruSure0+'" >') != ruSure0:
        return 'Cancelled'
    print ('Deleting directory '+baseDir+' and all of it\'s contents in:')
    for i in range(5, 0, -1):
        print (i)
        time.sleep(1)
    print ('Deleting...')
    shutil.rmtree(baseDir+'/')
    print ('Done.')
    return False
def backup(baseDir):
    dest = fixDir(input('Enter destination directory >'), True)
    if input('Is '+dest+' correct? (Y/n) >').lower() == 'n':
        return
    try:
        print ('Copying...')
        if os.path.exists(dest):
            dest += '/Gandalf/'
        shutil.copytree(baseDir, dest)
        print ('Done')
    except Exception as e:
        print ('An error occured')
        print (e)
def exitCommand(baseDir):
    raise Exception('runExit')
def installRequirements(baseDir):
    reqDir = baseDir+'/requirements.txt'
    print ('requirements.txt dir is '+reqDir)
    if not os.path.exists(reqDir):
        return 'Error: '+reqDir+' not found.'
    try:
        print ('Attempting pip3 install...')
        code = os.system('pip3 install -r '+reqDir)
        if code != 0:
            raise Exception(str(code))
    except Exception as e:
        print ('pip3 install failed')
        print (e)
        try:
            print ('Attempting pip install...')
            code = os.system('pip install -r '+reqDir)
            if code != 0:
                raise Exception(str(code))
        except Exception as e:
            print ('pip install failed')
            print (e)
            print ('Unable to install requirements')
def installAptPackages(baseDir):
    packDir = baseDir+'/required-apt-installs.txt'
    if input('Attempt to install packages (Linux only) in required-apt-installs.txt? (y/N) >') != 'y':
        return 'Cancelled'
    if not os.path.exists(packDir):
        return 'Error: '+packDir+' not found'
    try:
        print ('Reading...')
        file = open(packDir, 'r')
        packsT = file.read()
        file.close()
        print ('Done')
    except Exception as e:
        print ('A fatal error occured while reading')
        return str(e)
    print ('Packages to install:\n'+packsT)
    packs = ' '.join(packsT.split('\n'))
    print ('sudo apt-get update')
    os.system('sudo apt-get update')
    print ('sudo apt-get upgrade')
    os.system('sudo apt-get upgrade')
    command = 'sudo apt-get install '+packs
    print (command)
    os.system(command)
def cleanupFiles(baseDir):
    print ('Cleaning dir '+baseDir)
    dirs = os.listdir(baseDir)
    ignore = ['System Volume Information', '_config']
    remove = ['__pycache__']
    for i in dirs:
        if not i in ignore:
            if i in remove:
                if os.path.isdir(baseDir+'/'+i):
                    print ('Removing directory '+baseDir+'/'+i)
                    shutil.rmtree(baseDir+'/'+i)
                else:
                    print ('Removing file '+baseDir+'/'+i)
                    os.remove(baseDir+'/'+i)
            elif os.path.isdir(baseDir+'/'+i):
                print ('Recursively cleaning '+baseDir+'/'+i)
                cleanupFiles(baseDir+'/'+i)
#Command List
commands = { #'command': ['Documentation', function],
    'help': ['This list', listCommands],
    'exit': ['Close this program', exitCommand],
    'reset_properties': ['Attempt to reset properties to defaults without having an external copy', resetProperties],
    'checksum': ['Get checksum of Gandalf files, excluding _config', checksum],
    'full_checksum': ['Get checksum of each file individually, and optionally save results to file', checksumForEach],
    'list_properties': ['List properties (formatted)', listProperties],
    'install_requirements': ['Install required Python modules from requirements.txt', installRequirements],
    'apt_install': ['Install required packages through apt-get (linux only!)', installAptPackages],
    'cleanup': ['Cleanup un-needed files', cleanupFiles],
    'uninstall': ['Delete Gandalf completely', clean],
    'backup': ['Make a backup of Gandalf at the chosen directory', backup],
}
#Main
##Get Directory
while True:
    gDir = fixDir(input('Enter Gandalf directory (Without /Gandalf) >'))+'Gandalf'
    print ('Working directory:\n'+gDir)
    correct = input('Is this correct? (Y/n) >').lower()
    if not os.path.exists(gDir):
        print ('Directory "'+gDir+'" does not exist.')
        correct = 'n'
    if correct != 'n':
        break
##Main Functions
while True:
    command = input('Enter command (Enter "help" for list of commands) >').lower()
    print ('Running command "'+command+'"')
    try:
        out = commands[command][1](gDir)
        if out == False:
            break
        elif out != None:
            print (out)
    except KeyError:
        print ('Unknown command "'+command+'". Check "help"?')
    except Exception as e:
        if command == 'exit':
            break
        else:
            print ('Error')
            print (e)
