#!/usr/bin/python
# coding=utf-8
from tkinter import *
import tkinter.font as tkf
import signal

import queue
import threading
from time import sleep

class GuiPart:
	
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        # Set up the GUI
        console = Button(master, text='Done', command=endCommand)
        console.pack()
        # Add more GUI stuff here

    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                print(msg)
            except Queue.Empty:
                pass
                
                
