"""
Unit tests for data loading functionality
"""
import pytest
import json
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CustomerInsight_Review_Agent import load_reviews


class TestLoadJSON:
    """Tests for loading JSON files"""

    def test_load_json_valid(self, temp_json_file):
        """Valid JSON file loads correctly"""
        reviews = load_reviews(temp_json_file)
        assert len(reviews) == 10
        assert reviews[0]["content"] == "Love this app, works perfectly!"

    def test_load_json_structure(self, temp_json_file):
        """JSON structure is preserved"""
        reviews = load_reviews(temp_json_file)
        assert "content" in reviews[0]
        assert "title" in reviews[0]
        assert "rating" in reviews[0]

    def test_load_json_empty(self, temp_empty_json):
        """Empty JSON file returns empty list"""
        reviews = load_reviews(temp_empty_json)
        assert reviews == []

    def test_load_json_single_review(self, tmp_path):
        """Single review JSON loads correctly"""
        filepath = tmp_path / "single.json"
        with open(filepath, "w") as f:
            json.dump([{"content": "Test review", "rating": 5}], f)
        reviews = load_reviews(str(filepath))
        assert len(reviews) == 1


class TestLoadCSV:
    """Tests for loading CSV files"""

    def test_load_csv_valid(self, temp_csv_file):
        """Valid CSV file loads correctly"""
        reviews = load_reviews(temp_csv_file)
        assert len(reviews) == 10

    def test_load_csv_structure(self, temp_csv_file):
        """CSV structure is converted to dict"""
        reviews = load_reviews(temp_csv_file)
        assert "content" in reviews[0]
        assert "title" in reviews[0]
        assert "rating" in reviews[0]

    def test_load_csv_empty(self, temp_empty_csv):
        """Empty CSV file returns empty list"""
        reviews = load_reviews(temp_empty_csv)
        assert reviews == []

    def test_load_csv_with_quotes(self, tmp_path):
        """CSV with quoted content loads correctly"""
        filepath = tmp_path / "quoted.csv"
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["content", "title", "rating"])
            writer.writeheader()
            writer.writerow({
                "content": "This has, commas, inside",
                "title": "Test",
                "rating": 5
            })
        reviews = load_reviews(str(filepath))
        assert reviews[0]["content"] == "This has, commas, inside"


class TestMissingFile:
    """Tests for missing file handling"""

    def test_missing_json_file(self):
        """Missing JSON file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            load_reviews("/nonexistent/path/reviews.json")

    def test_missing_csv_file(self):
        """Missing CSV file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            load_reviews("/nonexistent/path/reviews.csv")


class TestIOSFormat:
    """Tests for iOS App Store review format"""

    def test_ios_format_loads(self, tmp_path, ios_format_reviews):
        """iOS format reviews load correctly"""
        filepath = tmp_path / "ios_reviews.json"
        with open(filepath, "w") as f:
            json.dump(ios_format_reviews, f)
        reviews = load_reviews(str(filepath))
        assert len(reviews) == 2
        # iOS format uses 'review' instead of 'content'
        assert reviews[0]["review"] == "Great app for printing documents!"

    def test_ios_format_has_rating(self, tmp_path, ios_format_reviews):
        """iOS format has rating field"""
        filepath = tmp_path / "ios_reviews.json"
        with open(filepath, "w") as f:
            json.dump(ios_format_reviews, f)
        reviews = load_reviews(str(filepath))
        assert reviews[0]["rating"] == 5

    def test_ios_format_has_title(self, tmp_path, ios_format_reviews):
        """iOS format has title field"""
        filepath = tmp_path / "ios_reviews.json"
        with open(filepath, "w") as f:
            json.dump(ios_format_reviews, f)
        reviews = load_reviews(str(filepath))
        assert reviews[0]["title"] == "Excellent"


class TestGooglePlayFormat:
    """Tests for Google Play review format"""

    def test_googleplay_format_loads(self, tmp_path, googleplay_format_reviews):
        """Google Play format reviews load correctly"""
        filepath = tmp_path / "gplay_reviews.json"
        with open(filepath, "w") as f:
            json.dump(googleplay_format_reviews, f)
        reviews = load_reviews(str(filepath))
        assert len(reviews) == 2
        # Google Play format uses 'content'
        assert reviews[0]["content"] == "WiFi setup was super easy!"

    def test_googleplay_format_score(self, tmp_path, googleplay_format_reviews):
        """Google Play format has score field"""
        filepath = tmp_path / "gplay_reviews.json"
        with open(filepath, "w") as f:
            json.dump(googleplay_format_reviews, f)
        reviews = load_reviews(str(filepath))
        # Score maps to rating concept
        assert reviews[0]["score"] == 5


class TestEncodingHandling:
    """Tests for character encoding"""

    def test_utf8_json(self, tmp_path):
        """UTF-8 encoded JSON loads correctly"""
        filepath = tmp_path / "utf8.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([{"content": "Caf cafe test", "rating": 5}], f)
        reviews = load_reviews(str(filepath))
        assert "" in reviews[0]["content"]

    def test_special_chars_csv(self, tmp_path):
        """Special characters in CSV load correctly"""
        filepath = tmp_path / "special.csv"
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["content", "rating"])
            writer.writeheader()
            writer.writerow({"content": "Test   special", "rating": 5})
        reviews = load_reviews(str(filepath))
        assert "" in reviews[0]["content"]


class TestLargeFiles:
    """Tests for handling larger files"""

    def test_load_100_reviews_json(self, tmp_path):
        """Load 100 reviews from JSON"""
        filepath = tmp_path / "large.json"
        reviews_data = [
            {"content": f"Review {i}", "rating": (i % 5) + 1}
            for i in range(100)
        ]
        with open(filepath, "w") as f:
            json.dump(reviews_data, f)
        reviews = load_reviews(str(filepath))
        assert len(reviews) == 100

    def test_load_100_reviews_csv(self, tmp_path):
        """Load 100 reviews from CSV"""
        filepath = tmp_path / "large.csv"
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["content", "rating"])
            writer.writeheader()
            for i in range(100):
                writer.writerow({"content": f"Review {i}", "rating": (i % 5) + 1})
        reviews = load_reviews(str(filepath))
        assert len(reviews) == 100
