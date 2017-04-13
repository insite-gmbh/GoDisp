#!/usr/bin/env python
# -*- coding: utf-8 -*-

class rumbler:
    
    gate = None
    blocked = False
    
       
    def __init__(self, gate):
        self.gate = gate
        
    def unblock(self):
        self.blocked = False        
    
    def block(self):
        self.blocked = True
            
    def fine(self):
        if not self.blocked:
            print("-------------------RUMBLE FINE ------------------------------")
            self.gate.execute(["S",-3])
            self.gate.execute(["S",3])
            
    def coarse(self):
        if not self.blocked:
            print("-------------------RUMBLE COARSE ------------------------------")
            self.gate.execute(["S",-15])
            self.gate.execute(["S",15])        
        