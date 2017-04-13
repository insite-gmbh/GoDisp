#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=C0303
# pylint: disable=W0621
# pylint: disable=W0312

import unittest.mock as mock
import unittest
from stats import statistics
from gate import Gate
from flowControl import FlowControl
from flowDetection import FlowDetection
from wsgiref.validate import assert_
from numpy.ma.testutils import assert_equal

class dispTest(unittest.TestCase):

    def test_negativeSlope(self):
        stats = statistics(3)
        stats.addSample(4)
        stats.addSample(3)
        stats.addSample(2)
        stats.addSample(1)

        slope = stats.getSlope()
        stats.reset()
        self.assertEqual(slope, -1)

    def test_positiveSlope(self):
        stats = statistics(3)
        stats.reset()
        stats.addSample(100)
        stats.addSample(200)
        stats.addSample(300)
        stats.addSample(400)
        slope = stats.getSlope()

        self.assertEqual(slope, 100)

    def test_averageY(self):
        stats = statistics(3)
        stats.addSample(2)
        stats.addSample(2)
        stats.addSample(2)

        avg = stats.getAvgY()
        stats = statistics(3)
        self.assertEqual(avg, 2)
    

    def test_circularsamplebuffer(self):
        stats = statistics(3)
        stats.reset()
        stats.addSample(1)
        self.assertEqual(stats.getCountSamples(), 1)
        stats.addSample(2)
        self.assertEqual(stats.getCountSamples(), 2)
        stats.addSample(3)
        self.assertEqual(stats.getCountSamples(), 3)
        stats.addSample(4)
        self.assertEqual(stats.getCountSamples(), 3)
        stats.addSample(5)
        self.assertEqual(stats.getCountSamples(), 3)
        
    def test_RestStatistics(self):
        stats = statistics(3)
        stats.addSample(1)
        stats.addSample(1)
        stats.reset()
        self.assertEqual(0,stats.getCountSamples())
    
    
    @mock.patch("gate.Gate")
    @mock.patch("flowDetection.FlowDetection")
    def test_FlowControlCSV(self, mockGate, mockFlowDetection):       
        flowcontrol = FlowControl(mockGate, mockFlowDetection)
        flowcontrol.start()
        flowcontrol.setTargetFlow(0)
        assert_equal(0,flowcontrol.findGateOpeningCSV())
        
if __name__ == '__main__':
    unittest.main()


