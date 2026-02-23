"""
Unit tests for review categorization functionality
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CustomerInsight_Review_Agent import categorize_review, INSIGHT_CATEGORIES


class TestConnectivityCategory:
    """Tests for connectivity category detection"""

    def test_wifi_keyword(self):
        """Test 'wifi' triggers connectivity category"""
        result = categorize_review("Can't connect to wifi")
        assert "connectivity" in result

    def test_bluetooth_keyword(self):
        """Test 'bluetooth' triggers connectivity category"""
        result = categorize_review("Bluetooth pairing failed")
        assert "connectivity" in result

    def test_network_keyword(self):
        """Test 'network' triggers connectivity category"""
        result = categorize_review("Network connection issues")
        assert "connectivity" in result

    def test_setup_keyword(self):
        """Test 'setup' triggers connectivity category"""
        result = categorize_review("Setup was easy")
        assert "connectivity" in result

    def test_wireless_keyword(self):
        """Test 'wireless' triggers connectivity category"""
        result = categorize_review("Wireless printing works")
        assert "connectivity" in result


class TestPrintingCategory:
    """Tests for printing category detection"""

    def test_print_keyword(self):
        """Test 'print' triggers printing category"""
        result = categorize_review("Can't print anything")
        assert "printing" in result

    def test_quality_keyword(self):
        """Test 'quality' triggers printing category"""
        result = categorize_review("Print quality is excellent")
        assert "printing" in result

    def test_ink_keyword(self):
        """Test 'ink' triggers printing category"""
        result = categorize_review("Low ink warning")
        assert "printing" in result

    def test_paper_keyword(self):
        """Test 'paper' triggers printing category"""
        result = categorize_review("Paper jam issues")
        assert "printing" in result

    def test_photo_keyword(self):
        """Test 'photo' triggers printing category"""
        result = categorize_review("Photo printing is great")
        assert "printing" in result


class TestScanningCategory:
    """Tests for scanning category detection"""

    def test_scan_keyword(self):
        """Test 'scan' triggers scanning category"""
        result = categorize_review("Scan feature doesn't work")
        assert "scanning" in result

    def test_scanner_keyword(self):
        """Test 'scanner' triggers scanning category"""
        result = categorize_review("Scanner is slow")
        assert "scanning" in result

    def test_ocr_keyword(self):
        """Test 'ocr' triggers scanning category"""
        result = categorize_review("OCR doesn't recognize text")
        assert "scanning" in result


class TestMobileExperienceCategory:
    """Tests for mobile experience category detection"""

    def test_app_keyword(self):
        """Test 'app' triggers mobile_experience category"""
        result = categorize_review("This app is confusing")
        assert "mobile_experience" in result

    def test_interface_keyword(self):
        """Test 'interface' triggers mobile_experience category"""
        result = categorize_review("User interface is clean")
        assert "mobile_experience" in result

    def test_easy_keyword(self):
        """Test 'easy' triggers mobile_experience category"""
        result = categorize_review("Easy to navigate")
        assert "mobile_experience" in result

    def test_confusing_keyword(self):
        """Test 'confusing' triggers mobile_experience category"""
        result = categorize_review("Very confusing layout")
        assert "mobile_experience" in result


class TestReliabilityCategory:
    """Tests for reliability category detection"""

    def test_crash_keyword(self):
        """Test 'crash' triggers reliability category"""
        result = categorize_review("App crashes constantly")
        assert "reliability" in result

    def test_bug_keyword(self):
        """Test 'bug' triggers reliability category"""
        result = categorize_review("Too many bugs")
        assert "reliability" in result

    def test_freeze_keyword(self):
        """Test 'freeze' triggers reliability category"""
        result = categorize_review("App freezes")
        assert "reliability" in result

    def test_error_keyword(self):
        """Test 'error' triggers reliability category"""
        result = categorize_review("Getting error messages")
        assert "reliability" in result


class TestUpdatesCategory:
    """Tests for updates category detection"""

    def test_update_keyword(self):
        """Test 'update' triggers updates category"""
        result = categorize_review("After the update everything broke")
        assert "updates" in result

    def test_ios_keyword(self):
        """Test 'ios' triggers updates category"""
        result = categorize_review("Not working on iOS 17")
        assert "updates" in result

    def test_version_keyword(self):
        """Test 'version' triggers updates category"""
        result = categorize_review("Old version was better")
        assert "updates" in result


class TestFeaturesCategory:
    """Tests for features category detection"""

    def test_feature_keyword(self):
        """Test 'feature' triggers features category"""
        result = categorize_review("Need more features")
        assert "features" in result

    def test_wish_keyword(self):
        """Test 'wish' triggers features category"""
        result = categorize_review("I wish it could do more")
        assert "features" in result

    def test_missing_keyword(self):
        """Test 'missing' triggers features category"""
        result = categorize_review("Missing functionality")
        assert "features" in result


class TestAccountCloudCategory:
    """Tests for account/cloud category detection"""

    def test_login_keyword(self):
        """Test 'login' triggers account_cloud category"""
        result = categorize_review("Can't login to my account")
        assert "account_cloud" in result

    def test_cloud_keyword(self):
        """Test 'cloud' triggers account_cloud category"""
        result = categorize_review("Cloud storage works well")
        assert "account_cloud" in result

    def test_account_keyword(self):
        """Test 'account' triggers account_cloud category"""
        result = categorize_review("Account verification failed")
        assert "account_cloud" in result


class TestSupportCategory:
    """Tests for support category detection"""

    def test_support_keyword(self):
        """Test 'support' triggers support category"""
        result = categorize_review("Customer support is terrible")
        assert "support" in result

    def test_help_keyword(self):
        """Test 'help' triggers support category"""
        result = categorize_review("Help section is useful")
        assert "support" in result


class TestValueCategory:
    """Tests for value category detection"""

    def test_free_keyword(self):
        """Test 'free' triggers value category"""
        result = categorize_review("Great free app")
        assert "value" in result

    def test_subscription_keyword(self):
        """Test 'subscription' triggers value category"""
        result = categorize_review("Subscription is too expensive")
        assert "value" in result

    def test_worth_keyword(self):
        """Test 'worth' triggers value category"""
        result = categorize_review("Not worth the money")
        assert "value" in result


class TestMultipleCategories:
    """Tests for reviews matching multiple categories"""

    def test_connectivity_and_printing(self):
        """Test review matching both connectivity and printing"""
        result = categorize_review("WiFi setup for printing is hard")
        assert "connectivity" in result
        assert "printing" in result

    def test_three_categories(self):
        """Test review matching three categories"""
        result = categorize_review("WiFi setup is easy and printing quality is great with no crashes")
        assert "connectivity" in result
        assert "printing" in result
        assert "reliability" in result

    def test_scanning_and_mobile(self):
        """Test review matching scanning and mobile experience"""
        result = categorize_review("The app scan feature is confusing")
        assert "scanning" in result
        assert "mobile_experience" in result


class TestUncategorized:
    """Tests for uncategorized reviews"""

    def test_no_keywords_uncategorized(self):
        """Review with no keywords returns uncategorized"""
        result = categorize_review("This is just a test")
        assert result == ["uncategorized"]

    def test_empty_string_uncategorized(self):
        """Empty string returns uncategorized"""
        result = categorize_review("")
        assert result == ["uncategorized"]

    def test_generic_text_uncategorized(self):
        """Generic text without category keywords"""
        result = categorize_review("I use this every day")
        assert result == ["uncategorized"]


class TestCaseInsensitiveCategories:
    """Tests for case-insensitive category matching"""

    def test_uppercase_wifi(self):
        """Test uppercase 'WIFI' matches connectivity"""
        result = categorize_review("WIFI is broken")
        assert "connectivity" in result

    def test_mixed_case_bluetooth(self):
        """Test mixed case 'BlueTooth' matches"""
        result = categorize_review("BlueTooth pairing")
        assert "connectivity" in result

    def test_uppercase_crash(self):
        """Test uppercase 'CRASH' matches reliability"""
        result = categorize_review("APP CRASH CONSTANTLY")
        assert "reliability" in result


class TestAllCategoriesDetectable:
    """Verify each category can be detected"""

    @pytest.mark.parametrize("category,sample_text", [
        ("connectivity", "wifi connection problems"),
        ("printing", "print quality issues"),
        ("scanning", "scanner not working"),
        ("mobile_experience", "app interface confusing"),
        ("reliability", "crashes all the time"),
        ("updates", "after update broken"),
        ("features", "wish for new features"),
        ("account_cloud", "login to cloud storage"),
        ("support", "customer support help"),
        ("value", "free subscription worth"),
    ])
    def test_category_detectable(self, category, sample_text):
        """Each category should be detectable with its keywords"""
        result = categorize_review(sample_text)
        assert category in result
