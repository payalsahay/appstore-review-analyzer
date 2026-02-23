"""
Unit tests for sentiment analysis functionality
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CustomerInsight_Review_Agent import analyze_sentiment, SENTIMENT_KEYWORDS


class TestPositiveKeywords:
    """Tests for positive sentiment detection"""

    def test_love_keyword(self):
        """Test 'love' is detected as positive"""
        assert analyze_sentiment("I love this app") == "positive"

    def test_great_keyword(self):
        """Test 'great' is detected as positive"""
        assert analyze_sentiment("Great app for printing") == "positive"

    def test_excellent_keyword(self):
        """Test 'excellent' is detected as positive"""
        assert analyze_sentiment("Excellent quality prints") == "positive"

    def test_amazing_keyword(self):
        """Test 'amazing' is detected as positive"""
        assert analyze_sentiment("This app is amazing") == "positive"

    def test_perfect_keyword(self):
        """Test 'perfect' is detected as positive"""
        assert analyze_sentiment("Works perfect every time") == "positive"

    def test_multiple_positive_keywords(self):
        """Test multiple positive keywords boost positive score"""
        result = analyze_sentiment("Love this amazing app, works great and perfect!")
        assert result == "positive"


class TestNegativeKeywords:
    """Tests for negative sentiment detection"""

    def test_terrible_keyword(self):
        """Test 'terrible' is detected as negative"""
        assert analyze_sentiment("Terrible app") == "negative"

    def test_awful_keyword(self):
        """Test 'awful' is detected as negative"""
        assert analyze_sentiment("Awful experience") == "negative"

    def test_crash_keyword(self):
        """Test 'crash' is detected as negative"""
        assert analyze_sentiment("The app keeps crashing") == "negative"

    def test_useless_keyword(self):
        """Test 'useless' is detected as negative"""
        assert analyze_sentiment("Completely useless app") == "negative"

    def test_frustrating_keyword(self):
        """Test 'frustrating' is detected as negative"""
        assert analyze_sentiment("Very frustrating to use") == "negative"

    def test_multiple_negative_keywords(self):
        """Test multiple negative keywords"""
        result = analyze_sentiment("Terrible awful app, crashes constantly, useless!")
        assert result == "negative"


class TestNeutralSentiment:
    """Tests for neutral sentiment detection"""

    def test_neutral_tie(self):
        """Equal positive and negative should return neutral"""
        # One positive (love) and one negative (crash)
        result = analyze_sentiment("I love the idea but it crashes")
        assert result == "neutral"

    def test_empty_string(self):
        """Empty input should return neutral"""
        assert analyze_sentiment("") == "neutral"

    def test_no_sentiment_words(self):
        """Text without sentiment keywords returns neutral"""
        assert analyze_sentiment("The app prints documents") == "neutral"

    def test_okay_keyword(self):
        """Test 'okay' returns neutral (no strong sentiment)"""
        # Note: 'okay' is in neutral keywords but doesn't affect score
        result = analyze_sentiment("It's okay")
        assert result == "neutral"


class TestCaseInsensitivity:
    """Tests for case-insensitive matching"""

    def test_uppercase_love(self):
        """Test uppercase 'LOVE' is detected"""
        assert analyze_sentiment("I LOVE this app") == "positive"

    def test_mixed_case_great(self):
        """Test mixed case 'GrEaT' is detected"""
        assert analyze_sentiment("GrEaT app") == "positive"

    def test_lowercase_terrible(self):
        """Test lowercase 'terrible' is detected"""
        assert analyze_sentiment("terrible experience") == "negative"

    def test_uppercase_terrible(self):
        """Test uppercase 'TERRIBLE' is detected"""
        assert analyze_sentiment("TERRIBLE APP") == "negative"


class TestMultipleOccurrences:
    """Tests for counting multiple occurrences"""

    def test_repeated_great(self):
        """Test repeated positive words count correctly"""
        # 'great' appears 3 times - should strongly be positive
        result = analyze_sentiment("great great great")
        assert result == "positive"

    def test_repeated_terrible(self):
        """Test repeated negative words count correctly"""
        result = analyze_sentiment("terrible terrible terrible")
        assert result == "negative"

    def test_positive_beats_single_negative(self):
        """Multiple different positive words should beat single negative"""
        # Note: The analyzer counts unique keywords, not repetitions of same word
        # Using different positive words to test this
        result = analyze_sentiment("great amazing excellent but one crash")
        assert result == "positive"

    def test_negative_beats_single_positive(self):
        """Multiple different negative words should beat single positive"""
        # Note: The analyzer counts unique keywords, not repetitions of same word
        result = analyze_sentiment("terrible awful crashes constantly but love the idea")
        assert result == "negative"


class TestMixedSentiment:
    """Tests for reviews with both positive and negative keywords"""

    def test_more_positive_wins(self):
        """More positive keywords should result in positive sentiment"""
        text = "Great app, love it, excellent quality, but one small bug"
        result = analyze_sentiment(text)
        assert result == "positive"

    def test_more_negative_wins(self):
        """More negative keywords should result in negative sentiment"""
        text = "Terrible, awful, crashes constantly, but easy to use"
        result = analyze_sentiment(text)
        assert result == "negative"

    def test_equal_counts_neutral(self):
        """Equal positive and negative counts should be neutral"""
        # 2 positive: love, great; 2 negative: crash, fail
        text = "Love the concept, great idea, but crashes and fails often"
        result = analyze_sentiment(text)
        assert result == "neutral"


class TestSubstringMatching:
    """Tests for substring matching behavior (known limitation)"""

    def test_works_in_network(self):
        """'works' substring in 'network' - known issue"""
        # This tests the current behavior (substring matching)
        # 'network' contains 'work' but shouldn't match 'works'
        result = analyze_sentiment("network issues")
        # Currently returns neutral as 'works' is not in 'network'
        assert result == "neutral"

    def test_easy_in_text(self):
        """Test 'easy' is detected"""
        assert analyze_sentiment("easy to use") == "positive"


class TestEdgeCases:
    """Edge case tests"""

    def test_whitespace_only(self):
        """Whitespace only should return neutral"""
        assert analyze_sentiment("   ") == "neutral"

    def test_special_characters(self):
        """Special characters should not affect analysis"""
        assert analyze_sentiment("Love!!! this app!!!") == "positive"

    def test_numbers_only(self):
        """Numbers only should return neutral"""
        assert analyze_sentiment("12345") == "neutral"

    def test_very_long_text(self):
        """Very long text should be handled"""
        long_positive = "great " * 100
        assert analyze_sentiment(long_positive) == "positive"

    def test_unicode_characters(self):
        """Unicode should not break analysis"""
        assert analyze_sentiment("Love this app! ") == "positive"
