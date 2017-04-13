#!/usr/bin/python
# coding=utf-8
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=W0621
# pylint: disable=W0312
import queue
import threading
import numpy as np
import time
from Util.Publisher import Publisher

# raspi: serPort = "/dev/ttyUSB0"
# mac serPort = "/dev/tty.usbserial-FTDWE8ZH"

serPort = "/dev/ttyUSB0"

try:
	import serial
except ImportError:
	import MockSerial as serial
	
class Scales (threading.Thread, Publisher):
	
	State = 0
	ExitFlag = 0
	
	def __init__(self):
		threading.Thread.__init__(self)
		Publisher.__init__(self, ["WeightChanged"])
		self.qCmdLock = threading.Lock()
		self.qCmd = queue.Queue(10);
		self.ser = serial.Serial(serPort, baudrate=9600, timeout=0.1)
		self.lastRx = ""

	def _tare(self):
		self._send("T");
		self._waitzero();
		
	def _zero(self):
		self._send("Z");
		self._waitzero();

	def _waitzero(self):
		time.sleep(0.5);
		self._requestWeight();
		if not self.lastRx.find("0.000,kg"):
			raise ValueError("no zero weight received!") 
		
	def _requestWeight(self):
		self.ser.flushInput()
		self._send("S")
		time.sleep(1.0)
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
					Publisher.dispatch(self, "WeightChanged", [0, True])
				elif rx.startswith("ST") or rx.startswith("US"):
					self._processRxData(rx)
				self.lastRx = rx
			time.sleep(0.001)
		self.ser.close()
	
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
		stable = rx.startswith("ST")
		if stable or rx.startswith("US"):
			try:
				#print("scales rx: >", rx[4:-5], "<, stable=", stable)
				Publisher.dispatch(self, "WeightChanged", [int(float(rx[4:-5]) * 1000.0 + 0.5), stable])
			except:
				Publisher.dispatch(self, "WeightChanged", [0, True])
		
	def __del__(self):
		self.ser.close()


