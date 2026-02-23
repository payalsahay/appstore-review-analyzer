"""
Pytest fixtures for CustomerInsight_Review_Agent tests
"""
import json
import os
import pytest
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CustomerInsight_Review_Agent import (
    analyze_sentiment,
    categorize_review,
    analyze_reviews,
    load_reviews,
    SENTIMENT_KEYWORDS,
    INSIGHT_CATEGORIES,
)


@pytest.fixture
def sample_positive_review():
    """A clearly positive review"""
    return {
        "content": "This app is amazing and works great! Love how easy it is to use.",
        "title": "Perfect app",
        "rating": 5
    }


@pytest.fixture
def sample_negative_review():
    """A clearly negative review"""
    return {
        "content": "Terrible app, crashes constantly and is completely useless. Waste of time.",
        "title": "Awful experience",
        "rating": 1
    }


@pytest.fixture
def sample_neutral_review():
    """A neutral review"""
    return {
        "content": "The app is okay, does what it needs to do.",
        "title": "Average",
        "rating": 3
    }


@pytest.fixture
def sample_connectivity_review():
    """A review about connectivity issues"""
    return {
        "content": "Can't connect to WiFi, the bluetooth pairing never works and printer goes offline.",
        "title": "Connection problems",
        "rating": 2
    }


@pytest.fixture
def sample_printing_review():
    """A review about printing functionality"""
    return {
        "content": "Print quality is excellent, colors are vibrant and pages come out perfect.",
        "title": "Great printing",
        "rating": 5
    }


@pytest.fixture
def sample_multi_category_review():
    """A review touching multiple categories"""
    return {
        "content": "WiFi setup was easy but the app crashes when I try to scan. Print quality is good though.",
        "title": "Mixed experience",
        "rating": 3
    }


@pytest.fixture
def sample_reviews_list():
    """A list of sample reviews for integration testing"""
    return [
        {"content": "Love this app, works perfectly!", "title": "Great", "rating": 5},
        {"content": "Terrible, crashes all the time", "title": "Bad", "rating": 1},
        {"content": "App is okay, basic functionality works", "title": "OK", "rating": 3},
        {"content": "WiFi connection is unreliable", "title": "Connection issues", "rating": 2},
        {"content": "Print quality is amazing", "title": "Excellent prints", "rating": 5},
        {"content": "Scanning feature doesn't work", "title": "Scanner broken", "rating": 1},
        {"content": "Easy to use interface", "title": "Good UI", "rating": 4},
        {"content": "After update app won't start", "title": "Update broke it", "rating": 1},
        {"content": "Need more features please", "title": "Feature request", "rating": 3},
        {"content": "Cloud sync works well", "title": "Good cloud", "rating": 4},
    ]


@pytest.fixture
def golden_dataset():
    """Load the golden dataset for accuracy testing"""
    golden_path = os.path.join(os.path.dirname(__file__), "golden_dataset.json")
    with open(golden_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def temp_json_file(tmp_path, sample_reviews_list):
    """Create a temporary JSON file with sample reviews"""
    filepath = tmp_path / "test_reviews.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(sample_reviews_list, f)
    return str(filepath)


@pytest.fixture
def temp_csv_file(tmp_path, sample_reviews_list):
    """Create a temporary CSV file with sample reviews"""
    import csv
    filepath = tmp_path / "test_reviews.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["content", "title", "rating"])
        writer.writeheader()
        writer.writerows(sample_reviews_list)
    return str(filepath)


@pytest.fixture
def temp_empty_json(tmp_path):
    """Create an empty JSON file"""
    filepath = tmp_path / "empty.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump([], f)
    return str(filepath)


@pytest.fixture
def temp_empty_csv(tmp_path):
    """Create an empty CSV file"""
    import csv
    filepath = tmp_path / "empty.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["content", "title", "rating"])
        writer.writeheader()
    return str(filepath)


@pytest.fixture
def ios_format_reviews():
    """iOS App Store review format"""
    return [
        {
            "id": "12345",
            "userName": "User1",
            "review": "Great app for printing documents!",
            "title": "Excellent",
            "rating": 5,
            "date": "2024-01-15"
        },
        {
            "id": "12346",
            "userName": "User2",
            "review": "Terrible app, crashes constantly",
            "title": "Awful",
            "rating": 1,
            "date": "2024-01-16"
        }
    ]


@pytest.fixture
def googleplay_format_reviews():
    """Google Play review format"""
    return [
        {
            "reviewId": "abc123",
            "userName": "User1",
            "content": "WiFi setup was super easy!",
            "score": 5,
            "at": "2024-01-15"
        },
        {
            "reviewId": "abc124",
            "userName": "User2",
            "content": "App keeps freezing",
            "score": 2,
            "at": "2024-01-16"
        }
    ]
