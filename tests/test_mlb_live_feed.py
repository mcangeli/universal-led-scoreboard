import unittest
from universal_led.mlb_live_feed import parse_live_pitch_details


class MLBLiveFeedTests(unittest.TestCase):
    def test_extracts_pitch_and_previous_play(self):
        payload={'liveData':{
            'plays':{
                'currentPlay':{'matchup':{'pitcher':{'id':42}},
                               'playEvents':[{'pitchData':{'startSpeed':94.6}}]},
                'allPlays':[{'about':{'isComplete':True},
                             'result':{'description':'Runner scores on a single.'}},
                            {'about':{'isComplete':False},
                             'result':{'description':'In progress'}}]},
            'boxscore':{'teams':{'home':{'players':{'ID42':{
                'stats':{'pitching':{'numberOfPitches':87}}}}}}}}}
        details=parse_live_pitch_details(payload)
        self.assertEqual(details.pitch_count,87)
        self.assertEqual(details.pitch_speed_mph,94.6)
        self.assertEqual(details.previous_play,'Runner scores on a single.')

    def test_empty_payload(self):
        details=parse_live_pitch_details({})
        self.assertIsNone(details.pitch_count)
        self.assertIsNone(details.pitch_speed_mph)
        self.assertIsNone(details.previous_play)

    def test_rejects_implausible_speed(self):
        payload={'liveData':{'plays':{'currentPlay':{'playEvents':[
            {'pitchData':{'startSpeed':-12}}]}}}}
        self.assertIsNone(parse_live_pitch_details(payload).pitch_speed_mph)


if __name__=='__main__':
    unittest.main()
