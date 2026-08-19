import os
import unittest
from unittest.mock import patch

import duolingo

USERNAME = os.environ.get('DUOLINGO_USER', 'ferguslongley')
PASSWORD = os.environ.get('DUOLINGO_PASSWORD')
JWT = os.environ.get('DUOLINGO_JWT')


def _example_word(lang):
    """
    Returns an example word for a given language
    :param lang: str Language abbreviation
    :return: A word. Should be one early in the vocab for that language
    """
    return {
        "de": "mann",
        "es": "hombre",
        "fr": "homme",
        "it": "uomo"
    }.get(lang)


class DuolingoTest(unittest.TestCase):

    @patch("duolingo.Duolingo._get_data")
    def test_password_jwt_or_file_needed(self, mock_data):
        with self.assertRaises(duolingo.DuolingoException):
            duolingo.Duolingo(USERNAME)
        mock_data.assert_not_called()

    @patch("duolingo.Duolingo._login")
    @patch("duolingo.Duolingo._get_data", return_value={"id": 1, "learning_language": "fr"})
    def test_password_only_calls_login(self, mock_login, mock_data):
        duolingo.Duolingo(USERNAME, PASSWORD or "dummy-password")
        mock_login.assert_called_once_with()
        mock_data.assert_called_once_with()

    @patch("duolingo.Duolingo._login")
    @patch("duolingo.Duolingo._get_data", return_value={"id": 1, "learning_language": "fr"})
    def test_jwt_only_calls_login(self, mock_login, mock_data):
        duolingo.Duolingo(USERNAME, jwt="jwt-example")
        mock_login.assert_called_once_with()
        mock_data.assert_called_once_with()

    @patch("duolingo.Duolingo._login")
    @patch("duolingo.Duolingo._get_data", return_value={"id": 1, "learning_language": "fr"})
    def test_file_only_calls_login(self, mock_login, mock_data):
        duolingo.Duolingo(USERNAME, session_file="temp/filename.json")
        mock_login.assert_called_once_with()
        mock_data.assert_called_once_with()


class DuolingoLoginTest(unittest.TestCase):
    lingo = None

    @classmethod
    def setUpClass(cls):
        if PASSWORD:
            cls.lingo = duolingo.Duolingo(USERNAME, PASSWORD)
        else:
            cls.lingo = duolingo.Duolingo(USERNAME, jwt=JWT)
        cls.lang = cls.lingo.user_data.learning_language

    @classmethod
    def tearDownClass(cls):
        if cls.lingo:
            cls.lingo.session.close()

    def test_get_user_info(self):
        response = self.lingo.get_user_info()
        assert isinstance(response, dict)
        assert "avatar" in response
        assert "id" in response
        assert "location" in response
        assert "learning_language_string" in response

    def test_get_settings(self):
        response = self.lingo.get_settings()
        assert isinstance(response, dict)
        assert "deactivated" in response

    def test_get_languages(self):
        response1 = self.lingo.get_languages()
        assert isinstance(response1, list)
        for course in response1:
            assert isinstance(course, dict)
            assert "learningLanguage" in course
            assert isinstance(course["learningLanguage"], str)

    def test_get_friends(self):
        response = self.lingo.get_friends()
        assert isinstance(response, list)
        for friend in response:
            assert "username" in friend
            assert "totalXp" in friend
            assert isinstance(friend['totalXp'], int)
            assert "userId" in friend

    def test_get_calendar(self):
        response1 = self.lingo.get_calendar()
        response2 = self.lingo.get_calendar(self.lang)
        for response in [response1, response2]:
            assert isinstance(response, list)
            for item in response:
                assert "skill_id" in item
                assert "improvement" in item
                assert "event_type" in item
                assert "datetime" in item
                assert isinstance(item['datetime'], int)

    def test_get_streak_info(self):
        response = self.lingo.get_streak_info()
        assert isinstance(response, dict)
        assert "site_streak" in response
        assert "daily_goal" in response
        assert "streak_extended_today" in response

    def test_get_leaderboard(self):
        response = self.lingo.get_leaderboard()
        assert isinstance(response, list)
        for item in response:
            assert "score" in item
            assert "user_id" in item
            assert "display_name" in item

    def test_get_league_info(self):
        response = self.lingo.get_league_info()
        assert isinstance(response, dict)
        assert "tier" in response
        assert "tier_name" in response
        assert response["tier_name"] in duolingo.Duolingo.TIER_NAMES
        assert isinstance(response["position"], int)
        assert "contest_start" in response
        assert "contest_end" in response
        assert "is_demoted" in response
        assert "is_promoted" in response
        assert "stats" in response
        assert isinstance(response["stats"], dict)

    def test_get_language_details(self):
        language = self.lingo.get_language_from_abbr(self.lang)
        response = self.lingo.get_language_details(language)
        assert isinstance(response, dict)
        assert "current_learning" in response
        assert "language" in response
        assert "language_string" in response
        assert "learning" in response
        assert "level" in response
        assert "points" in response
        assert "streak" in response

    def test_get_language_progress(self):
        response = self.lingo.get_language_progress(self.lang)
        assert isinstance(response, dict)
        assert "language" in response
        assert "language_string" in response
        assert "level_left" in response
        assert "level_percent" in response
        assert "level_points" in response
        assert "level_progress" in response
        assert "next_level" in response
        assert "num_skills_learned" in response
        assert "points" in response
        assert "points_rank" in response
        assert "streak" in response

    def test_get_known_topics(self):
        response = self.lingo.get_known_topics(self.lang)
        assert isinstance(response, list)
        for topic in response:
            assert isinstance(topic, str)

    def test_get_unknown_topics(self):
        response = self.lingo.get_unknown_topics(self.lang)
        assert isinstance(response, list)
        for topic in response:
            assert isinstance(topic, str)

    def test_get_golden_topics(self):
        response = self.lingo.get_golden_topics(self.lang)
        assert isinstance(response, list)
        for topic in response:
            assert isinstance(topic, str)

    def test_get_reviewable_topics(self):
        response = self.lingo.get_reviewable_topics(self.lang)
        assert isinstance(response, list)
        for topic in response:
            assert isinstance(topic, str)

    def test_get_known_words(self):
        response = self.lingo.get_known_words(self.lang)
        assert isinstance(response, list)
        for word in response:
            assert isinstance(word, str)

    @unittest.skip("Duolingo removed the vocabulary overview endpoint")
    def test_get_related_words(self):
        # Setup
        word = _example_word(self.lang)
        # Get value
        response = self.lingo.get_related_words(word)
        # Check
        assert isinstance(response, list)

    def test_get_learned_skills(self):
        response = self.lingo.get_learned_skills(self.lang)
        assert isinstance(response, list)
        for skill in response:
            assert "language_string" in skill
            assert "id" in skill
            assert "title" in skill
            assert "explanation" in skill
            assert "progress_percent" in skill
            assert "words" in skill
            assert "name" in skill

    def test_get_language_from_abbr(self):
        response = self.lingo.get_language_from_abbr(self.lang)
        assert isinstance(response, str)

    def test_get_abbreviation_of(self):
        response = self.lingo.get_abbreviation_of('french')
        assert isinstance(response, str)

    @unittest.skip("Duolingo removed the translations endpoint (d2.duolingo.com no longer resolves)")
    def test_get_translations(self):
        response1 = self.lingo.get_translations('e')
        response2 = self.lingo.get_translations('e', self.lang)
        response3 = self.lingo.get_translations('e', self.lang, 'fr')
        for response in [response1, response2, response3]:
            assert isinstance(response, dict)
            assert "e" in response
            assert isinstance(response['e'], list)
        response = self.lingo.get_translations(['e', 'a'])
        assert isinstance(response, dict)
        assert "e" in response
        assert isinstance(response['e'], list)
        assert "a" in response
        assert isinstance(response['a'], list)

    def test_segment_translation_word_list(self):
        # Nothing should happen to short list
        short_list = ["a", "e", "i", "o", "u"]
        result = self.lingo._segment_translations_list(short_list)
        assert result == [short_list]
        # Just under count limit
        just_under_count = ["a"] * 1999
        result = self.lingo._segment_translations_list(just_under_count)
        assert result == [just_under_count]
        # Just over count limit
        just_over_count = ["a"] * 2000
        result = self.lingo._segment_translations_list(just_over_count)
        assert result != [just_over_count]
        assert result == [["a"] * 1999, ["a"]]
        # Just under json length limit
        just_under_length = ["aaaaaaaa"] * 1066
        result = self.lingo._segment_translations_list(just_under_length)
        assert result == [just_under_length]
        # Just over json length limit
        just_over_length = ["aaaaaaaa"] * 1067
        result = self.lingo._segment_translations_list(just_over_length)
        assert result != [just_over_length]
        assert result == [["aaaaaaaa"] * 1066, ["aaaaaaaa"]]

    @unittest.skip("Duolingo removed the vocabulary overview endpoint")
    def test_get_vocabulary(self):
        response1 = self.lingo.get_vocabulary()
        response2 = self.lingo.get_vocabulary(self.lang)
        for response in [response1, response2]:
            assert isinstance(response, dict)
            assert response['language_string']
            assert "language_string" in response
            assert "learning_language" in response
            assert response["learning_language"] == self.lang
            assert "from_language" in response
            assert "language_information" in response
            assert "vocab_overview" in response
            assert isinstance(response["vocab_overview"], list)

    @unittest.skip("Audio endpoints no longer return voice data")
    def test_get_audio_url(self):
        # Setup
        word = _example_word(self.lang)
        # Test
        response = self.lingo.get_audio_url(word)
        assert isinstance(response, str)
        response = self.lingo.get_audio_url(word, self.lang)
        assert isinstance(response, str)
        response = self.lingo.get_audio_url("zz")
        assert response is None

    @unittest.skip("Duolingo removed the dictionary_page endpoint")
    def test_get_word_definition_by_id(self):
        response = self.lingo.get_word_definition_by_id("52383869a8feb3e5cf83dbf7fab9a018")
        assert isinstance(response, dict)
        keys = ["alternative_forms", "translations", "learning_language_name", "from_language_name", "word"]
        for key in keys:
            assert key in response

    def test_get_daily_xp_progress(self):
        response = self.lingo.get_daily_xp_progress()
        assert isinstance(response['xp_goal'], int)
        assert isinstance(response['xp_today'], int)
        assert isinstance(response['lessons_today'], list)

    def test_get_xp_summaries(self):
        response = self.lingo.get_xp_summaries()
        assert isinstance(response, list)
        for summary in response:
            assert isinstance(summary['gainedXp'], int)
            assert isinstance(summary['date'], int)
            assert "streakExtended" in summary
            assert "frozen" in summary
            assert "numSessions" in summary
            assert "totalSessionTime" in summary

    def test_get_total_xp(self):
        response = self.lingo.get_total_xp()
        assert isinstance(response, int)

    def test_get_weekly_xp(self):
        response = self.lingo.get_weekly_xp()
        assert isinstance(response, int)

    def test_get_shop_items(self):
        response = self.lingo.get_shop_items()
        assert isinstance(response, list)
        for item in response:
            assert "itemName" in item

    def test_get_quest_schema(self):
        response = self.lingo.get_quest_schema()
        assert isinstance(response, list)
        for goal in response:
            assert "goalId" in goal
            assert "category" in goal

    def test_get_quest_progress(self):
        response = self.lingo.get_quest_progress()
        assert isinstance(response, dict)
        assert "goals" in response
        assert "badges" in response
        assert "difficulty" in response

    def test_get_daily_quests(self):
        response = self.lingo.get_daily_quests()
        assert isinstance(response, list)
        for quest in response:
            assert "goal_id" in quest
            assert "threshold" in quest
            assert isinstance(quest["progress"], int)
            assert isinstance(quest["progress_increments"], list)

    def test_get_monthly_challenge(self):
        response = self.lingo.get_monthly_challenge()
        assert isinstance(response, dict)
        assert "challenge" in response
        assert "earned_badges" in response
        assert isinstance(response["earned_badges"], list)
        assert response["challenge"] is not None

    def test_get_friends_quest(self):
        response = self.lingo.get_friends_quest()
        if response is not None:
            assert "goal_id" in response
            assert "social_progress" in response

    def test_get_friend_streak(self):
        response = self.lingo.get_friend_streak()
        assert isinstance(response, list)
        for match in response:
            assert "match_id" in match
            assert isinstance(match["users"], list)
            assert "has_active_streak" in match
            assert "streak_length" in match


if __name__ == '__main__':
    unittest.main()
