"""
Unit tests for full analysis pipeline
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CustomerInsight_Review_Agent import analyze_reviews, analyze_sentiment, categorize_review


class TestAnalyzeReviewsBasic:
    """Basic tests for analyze_reviews function"""

    def test_returns_dict(self, sample_reviews_list):
        """analyze_reviews returns a dictionary"""
        result = analyze_reviews(sample_reviews_list)
        assert isinstance(result, dict)

    def test_has_total_reviews(self, sample_reviews_list):
        """Result includes total_reviews count"""
        result = analyze_reviews(sample_reviews_list)
        assert "total_reviews" in result
        assert result["total_reviews"] == 10

    def test_has_category_counts(self, sample_reviews_list):
        """Result includes category_counts"""
        result = analyze_reviews(sample_reviews_list)
        assert "category_counts" in result

    def test_has_sentiment_counts(self, sample_reviews_list):
        """Result includes sentiment_counts"""
        result = analyze_reviews(sample_reviews_list)
        assert "sentiment_counts" in result

    def test_has_rating_distribution(self, sample_reviews_list):
        """Result includes rating_distribution"""
        result = analyze_reviews(sample_reviews_list)
        assert "rating_distribution" in result


class TestRatingDistribution:
    """Tests for rating distribution accuracy"""

    def test_counts_correct(self, sample_reviews_list):
        """Rating counts are accurate"""
        result = analyze_reviews(sample_reviews_list)
        ratings = result["rating_distribution"]
        # Count manually from sample_reviews_list
        # 5: 2, 4: 2, 3: 2, 2: 1, 1: 3
        assert ratings[5] == 2
        assert ratings[4] == 2
        assert ratings[3] == 2
        assert ratings[2] == 1
        assert ratings[1] == 3

    def test_all_5_star_reviews(self):
        """All 5-star reviews counted correctly"""
        reviews = [
            {"content": "Great", "rating": 5},
            {"content": "Amazing", "rating": 5},
            {"content": "Perfect", "rating": 5},
        ]
        result = analyze_reviews(reviews)
        assert result["rating_distribution"][5] == 3

    def test_missing_rating_defaults_to_3(self):
        """Missing rating defaults to 3"""
        reviews = [{"content": "Test review"}]  # No rating
        result = analyze_reviews(reviews)
        assert result["rating_distribution"][3] == 1


class TestSentimentCounts:
    """Tests for sentiment counting"""

    def test_sentiment_sum_equals_total(self, sample_reviews_list):
        """Sum of sentiments equals total reviews"""
        result = analyze_reviews(sample_reviews_list)
        sent = result["sentiment_counts"]
        total_sentiment = sent["positive"] + sent["negative"] + sent["neutral"]
        assert total_sentiment == result["total_reviews"]

    def test_positive_reviews_counted(self):
        """Positive reviews are counted correctly"""
        reviews = [
            {"content": "Love this app", "rating": 5},
            {"content": "Amazing and great", "rating": 5},
        ]
        result = analyze_reviews(reviews)
        assert result["sentiment_counts"]["positive"] == 2

    def test_negative_reviews_counted(self):
        """Negative reviews are counted correctly"""
        reviews = [
            {"content": "Terrible app", "rating": 1},
            {"content": "Awful and crashes", "rating": 1},
        ]
        result = analyze_reviews(reviews)
        assert result["sentiment_counts"]["negative"] == 2

    def test_neutral_reviews_counted(self):
        """Neutral reviews are counted correctly"""
        reviews = [
            {"content": "It works", "rating": 3},
            {"content": "Just a test", "rating": 3},
        ]
        result = analyze_reviews(reviews)
        assert result["sentiment_counts"]["neutral"] == 2


class TestCategoryCounts:
    """Tests for category counting"""

    def test_category_counts_exist(self, sample_reviews_list):
        """Category counts are populated"""
        result = analyze_reviews(sample_reviews_list)
        assert len(result["category_counts"]) > 0

    def test_connectivity_counted(self):
        """Connectivity category is counted"""
        reviews = [
            {"content": "WiFi doesn't work", "rating": 1},
            {"content": "Bluetooth issues", "rating": 2},
        ]
        result = analyze_reviews(reviews)
        assert result["category_counts"]["connectivity"] == 2

    def test_printing_counted(self):
        """Printing category is counted"""
        reviews = [
            {"content": "Print quality great", "rating": 5},
            {"content": "Can't print", "rating": 1},
        ]
        result = analyze_reviews(reviews)
        assert result["category_counts"]["printing"] == 2

    def test_multi_category_review_counted(self):
        """Review matching multiple categories counts for each"""
        reviews = [
            {"content": "WiFi setup for printing", "rating": 3},
        ]
        result = analyze_reviews(reviews)
        assert result["category_counts"]["connectivity"] >= 1
        assert result["category_counts"]["printing"] >= 1


class TestEmptyReviews:
    """Tests for handling empty review list"""

    def test_empty_list_returns_zeros(self):
        """Empty review list returns zero counts"""
        result = analyze_reviews([])
        assert result["total_reviews"] == 0
        assert len(result["category_counts"]) == 0

    def test_empty_list_sentiment_counts(self):
        """Empty list has zero sentiment counts"""
        result = analyze_reviews([])
        sent = result["sentiment_counts"]
        assert sent["positive"] == 0
        assert sent["negative"] == 0
        assert sent["neutral"] == 0


class TestMissingFields:
    """Tests for reviews with missing fields"""

    def test_missing_content(self):
        """Review with missing content is handled"""
        reviews = [{"title": "Test", "rating": 5}]
        result = analyze_reviews(reviews)
        assert result["total_reviews"] == 1

    def test_missing_title(self):
        """Review with missing title is handled"""
        reviews = [{"content": "Great app", "rating": 5}]
        result = analyze_reviews(reviews)
        assert result["total_reviews"] == 1

    def test_missing_rating(self):
        """Review with missing rating defaults correctly"""
        reviews = [{"content": "Test review"}]
        result = analyze_reviews(reviews)
        assert 3 in result["rating_distribution"]

    def test_empty_content(self):
        """Review with empty content string is handled"""
        reviews = [{"content": "", "title": "", "rating": 3}]
        result = analyze_reviews(reviews)
        assert result["total_reviews"] == 1

    def test_none_content(self):
        """Review with None content is handled"""
        reviews = [{"content": None, "title": None, "rating": 3}]
        result = analyze_reviews(reviews)
        assert result["total_reviews"] == 1


class TestCategorySentiment:
    """Tests for category-level sentiment tracking"""

    def test_category_sentiment_tracked(self, sample_reviews_list):
        """Category sentiment is tracked"""
        result = analyze_reviews(sample_reviews_list)
        assert "category_sentiment" in result

    def test_category_sentiment_structure(self):
        """Category sentiment has correct structure"""
        reviews = [
            {"content": "Love the WiFi setup", "rating": 5},
            {"content": "WiFi is terrible", "rating": 1},
        ]
        result = analyze_reviews(reviews)
        conn_sent = result["category_sentiment"]["connectivity"]
        assert "positive" in conn_sent
        assert "negative" in conn_sent
        assert "neutral" in conn_sent

    def test_category_positive_sentiment(self):
        """Positive category sentiment is counted"""
        reviews = [{"content": "Love the WiFi", "rating": 5}]
        result = analyze_reviews(reviews)
        assert result["category_sentiment"]["connectivity"]["positive"] == 1

    def test_category_negative_sentiment(self):
        """Negative category sentiment is counted"""
        reviews = [{"content": "WiFi is terrible", "rating": 1}]
        result = analyze_reviews(reviews)
        assert result["category_sentiment"]["connectivity"]["negative"] == 1


class TestCategoryReviews:
    """Tests for sample review storage per category"""

    def test_category_reviews_tracked(self, sample_reviews_list):
        """Category reviews are tracked"""
        result = analyze_reviews(sample_reviews_list)
        assert "category_reviews" in result

    def test_max_5_samples_per_category(self):
        """Maximum 5 review samples per category"""
        reviews = [
            {"content": f"WiFi test review {i}", "rating": 3}
            for i in range(10)
        ]
        result = analyze_reviews(reviews)
        assert len(result["category_reviews"]["connectivity"]) <= 5

    def test_sample_has_required_fields(self):
        """Sample reviews have required fields"""
        reviews = [{"content": "WiFi works great", "title": "Good", "rating": 5}]
        result = analyze_reviews(reviews)
        sample = result["category_reviews"]["connectivity"][0]
        assert "rating" in sample
        assert "title" in sample
        assert "snippet" in sample
        assert "sentiment" in sample


class TestIOSFormatHandling:
    """Tests for iOS format review handling"""

    def test_ios_review_field(self, ios_format_reviews):
        """iOS 'review' field is processed"""
        result = analyze_reviews(ios_format_reviews)
        assert result["total_reviews"] == 2

    def test_ios_content_analyzed(self, ios_format_reviews):
        """iOS review content is analyzed for sentiment"""
        result = analyze_reviews(ios_format_reviews)
        # First review is positive, second is negative
        assert result["sentiment_counts"]["positive"] >= 1
        assert result["sentiment_counts"]["negative"] >= 1


class TestIntegration:
    """Integration tests for full pipeline"""

    def test_full_pipeline_with_sample_data(self, sample_reviews_list):
        """Full analysis pipeline works with sample data"""
        result = analyze_reviews(sample_reviews_list)

        # Verify all expected keys exist
        assert "total_reviews" in result
        assert "category_counts" in result
        assert "category_sentiment" in result
        assert "category_reviews" in result
        assert "sentiment_counts" in result
        assert "rating_distribution" in result

        # Verify counts are consistent
        assert result["total_reviews"] == len(sample_reviews_list)

    def test_pipeline_with_mixed_formats(self):
        """Pipeline handles reviews with different field names"""
        reviews = [
            {"content": "Great app", "rating": 5},  # Standard
            {"review": "Terrible", "rating": 1},     # iOS format
            {"content": "WiFi works", "score": 4},   # Google Play score
        ]
        result = analyze_reviews(reviews)
        assert result["total_reviews"] == 3
