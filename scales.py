#!/usr/bin/python
# coding=utf-8
import queue
import threading
import serial
import numpy as np
from time import sleep

class Scales (threading.Thread):
	
	State = 0
	ExitFlag = 0
	
	def __init__(self, weightChangedHandler):
		threading.Thread.__init__(self)
		self.qCmdLock = threading.Lock()
		self.qCmd = queue.Queue(10);
		self.weightChangedHandler = weightChangedHandler
		self.ser = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0.1)
		self.lastRx = ""

	def _tare(self):
		self._send("T");
		self._waitzero();
		
	def _zero(self):
		self._send("Z");
		self._waitzero();

	def _waitzero(self):
		sleep(0.5);
		self._requestWeight();
		if not self.lastRx.find("0.000,kg"):
			raise ValueError("no zero weight received!") 
		
	def _requestWeight(self):
		self.ser.flushInput()
		self._send("S")
		sleep(1.0)
		self.lastRx = self._receive()
		self._processRxData(self.lastRx)

	def _send(self, data):
		self.ser.write(np.array([ord(c) for c in data]))
		
	def run(self):
		while self.ExitFlag == 0:
			if not self.qCmd.empty():
				self.qCmdLock.acquire()
				data = self.qCmd.get()
				self._processQCmdData(data)
				self.qCmdLock.release()
			rx = self._receive()
			if rx != self.lastRx:
				if rx == "":
					self.weightChangedHandler(self, 0)
				elif rx.startswith("ST"):
					self._processRxData(rx)
				self.lastRx = rx
			sleep(0.001)
	
	def _receive(self):
		ascii = self.ser.readline()
		return ''.join(chr(i) for i in ascii)
		
	def execute(self, cmd):
		self.qCmdLock.acquire()
		self.qCmd.put(cmd)
		self.qCmdLock.release()
		
	def _processQCmdData(self, data):
		self.State = 1
		if data[0] == "T":
			self._tare()
		elif data[0] == "Z":
			self._zero()
		elif data[0] == "R":
			self._requestWeight()
		elif data[0] == "X":
			self.ExitFlag = 1
		self.State = 0
		
	def _processRxData(self, rx):
		self.weightChangedHandler(self, int(float(rx[4:-5]) * 1000.0 + 0.5))
		
	def __del__(self):
		self.ser.close()


