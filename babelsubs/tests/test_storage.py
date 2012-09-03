try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from babelsubs import storage
from babelsubs.tests import utils

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
        self.assertEquals("01:10:20.200", storage.milliseconds_to_time_clock_exp(milliseconds))


    def test_time_expression_to_milliseconds_clock_time_fraction(self):
        milliseconds  = (((3 * 3600 ) + (20 * 60 ) + (40 )) * 1000 )  + 200
        self.assertEquals(storage.time_expression_to_milliseconds("03:20:40.200"), milliseconds)
        
    def test_parse_time_expression_clock_time(self):
        milliseconds  = (((3 * 3600 ) + (20 * 60 ) + (40 )) * 1000 )  
        self.assertEquals(storage.time_expression_to_milliseconds("03:20:40"), milliseconds)


    def test_parse_time_expression_metric(self):
        self.assertEquals(storage.time_expression_to_milliseconds("10h"), 10 * 3600 * 1000)
        self.assertEquals(storage.time_expression_to_milliseconds("5m"), 5 * 60 * 1000)
        self.assertEquals(storage.time_expression_to_milliseconds("3000s"),  3000 * 1000)
        self.assertEquals(storage.time_expression_to_milliseconds("5000ms"), 5000)
        

    def test_parse_time_expression_clock_regex(self):
        def _components(expression, hours, minutes, seconds, fraction):
            match = storage.TIME_EXPRESSION_CLOCK_TIME.match(expression)
            self.assertTrue(match)
            self.assertEquals(int(match.groupdict()['hours']), hours)
            self.assertEquals(int(match.groupdict()['minutes']), minutes)
            self.assertEquals(int(match.groupdict()['seconds']), seconds)
            try:
                self.assertEquals(int(match.groupdict()['fraction']), fraction)
            except (ValueError, TypeError):
                self.assertEquals(fraction, None)


        _components("00:03:02", 0, 3, 2, None)
        _components("100:03:02", 100, 3, 2, None)
        _components("100:03:02.200", 100, 3, 2, 200)


    def test_normalize_time(self):
        content_str = open(utils.get_data_file_path("normalize-time.dfxp") ).read()
        dfxp = storage.SubtitleSet('en', content_str, normalize_time=True)
        subs = dfxp.get_subtitles()
        self.assertTrue(len(dfxp) )
        for el in subs:
            self.assertIn("begin", el.attrib)
            self.assertTrue(storage.TIME_EXPRESSION_CLOCK_TIME.match(el.attrib['begin']))
            self.assertIn("end", el.attrib)
            self.assertTrue(storage.TIME_EXPRESSION_CLOCK_TIME.match(el.attrib['end']))
            self.assertNotIn('dur', el.attrib)
        

class AddSubtitlesTest(TestCase):

    def _paragraphs_in_div(self, el):
        return [x for x in el.getchildren() if x.tag.endswith("}p")]
        
    def test_new_paragraph(self):
        dfxp = storage.SubtitleSet('en')
        dfxp.append_subtitle(0, 1000, "paragraph 1 - A")
        dfxp.append_subtitle(1000, 2000, "paragraph 1 - B")
        dfxp.append_subtitle(2000, 3000, "paragraph 2 - A", new_paragraph=True)
        dfxp.append_subtitle(3000, 4000, "paragraph 2 - B")
        dfxp.append_subtitle(3000, 4000, "paragraph 2 - C")
        divs = dfxp._ttml.xpath('/n:tt/n:body/n:div', namespaces={'n': storage.TTML_NAMESPACE_URI})
        self.assertEquals(len(divs), 2)
        self.assertEquals(len(self._paragraphs_in_div(divs[0])), 2)
        self.assertEquals(len(self._paragraphs_in_div(divs[1])), 3)
                     
        
