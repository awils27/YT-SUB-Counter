from time import sleep
import machine
import network
import urequests
from ht16k33segment14 import HT16K33Segment14

#Youtube API variables
#Channel id to recive subsribers from
channel = 'Your Channel ID Here'
#API key to acess youtube API
key = 'Your API Key Here'

#Network data
#Wifi SSID name
ssid = 'AH'
#Wifi password name
password = 'Lillie The Dog'

# Update the pin values for your board
DEVICE_I2C_SCL_PIN = 5
DEVICE_I2C_SDA_PIN = 4


#LED on the board
smd = machine.Pin("LED", machine.Pin.OUT)


#Create the needed interface for the 14 segment display.
i2c = machine.I2C(0, scl=machine.Pin(DEVICE_I2C_SCL_PIN), sda=machine.Pin(DEVICE_I2C_SDA_PIN))
led = HT16K33Segment14(i2c, 112, True)
led.set_brightness(6)
led.clear().draw()


#Function for error handling and siaplying on screen.
def Error(type):
    led.clear().draw()
    led.set_character('E', 0).set_character('R', 1).draw()
    led.set_character('R', 2).set_character(type, 3).draw()

#Function for network connection
def connect(ssid, password):
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print('Waiting for connection...')
        led.clear().draw()
        led.set_character('C', 0).set_character('O', 1).draw()
        led.set_character('N', 2).set_character('N', 3).draw()
        led.set_blink_rate(1)
        sleep(2)
    ip = wlan.ifconfig()[0]
    led.clear().draw()
    led.set_blink_rate(0)
    print(f'Connected on {ip}')
    return ip

#Function for getting youtube stats
def get_subs(channel, key):
    response = urequests.get('https://www.googleapis.com/youtube/v3/channels?part=statistics&id=' + channel + '&key=' + key)
    data = response.json()
    subs_raw = int(data['items'][0]['statistics']['subscriberCount'])
    print(subs_raw)
    return subs_raw

#Function for remopving trailing 0s
def formatNumber(num):
  if num % 1 == 0:
    return int(num)
  else:
    return num

#Function for converting raw subscriber numbers into text to be represented on the segmented display.
def sub_multiplex(sub_raw):
    #Define the local variables we need.
    subs = sub_raw
    rep = ''

    #If the sub count is less than 1000 then leave it as is.
    if sub_raw <= 999:
        rep = ''

    #if it is less than 1 million then divide by 1000 and remove tralling 0s.
    elif sub_raw <= 999999:
        subs = formatNumber(sub_raw/1000)
        rep = 'K'

    #if it is less than 1 billion then divide by 1 million and remove tralling 0s.
    elif sub_raw <= 999999999:
        subs = formatNumber(sub_raw/1000000)
        rep = 'M'

    #Or repport an error
    else:
        Error('1')

    #Return the formated string to be displayed on the segmented display.
    return str(subs) + rep

#Function for the display of the subsriber count to the 14 segment display.
def segment(display):
    led.clear().draw()
    if len(display) == 5:
        pos = 0
        split = display.split('.')
        dec = False

        for x in split[0]:
            led.set_character(x, pos).draw()
            pos +=1

        for x in split[1]:
            led.set_character(x, pos).draw()
            pos +=1

        dec = display.find('.') - 1
        char = split[0][dec]
        led.set_character(char, dec, True).draw()


    elif len(display)<= 4:
        pos = 4 - len(display)
        for x in display:
            led.set_character(x, pos).draw()
            pos +=1

    else:
        Error('2')

#Loop counter.
NumLoops = 0

#Test error working
Error('0')
led.clear().draw()
smd.value(1)

#Connect to the wifi
ip = connect(ssid, password)
sleep(0.5)

#Main loop
while 1:
    NumLoops +=1
    smd.value(1)
    segment(sub_multiplex(get_subs(channel, key)))
    smd.value(0)
    print('Loops: ' + str(NumLoops))
    sleep(1800)