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
			if (limits) and (((self.curpos + delta) < self.minpos) or ((self.curpos + delta) > self.maxpos)):
				break;
			GPIO.output(step, True)
			sleep(speed)
			GPIO.output(step, False)
			sleep(speed)
			self.curpos += delta
		GPIO.output(enable, True)

	def run(self):
		while ExitFlag == 0:
			qLock.acquire()
			if not q.empty():
				data = q.get()
				self._processQData(data)
			qLock.release()
			sleep(0.05)
	
	def execute(self, cmd):
		qLock.acquire()
		qLock.put(cmd)
		qLock.release()
		
	def _processQData(self, data):
		State = 1
		if data[0] == "O":
			self._open()
		elif data[0] == "C":
			self._close(self)
		elif data[0] == "Z":
			self._zero(self)
		elif data[0] == "X":
			self.ExitFlag = 1
		else:
			targetPos = self._percentage(int(data))
			if targetPos > self.curpos:
				self._up(targetPos - self.curpos)
			elif targetPos < self.curpos:
				self._down(self.curpos - targetPos)
		State = 0
		
	def _percentageToSteps(self, percentage):
		return self.minpos + (((self.maxpos - self.minpos) * percentage) / 100)
		
	def __del__(self):
		GPIO.cleanup()

