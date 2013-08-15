from unittest2 import TestCase
from babelsubs.storage import SubtitleSet, SubtitleLine, diff, calc_changes

class DiffingTest(TestCase):
    def test_empty_subs(self):
        result = diff(SubtitleSet('en'), SubtitleSet('en'))
        self.assertEqual(result['changed'], False)
        self.assertEqual(result['text_changed'], 0)
        self.assertEqual(result['time_changed'], 0)
        self.assertEqual(len(result['subtitle_data']), 0)


    def empty_line(self):
        return SubtitleLine(None, None, None, None)

    def test_one_set_empty(self):
        set_1 = SubtitleSet.from_list('en', [
            (0, 1000, "Hey 1"),
            (1000, 2000, "Hey 2"),
            (2000, 3000, "Hey 3"),
            (3000, 4000, "Hey 4"),
        ])
        result = diff(set_1, SubtitleSet('en'))
        self.assertEqual(result['changed'], True)
        self.assertEqual(result['text_changed'], 1.0)
        self.assertEqual(result['time_changed'], 1.0)

    def test_text_changes(self):
        set_1 = SubtitleSet.from_list('en', [
            (0, 1000, "Hey 1"),
            (1000, 2000, "Hey 2"),
            (2000, 3000, "Hey 3"),
            (3000, 4000, "Hey 4"),
            ])
        set_2 = SubtitleSet.from_list('en', [
            (0, 1000, "Hey 1"),
            (1000, 2000, "Hey 22"),
            (2000, 3000, "Hey 3"),
            (3000, 4000, "Hey 4"),
            ])
        result = diff(set_1, set_2)
        self.assertEqual(result['changed'], True)
        self.assertEqual(result['text_changed'], 1/4.0)
        self.assertEqual(result['time_changed'], 0)
        self.assertEqual(len(result['subtitle_data']), 4)
        # only sub #2 should have text changed
        for i,sub_data in enumerate(result['subtitle_data']):
            self.assertEqual(sub_data['text_changed'], i ==1)

    def test_time_changes(self):
        set_1 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (1000, 2000, "Hey 2"),
         (2000, 3000, "Hey 3"),
         (3000, 4000, "Hey 4"),
        ])
        set_2 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (1200, 2000, "Hey 2"),
         (2000, 3000, "Hey 3"),
         (3000, 4000, "Hey 4"),
        ])
        result = diff(set_1, set_2)
        self.assertEqual(result['changed'], True)
        self.assertEqual(result['time_changed'], 1/4.0)
        self.assertEqual(result['text_changed'], 0)
        self.assertEqual(len(result['subtitle_data']), 4)
        # only sub #2 should have text changed
        for i,sub_data in enumerate(result['subtitle_data']):
            self.assertEqual(sub_data['time_changed'], i ==1)
            self.assertFalse(sub_data['text_changed'])

    def check_unchanged_subtitle_data(self, result, set_1, set_2, *indexes):
        for i in indexes:
            sub_data = result['subtitle_data'][i]
            self.assertEquals(sub_data['time_changed'], False)
            self.assertEquals(sub_data['text_changed'], False)
            self.assertEquals(sub_data['subtitles'][0],
                              sub_data['subtitles'][1])

    def test_insert(self):
        set_1 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (1000, 2000, "Hey 2"),
         (2000, 3000, "Hey 3"),
         (3000, 4000, "Hey 4"),
        ])
        set_2 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (500, 800, "Hey 1.5"),
         (1000, 2000, "Hey 2"),
         (2000, 3000, "Hey 3"),
         (3000, 4000, "Hey 4"),
        ])
        result = diff(set_1, set_2)
        self.assertEqual(result['changed'], True)
        # for both time_change and text_changed, we calculate them as follows:
        # there are 9 total subs.  8 of those are matches and 1 is new in
        # set_2.  So the change amount is 1/9
        self.assertAlmostEqual(result['time_changed'], 1/9.0)
        self.assertAlmostEqual(result['text_changed'], 1/9.0)
        self.assertEqual(len(result['subtitle_data']), 5)

        # check the lines that haven't changed
        self.check_unchanged_subtitle_data(result, set_1, set_2, 0, 2, 3, 4)
        # check the line that was inserted
        insert_sub_data = result['subtitle_data'][1]
        self.assertEquals(insert_sub_data['time_changed'], True)
        self.assertEquals(insert_sub_data['text_changed'], True)
        self.assertEquals(insert_sub_data['subtitles'][0], self.empty_line())
        self.assertEquals(insert_sub_data['subtitles'][1], set_2[1])

    def test_delete(self):
        set_1 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (1000, 2000, "Hey 2"),
         (2000, 3000, "Hey 3"),
         (3000, 4000, "Hey 4"),
        ])
        set_2 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (2000, 3000, "Hey 3"),
         (3000, 4000, "Hey 4"),
        ])
        result = diff(set_1, set_2)
        self.assertEqual(result['changed'], True)
        # for both time_change and text_changed, we calculate them as follows:
        # there are 7 total subs.  6 of those are matches and 1 is new in
        # set_2.  So the change amount is 1/9
        self.assertAlmostEqual(result['time_changed'], 1/7.0)
        self.assertAlmostEqual(result['text_changed'], 1/7.0)
        self.assertEqual(len(result['subtitle_data']), 4)

        # check the lines that haven't changed
        self.check_unchanged_subtitle_data(result, set_1, set_2, 0, 2, 3)
        # check the line that was deleted
        delete_sub_data = result['subtitle_data'][1]
        self.assertEquals(delete_sub_data['time_changed'], True)
        self.assertEquals(delete_sub_data['text_changed'], True)
        self.assertEquals(delete_sub_data['subtitles'][1], self.empty_line())
        self.assertEquals(delete_sub_data['subtitles'][0], set_1[1])

    def test_simple_replace(self):
        set_1 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (1000, 2000, "Hey 2"),
         (2000, 3000, "Hey 3"),
         (3000, 4000, "Hey 4"),
        ])
        set_2 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (1000, 2000, "Hey New 2"),
         (2000, 3000, "Hey 3"),
         (3000, 4000, "Hey 4"),
        ])
        result = diff(set_1, set_2)
        self.assertEqual(result['changed'], True)
        self.assertAlmostEqual(result['time_changed'], 0)
        # for text_changed, we calculate as follows: there are 8 total subs.
        # 6 of those are matches and 1 is different in both sets.  So 2/8.0
        # has been changed.
        self.assertAlmostEqual(result['text_changed'], 2/8.0)
        self.assertEqual(len(result['subtitle_data']), 4)

        # check the lines that haven't changed
        self.check_unchanged_subtitle_data(result, set_1, set_2, 0, 2, 3)
        # check the line that was inserted
        insert_sub_data = result['subtitle_data'][1]
        self.assertEquals(insert_sub_data['time_changed'], False)
        self.assertEquals(insert_sub_data['text_changed'], True)
        self.assertEquals(insert_sub_data['subtitles'][0], set_1[1])
        self.assertEquals(insert_sub_data['subtitles'][1], set_2[1])

    def test_replace_single_line_with_multiple(self):
        set_1 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (1000, 2000, "Hey 2"),
         (2000, 3000, "Hey 3"),
         (3000, 4000, "Hey 4"),
        ])
        set_2 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (1000, 1500, "Hey 2.1"),
         (1500, 2000, "Hey 2.2"),
         (2000, 3000, "Hey 3"),
         (3000, 4000, "Hey 4"),
        ])
        result = diff(set_1, set_2)
        self.assertEqual(result['changed'], True)
        # for both time_change and text_changed, we calculate them as follows:
        # there are 9 total subs.  6 of those are matches and 1 in set 1 was
        # changed to 2 in set 2.  So the change amount is 3/9.
        self.assertAlmostEqual(result['time_changed'], 3/9.0)
        self.assertAlmostEqual(result['text_changed'], 3/9.0)
        self.assertEqual(len(result['subtitle_data']), 5)

        # check the lines that haven't changed
        self.check_unchanged_subtitle_data(result, set_1, set_2, 0, 3, 4)
        # line 1 in set_1 was replaced my lines 2 and 3 in set_2
        line1 = result['subtitle_data'][1]
        self.assertEquals(line1['time_changed'], True)
        self.assertEquals(line1['text_changed'], True)
        self.assertEquals(line1['subtitles'][0], set_1[1])
        self.assertEquals(line1['subtitles'][1], set_2[1])
        line2 = result['subtitle_data'][2]
        self.assertEquals(line2['time_changed'], True)
        self.assertEquals(line2['text_changed'], True)
        self.assertEquals(line2['subtitles'][0], self.empty_line())
        self.assertEquals(line2['subtitles'][1], set_2[2])

    def test_replace_multiple_lines_with_single(self):
        set_1 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (1000, 2000, "Hey 2"),
         (2000, 3000, "Hey 3"),
         (3000, 4000, "Hey 4"),
        ])
        set_2 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (1000, 3000, "Hey 2 and 3"),
         (3000, 4000, "Hey 4"),
        ])
        result = diff(set_1, set_2)
        self.assertEqual(result['changed'], True)
        # for both time_change and text_changed, we calculate them as follows:
        # there are 7 total subs.  4 of those are matches and 2 in set_1 were
        # replaced with 1 in set_2.  So the change amount is 3/7.
        self.assertAlmostEqual(result['time_changed'], 3/7.0)
        self.assertAlmostEqual(result['text_changed'], 3/7.0)
        self.assertEqual(len(result['subtitle_data']), 4)

        # check the lines that haven't changed
        self.check_unchanged_subtitle_data(result, set_1, set_2, 0, 3)
        # check the line that was inserted
        line1 = result['subtitle_data'][1]
        self.assertEquals(line1['time_changed'], True)
        self.assertEquals(line1['text_changed'], True)
        self.assertEquals(line1['subtitles'][0], set_1[1])
        self.assertEquals(line1['subtitles'][1], set_2[1])
        line2 = result['subtitle_data'][2]
        self.assertEquals(line2['time_changed'], True)
        self.assertEquals(line2['text_changed'], True)
        self.assertEquals(line2['subtitles'][0], set_1[2])
        self.assertEquals(line2['subtitles'][1], self.empty_line())

    def test_data_ordering(self):
        set_1 = SubtitleSet.from_list('en', [
            (0, 1000, "Hey 1"),
        ])
        set_2 = SubtitleSet.from_list('en', [
            (0, 1000, "Hey 1"),
            (1200, 2000, "Hey 2"),
            (2000, 3000, "Hey 3"),
        ])
        result = diff(set_1, set_2)

        subs_result = result['subtitle_data'][2]['subtitles']
        # make sure the 0 index subs is for set_1, test
        # we respect the ordering of arguments passed to diff
        self.assertEqual(subs_result[0].text , None)
        self.assertEqual(subs_result[1].text , "Hey 3")

    def test_unsynced_reflect_time_changes(self):
        set_1 = SubtitleSet.from_list('en', [
            (0, 1000, "Hey 1"),
            ])
        set_2 = SubtitleSet.from_list('en', [
            (0, 1000, "Hey 1"),
            (None, None, "Hey 2"),
            ])
        result = diff(set_1, set_2)

        self.assertAlmostEqual(result['time_changed'], 1/3.0)

    def test_calc_changes(self):
        set_1 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (1000, 2000, "Hey 2"),
         (2000, 3000, "Hey 3"),
         (3000, 4000, "Hey 4"),
        ])
        set_2 = SubtitleSet.from_list('en', [
         (0, 1000, "Hey 1"),
         (1000, 2000, "Hey New 2"),
         (2000, 3000, "Hey 3"),
         (3000, 4000, "Hey 4"),
        ])
        text_changed, time_changed = calc_changes(set_1, set_2)
        self.assertAlmostEqual(time_changed, 0)
        self.assertAlmostEqual(text_changed, 2/8.0)
