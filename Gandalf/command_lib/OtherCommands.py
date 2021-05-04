#Imports
import time
#Functions
##Test
def test(output):
    output('Test')
##Date & Time
def get_time(output):
    lt = time.localtime()
    if lt.tm_min == 0:
        timeFormat = 'It is currently '+str(lt.tm_hour)+' o clock'
    else:
        if lt.tm_min < 10:
            timeFormat = 'It is currently '+str(lt.tm_hour)+':0'+str(lt.tm_min)
        else:
            timeFormat = 'It is currently '+str(lt.tm_hour)+':'+str(lt.tm_min)
    output(timeFormat)
def get_date(output):
    lt = time.localtime()
    if lt.tm_min == 0:
        timeFormat = str(lt.tm_hour)+' o clock'
    else:
        if lt.tm_min < 10:
            timeFormat = str(lt.tm_hour)+':0'+str(lt.tm_min)
        else:
            timeFormat = str(lt.tm_hour)+':'+str(lt.tm_min)
    months = ['January', 'Febuary', 'March', 'April', 'May', 'June', 'July', 'Augest', 'September', 'October', 'November', 'December']
    month = months[lt.tm_mon-1]
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
