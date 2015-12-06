#!/usr/bin/python
# coding=utf-8
import RPi.GPIO as GPIO
from time import sleep
from tkinter import *
import tkinter.font as tkf
import signal

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

step = 5
dir = 7
enable = 3
minpos = 0
maxpos = 300
curpos = minpos
stop = 0

GPIO.setup(step, GPIO.OUT)
GPIO.setup(dir, GPIO.OUT)
GPIO.setup(enable, GPIO.OUT)

GPIO.output(step, False)
GPIO.output(dir, True)
GPIO.output(enable, True)

mywin = Tk()
mywin.wm_title('StepperMove')

def btn_left_click():
    turn(0.005, maxpos, 1, True)

def btn_right_click():
    turn(0.005, maxpos, 0, True)

def btn_lefttick_click():
    turn(0.005, 10, 1, False)

def btn_righttick_click():
    turn(0.005, 1, 0, False)

def btn_cycle_click():
    stop = 0
    if curpos == 0:
        for i in range(0, 3):
            btn_right_click()
            sleep(1)
            turn(0.005, int(maxpos / 2), 1, True)
            sleep(1)
            turn(0.005, int(maxpos / 2), 1, True)
            # btn_left_click()
            sleep(2)
        
def btn_stop_click():
    stop = 1

def btn_exit_click():
    sys.exit()

def btn_zero():
    global curpos
    curpos = minpos

def strg_c():
    mywin.quit()

def do_nothing():
    mywin.after(200, do_nothing)
    
def win_close():
    mywin.quit()
    
Button(mywin, text='Down', command=btn_left_click).grid(column=0, row=0, sticky=W)
Button(mywin, text='Up', command=btn_right_click).grid(column=2, row=0, sticky=W)
Button(mywin, text='Exit', command=btn_exit_click).grid(column=1, row=0, sticky=W)
Button(mywin, text='TickDn', command=btn_lefttick_click).grid(column=0, row=1, sticky=W)
Button(mywin, text='Zero', command=btn_zero).grid(column=1, row=1, sticky=W)
Button(mywin, text='TickUp', command=btn_righttick_click).grid(column=2, row=1, sticky=W)
Button(mywin, text='Cycle', command=btn_cycle_click).grid(column=0, row=2, sticky=W)
Button(mywin, text='Stop', command=btn_stop_click).grid(column=2, row=2, sticky=W)

mywin.protocol('WM_DELETE_WINDOW', win_close)
signal.signal(signal.SIGINT, strg_c)

def turn(speed, steps, direction, limits):
    global curpos
    if direction == 1:
        GPIO.output(dir, True)
        delta = -1
    else:
        GPIO.output(dir, False)
        delta = 1
    GPIO.output(enable, False)

    for i in range(0, steps):
        if (limits) and (((curpos + delta) < minpos) or ((curpos + delta) > maxpos)):
            break;
        GPIO.output(step, True)
        sleep(speed)
        GPIO.output(step, False)
        sleep(speed)
        curpos += delta

    print(curpos)
    GPIO.output(enable, True)

    return

mywin.mainloop()
GPIO.cleanup()

