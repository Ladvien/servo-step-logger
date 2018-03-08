from __future__ import division
import sys, termios, tty, os, time

import pymysql
# Connect to the database
connection = pymysql.connect(host='localhost',
                            user='alarm', 
                            passwd='alarm', 
                            db='db_servo_log')
cur = connection.cursor()

# Import the PCA9685 module.
import Adafruit_PCA9685

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

def get_number_steps_in_database():
    rows = 0
    q = "SELECT ID FROM servo_log"
    success = cur.execute(q)
    if success:
        connection.commit()
        rows = cur.rowcount
        print("Found "+ str(rows) + " steps")
    else:
        print("Connection to database failed")
    return rows

def read_step():
    q = "SELECT ID FROM servo_log"
    
    success = cur.execute(q)
    if success:
        connection.commit()
        rows = cur.rowcount
        print("Found "+ str(rows) + " steps")
    else:
        print("Connection to database failed")

def greeting():
    os.system('clear')
    print("Press 'q' to quit...")
    print("R: Resets the servo")
    print("B: Read steps from database")
    print("C: Delete database")

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    ch = ch.lower()
    return ch

def get_key(argument):
    argument = str(argument)
    argument = argument.lower()
    switcher = {
        "j": 1,
        "i": 5,
        "k": -5,
        "l": -1,
        "a": 1,
        "w": 5,
        "s": -5,
        "d": -1,
        "r": 99,
        "b": 88,
        "q": 5
    }
    return switcher.get(argument)

def reset_servos(reset_pos):
    # This only gets the first set of servos
    address = 0x40
    import Adafruit_GPIO.I2C as i2c
    device = i2c.get_i2c_device(0x00)
    if device is not None:
        device.writeRaw8(0x06)  # SWRST
    device = 0
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(60)
    pwm.set_pwm(0, 0, reset_pos)
    pwm.set_pwm(1, 1, reset_pos)
    print("Reset servos")

print("Welcome to the servo position reader")
print("C. Thomas Brittain")
print("(c) 2018-03-07")
print("")
greeting()

button_delay = 0.2
servo_position = [0, 0]

servo_min = 160  # Min pulse length out of 4096
servo_max = 550  # Max pulse length out of 4096
midpoint = 390   # Sets the middle position of the servo
reset_pos = 390  # If servos are reset, send to this position.
# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

# Set initial position for the servo.
servo_position = [midpoint, midpoint]
pwm.set_pwm(0, 0, servo_position[0])
pwm.set_pwm(1, 1, servo_position[1])
servo_num = 0
step_index = 0

rows = get_number_steps_in_database()
print(rows)

while True:
    k = getch()
    if k == 'q':
        exit(0)
    elif k == 'b':
        read_step()
    elif k == 'r':
        servo_position[0] = reset_pos
        servo_position[1] = reset_pos
        reset_servos(reset_pos)
    elif k is not None:
        greeting()