#!/usr/bin/python
# coding=utf-8
import Queue
import threading
import RPi.GPIO as GPIO
from time import sleep

class Gate (threading.Thread):
	
	ExitFlag = 0
	State = 0
	
	
	def __init__(self):
		threading.Thread.__init__(self)
		self.step = 5
		self.dir = 7
		self.enable = 3
		self.minpos = 0
		self.maxpos = 300
		self.curpos = minpos
		self.stop = 0
		self.qLock = threading.Lock();
		self.q = Queue.Queue(10);
		GPIO.setmode(GPIO.BOARD)
		GPIO.setwarnings(False)
		GPIO.setup(step, GPIO.OUT)
		GPIO.setup(dir, GPIO.OUT)
		GPIO.setup(enable, GPIO.OUT)
		GPIO.output(step, False)
		GPIO.output(dir, True)
		GPIO.output(enable, True)

	def _close(self):
		self.turn(0.005, self.maxpos, 1, True)

	def _open(self):
		self.turn(0.005, self.maxpos, 0, True)

	def _down(self, ticks):
		self.turn(0.005, ticks, 1, False)

	def _up(self, ticks):
		self.turn(0.005, ticks, 0, False)

	def _zero(self):
		self.curpos = self.minpos

	def _turn(self, speed, steps, direction, limits):
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
		GPIO.output(enable, True)

	def run(self):
		while ExitFlag == 0:
			
			time.sleep(0.005)
		self.name.exit();	
		
	def __del__(self):
		GPIO.cleanup()

