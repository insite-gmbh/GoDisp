#!/usr/bin/python
# coding=utf-8
import queue
import threading
import RPi.GPIO as GPIO
from time import sleep

class Gate (threading.Thread):
	
	ExitFlag = 0
	State = 0
	
	
	def __init__(self, openingChangedHandler):
		threading.Thread.__init__(self)
		self.step = 5
		self.dir = 7
		self.enable = 3
		self.minpos = 0
		self.maxpos = 200
		self.curpos = self.maxpos
		self.stop = 0
		self.qLock = threading.Lock();
		self.q = queue.Queue(10);
		self.openingChangedHandler = openingChangedHandler
		GPIO.setmode(GPIO.BOARD)
		GPIO.setwarnings(False)
		GPIO.setup(self.step, GPIO.OUT)
		GPIO.setup(self.dir, GPIO.OUT)
		GPIO.setup(self.enable, GPIO.OUT)
		GPIO.output(self.step, False)
		GPIO.output(self.dir, True)
		GPIO.output(self.enable, True)

	def _close(self):
		self._turn(0.005, self.maxpos, 1, True)

	def _open(self):
		self._turn(0.005, self.maxpos, 0, True)

	def _down(self, ticks):
		self._turn(0.005, ticks, 1, False)

	def _up(self, ticks):
		self._turn(0.005, ticks, 0, False)

	def _zero(self):
		self.curpos = self.minpos

	def _turn(self, speed, steps, direction, limits):
		if direction == 1:
			GPIO.output(self.dir, True)
			delta = -1
		else:
			GPIO.output(self.dir, False)
			delta = 1
		GPIO.output(self.enable, False)

		for i in range(0, steps):
			if (limits) and (((self.curpos + delta) < self.minpos) or ((self.curpos + delta) > self.maxpos)):
				break;
			GPIO.output(self.step, True)
			sleep(speed)
			GPIO.output(self.step, False)
			sleep(speed)
			self.curpos += delta
			self.openingChangedHandler(self, [self._stepsToPercentage(self.curpos), self.curpos])

		GPIO.output(self.enable, True)

	def run(self):
		while self.ExitFlag == 0:
			self.qLock.acquire()
			if not self.q.empty():
				data = self.q.get()
				self._processQData(data)
			self.qLock.release()
			sleep(0.05)
	
	def execute(self, cmd):
		self.qLock.acquire()
		self.q.put(cmd)
		self.qLock.release()
		
	def _processQData(self, data):
		self.State = 1
		if data[0] == "O":
			self._open()
		elif data[0] == "C":
			self._close()
		elif data[0] == "Z":
			self._zero()
		elif data[0] == "X":
			self.ExitFlag = 1
		elif data[0] == "S":
			if data[1] < 0:
				self._up(-(data[1]))
			elif data[1] > 0:
				self._down(data[1])
		elif data[0] == "P":
			targetPos = self._percentageToSteps(data[1])
			if targetPos > self.curpos:
				self._up(int(targetPos - self.curpos + 0.5))
			elif targetPos < self.curpos:
				self._down(int(self.curpos - targetPos + 0.5))
		else:
			targetPos = int(self._percentageToSteps(data[0]))
			if targetPos > self.curpos:
				self._up(int(targetPos - self.curpos + 0.5))
			elif targetPos < self.curpos:
				self._down(int(self.curpos - targetPos + 0.5))
		self.State = 0
		
	def _percentageToSteps(self, percentage):
		return self.minpos + (((self.maxpos - self.minpos) * percentage) / 100)
		
	def _stepsToPercentage(self, steps):
		return int(steps / (self.maxpos - self.minpos) * 100 + 0.5)
		
	def __del__(self):
		GPIO.cleanup()

