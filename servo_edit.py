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

def save_step(step, servo_1_pos, servo_2_pos):
    q = "INSERT INTO servo_log_1 (step, servo_1, servo_2) \
    VALUES (" + str(step) + ", " + str(servo_1_pos) + ", " \
    + str(servo_2_pos) + ")"
    
    success = cur.execute(q)
    if success:
        connection.commit()
        print("Step "+ str(step) + " saved")
    else:
        print("Connection to database failed")

def delete_all_steps():
    q = "DELETE FROM servo_log_1"
    success = cur.execute(q)
    if success:
        connection.commit()
        print("Database deleted and recreated")
    else:
        print("Connection to database failed")

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

print("Welcome to the servo position editor")
print("C. Thomas Brittain")
print("(c) 2018-03-07")
print("")

def greeting():
    os.system('clear')
    print("Press 'q' to quit...")
    print("W and S: Increases / Decrease servo #1 position by 5.")
    print("A and D: Increases / Decrease servo #1 position by 1.")
    print("I and K: Increases / Decrease servo #1 position by 5.")
    print("J and L: Increases / Decrease servo #1 position by 1.")
    print("R: Resets the servo")
    print("B: Save step to database")
    print("C: Delete ddatabase")

greeting()
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
    if(switcher.get(argument) == "q"):
        reset_servos()
        exit(0)
    return switcher.get(argument)


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

while True:
    k = getch()
    if k == 'q':
        exit(0)
    elif k == 'c':
        delete_all_steps()
    elif k == 'r':
        servo_position[0] = reset_pos
        servo_position[1] = reset_pos
        reset_servos(reset_pos)
    elif k == 'b':
        save_step(step_index, servo_position[0], servo_position[1])
        step_index+=1
    elif k is not None:
        greeting()
        if (k == "i") or (k == "j") or (k == "k") or (k == "l"):
            servo_num = 1
        else:
            servo_num = 0
    
        pos = get_key(k)
        if pos is not None:
            servo_position[servo_num] += pos
            if servo_position[servo_num] < servo_min:
                for i in range(0, len(servo_position)):
                    servo_position[i] = servo_min
                print("Reached servo_min")
            if servo_position[servo_num] > servo_max:
                for i in range(0, len(servo_position)):
                        servo_position[i] = servo_max
                print("Reached servo_max")
            pwm.set_pwm(servo_num, servo_num, servo_position[servo_num])
            
            for i in range(0, len(servo_position)):
                print("Set servo #" + str([i]) + " to " + str(servo_position[i]))
            # time.sleep(1)