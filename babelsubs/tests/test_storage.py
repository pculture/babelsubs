import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest


from unittest import TestCase


from babelsubs import storage


class TimeHandlingTest(TestCase):

    def test_split(self):
        # should looke like 1h:10:20:200
        milliseconds  = (((1 * 3600 ) + (10 * 60 ) + (20 )) * 1000 )  + 200
        components = storage.milliseconds_to_time_clock_components(milliseconds)
        self.assertEquals((1,10, 20, 200), components)
        
    def test_rounding(self):
        milliseconds  = (((1 * 3600 ) + (10 * 60 ) + (20 )) * 1000 )  + 200.40
        components = storage.milliseconds_to_time_clock_components(milliseconds)
        self.assertEquals((1,10, 20, 200), components)

    def test_none(self):
        self.assertEquals((0,0, 0, 0), storage.milliseconds_to_time_clock_components(0))


    def test_expression(self):
        # should looke like 1h:10:20:200
        milliseconds  = (((1 * 3600 ) + (10 * 60 ) + (20 )) * 1000 )  + 200
        self.assertEquals("1:10:20:200", storage.milliseconds_to_time_expression(milliseconds))


    def test_parse_time_expression_clock_time_fraction(self):
        milliseconds  = (((3 * 3600 ) + (20 * 60 ) + (40 )) * 1000 )  + 200
        self.assertEquals(storage.parse_time_expression("3:20:40:200"), milliseconds)
        
    def test_parse_time_expression_clock_time(self):
        milliseconds  = (((3 * 3600 ) + (20 * 60 ) + (40 )) * 1000 )  
        self.assertEquals(storage.parse_time_expression("3:20:40"), milliseconds)


    def test_parse_time_expression_metric(self):
        self.assertEquals(storage.parse_time_expression("10h"), 10 * 3600 * 1000)
        self.assertEquals(storage.parse_time_expression("5m"), 5 * 60 * 1000)
        self.assertEquals(storage.parse_time_expression("3000s"),  3000 * 1000)
        self.assertEquals(storage.parse_time_expression("5000ms"), 5000)


