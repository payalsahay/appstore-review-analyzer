"""
Accuracy evaluation tests against golden dataset

These tests measure the accuracy of the sentiment analysis and categorization
against a hand-labeled golden dataset, providing precision/recall metrics.
"""
import pytest
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CustomerInsight_Review_Agent import analyze_sentiment, categorize_review


# Accuracy thresholds
SENTIMENT_ACCURACY_THRESHOLD = 0.70  # 70%
CATEGORY_PRECISION_THRESHOLD = 0.60  # 60%
CATEGORY_RECALL_THRESHOLD = 0.50     # 50%
CATEGORY_F1_THRESHOLD = 0.55         # 55%


def calculate_precision_recall(true_positives, false_positives, false_negatives):
    """Calculate precision and recall"""
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    return precision, recall


def calculate_f1(precision, recall):
    """Calculate F1 score"""
    if precision + recall == 0:
        return 0
    return 2 * (precision * recall) / (precision + recall)


class TestSentimentAccuracy:
    """Evaluate sentiment classification accuracy against golden dataset"""

    def test_sentiment_accuracy(self, golden_dataset):
        """Measure overall sentiment classification accuracy"""
        correct = 0
        total = len(golden_dataset)

        results_by_class = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

        for review in golden_dataset:
            full_text = f"{review.get('title', '')} {review['content']}"
            predicted = analyze_sentiment(full_text)
            expected = review["expected_sentiment"]

            if predicted == expected:
                correct += 1
                results_by_class[expected]["tp"] += 1
            else:
                results_by_class[predicted]["fp"] += 1
                results_by_class[expected]["fn"] += 1

        accuracy = correct / total

        # Report results
        print(f"\n{'='*60}")
        print("SENTIMENT ACCURACY REPORT")
        print(f"{'='*60}")
        print(f"Overall Accuracy: {accuracy:.1%} ({correct}/{total})")
        print(f"Threshold: {SENTIMENT_ACCURACY_THRESHOLD:.1%}")
        print(f"Status: {'PASS' if accuracy >= SENTIMENT_ACCURACY_THRESHOLD else 'FAIL'}")
        print(f"\nPer-class metrics:")

        for sentiment_class in ["positive", "negative", "neutral"]:
            metrics = results_by_class[sentiment_class]
            precision, recall = calculate_precision_recall(
                metrics["tp"], metrics["fp"], metrics["fn"]
            )
            f1 = calculate_f1(precision, recall)
            print(f"  {sentiment_class:10s}: P={precision:.2f} R={recall:.2f} F1={f1:.2f}")

        print(f"{'='*60}\n")

        assert accuracy >= SENTIMENT_ACCURACY_THRESHOLD, \
            f"Sentiment accuracy {accuracy:.1%} below threshold {SENTIMENT_ACCURACY_THRESHOLD:.1%}"

    def test_positive_sentiment_detection(self, golden_dataset):
        """Test positive sentiment detection rate"""
        positive_reviews = [r for r in golden_dataset if r["expected_sentiment"] == "positive"]
        correct = 0

        for review in positive_reviews:
            full_text = f"{review.get('title', '')} {review['content']}"
            if analyze_sentiment(full_text) == "positive":
                correct += 1

        recall = correct / len(positive_reviews) if positive_reviews else 0
        print(f"\nPositive sentiment recall: {recall:.1%} ({correct}/{len(positive_reviews)})")

        # We expect at least 60% of positive reviews to be detected
        assert recall >= 0.60, f"Positive recall {recall:.1%} too low"

    def test_negative_sentiment_detection(self, golden_dataset):
        """Test negative sentiment detection rate"""
        negative_reviews = [r for r in golden_dataset if r["expected_sentiment"] == "negative"]
        correct = 0

        for review in negative_reviews:
            full_text = f"{review.get('title', '')} {review['content']}"
            if analyze_sentiment(full_text) == "negative":
                correct += 1

        recall = correct / len(negative_reviews) if negative_reviews else 0
        print(f"\nNegative sentiment recall: {recall:.1%} ({correct}/{len(negative_reviews)})")

        # We expect at least 70% of negative reviews to be detected
        assert recall >= 0.70, f"Negative recall {recall:.1%} too low"


class TestCategorizationAccuracy:
    """Evaluate category classification accuracy against golden dataset"""

    def test_categorization_accuracy(self, golden_dataset):
        """Measure category classification precision and recall"""
        # Track metrics per category
        category_metrics = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

        for review in golden_dataset:
            full_text = f"{review.get('title', '')} {review['content']}"
            predicted = set(categorize_review(full_text))
            expected = set(review["expected_categories"])

            # True positives: in both predicted and expected
            for cat in predicted & expected:
                category_metrics[cat]["tp"] += 1

            # False positives: in predicted but not expected
            for cat in predicted - expected:
                category_metrics[cat]["fp"] += 1

            # False negatives: in expected but not predicted
            for cat in expected - predicted:
                category_metrics[cat]["fn"] += 1

        # Calculate overall metrics
        total_tp = sum(m["tp"] for m in category_metrics.values())
        total_fp = sum(m["fp"] for m in category_metrics.values())
        total_fn = sum(m["fn"] for m in category_metrics.values())

        overall_precision, overall_recall = calculate_precision_recall(total_tp, total_fp, total_fn)
        overall_f1 = calculate_f1(overall_precision, overall_recall)

        # Report results
        print(f"\n{'='*60}")
        print("CATEGORIZATION ACCURACY REPORT")
        print(f"{'='*60}")
        print(f"Overall Precision: {overall_precision:.1%}")
        print(f"Overall Recall: {overall_recall:.1%}")
        print(f"Overall F1: {overall_f1:.2f}")
        print(f"\nThresholds: P>={CATEGORY_PRECISION_THRESHOLD:.1%}, R>={CATEGORY_RECALL_THRESHOLD:.1%}")
        print(f"\nPer-category metrics:")

        for cat in sorted(category_metrics.keys()):
            metrics = category_metrics[cat]
            precision, recall = calculate_precision_recall(
                metrics["tp"], metrics["fp"], metrics["fn"]
            )
            f1 = calculate_f1(precision, recall)
            print(f"  {cat:20s}: P={precision:.2f} R={recall:.2f} F1={f1:.2f} "
                  f"(TP={metrics['tp']}, FP={metrics['fp']}, FN={metrics['fn']})")

        print(f"{'='*60}\n")

        assert overall_precision >= CATEGORY_PRECISION_THRESHOLD, \
            f"Category precision {overall_precision:.1%} below threshold {CATEGORY_PRECISION_THRESHOLD:.1%}"
        assert overall_recall >= CATEGORY_RECALL_THRESHOLD, \
            f"Category recall {overall_recall:.1%} below threshold {CATEGORY_RECALL_THRESHOLD:.1%}"

    def test_category_f1_score(self, golden_dataset):
        """Test overall category F1 score meets threshold"""
        category_metrics = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

        for review in golden_dataset:
            full_text = f"{review.get('title', '')} {review['content']}"
            predicted = set(categorize_review(full_text))
            expected = set(review["expected_categories"])

            for cat in predicted & expected:
                category_metrics[cat]["tp"] += 1
            for cat in predicted - expected:
                category_metrics[cat]["fp"] += 1
            for cat in expected - predicted:
                category_metrics[cat]["fn"] += 1

        total_tp = sum(m["tp"] for m in category_metrics.values())
        total_fp = sum(m["fp"] for m in category_metrics.values())
        total_fn = sum(m["fn"] for m in category_metrics.values())

        precision, recall = calculate_precision_recall(total_tp, total_fp, total_fn)
        f1 = calculate_f1(precision, recall)

        assert f1 >= CATEGORY_F1_THRESHOLD, \
            f"Category F1 score {f1:.2f} below threshold {CATEGORY_F1_THRESHOLD}"

    def test_multi_category_detection(self, golden_dataset):
        """Test detection of reviews with multiple categories"""
        multi_cat_reviews = [r for r in golden_dataset if len(r["expected_categories"]) > 1]

        partial_match = 0
        full_match = 0

        for review in multi_cat_reviews:
            full_text = f"{review.get('title', '')} {review['content']}"
            predicted = set(categorize_review(full_text))
            expected = set(review["expected_categories"])

            # Check for at least partial overlap
            if predicted & expected:
                partial_match += 1

            # Check for full match (all expected categories detected)
            if expected <= predicted:
                full_match += 1

        partial_rate = partial_match / len(multi_cat_reviews) if multi_cat_reviews else 0
        full_rate = full_match / len(multi_cat_reviews) if multi_cat_reviews else 0

        print(f"\nMulti-category detection:")
        print(f"  Partial match rate: {partial_rate:.1%}")
        print(f"  Full match rate: {full_rate:.1%}")

        # We expect at least 70% partial match for multi-category reviews
        assert partial_rate >= 0.70, f"Multi-category partial match {partial_rate:.1%} too low"


class TestEdgeCaseAccuracy:
    """Test accuracy on known edge cases"""

    def test_negation_handling(self, golden_dataset):
        """Evaluate performance on negation cases"""
        negation_reviews = [r for r in golden_dataset if "negation" in r.get("notes", "").lower()]

        if not negation_reviews:
            pytest.skip("No negation test cases in golden dataset")

        for review in negation_reviews:
            full_text = f"{review.get('title', '')} {review['content']}"
            predicted = analyze_sentiment(full_text)
            expected = review["expected_sentiment"]

            # Log the case for analysis
            print(f"\nNegation case: '{full_text[:50]}...'")
            print(f"  Expected: {expected}, Predicted: {predicted}")

        # Note: We don't assert here because negation is a known limitation
        # This test is for visibility into the behavior

    def test_sarcasm_handling(self, golden_dataset):
        """Evaluate performance on sarcasm cases"""
        sarcasm_reviews = [r for r in golden_dataset if "sarcasm" in r.get("notes", "").lower()]

        if not sarcasm_reviews:
            pytest.skip("No sarcasm test cases in golden dataset")

        correct = 0
        for review in sarcasm_reviews:
            full_text = f"{review.get('title', '')} {review['content']}"
            predicted = analyze_sentiment(full_text)
            expected = review["expected_sentiment"]

            if predicted == expected:
                correct += 1

            print(f"\nSarcasm case: '{full_text[:50]}...'")
            print(f"  Expected: {expected}, Predicted: {predicted}")

        # Note: Sarcasm is very difficult for keyword-based approaches
        # This test is mainly for visibility

    def test_mixed_sentiment_handling(self, golden_dataset):
        """Evaluate performance on mixed sentiment cases"""
        mixed_reviews = [r for r in golden_dataset if "mixed" in r.get("notes", "").lower()]

        if not mixed_reviews:
            pytest.skip("No mixed sentiment test cases in golden dataset")

        for review in mixed_reviews:
            full_text = f"{review.get('title', '')} {review['content']}"
            predicted = analyze_sentiment(full_text)
            expected = review["expected_sentiment"]

            print(f"\nMixed sentiment case: '{full_text[:50]}...'")
            print(f"  Expected: {expected}, Predicted: {predicted}")


class TestAccuracyReporting:
    """Generate comprehensive accuracy reports"""

    def test_generate_full_report(self, golden_dataset):
        """Generate a full accuracy report for all test cases"""
        print(f"\n{'='*70}")
        print("FULL ACCURACY EVALUATION REPORT")
        print(f"{'='*70}")
        print(f"Total test cases: {len(golden_dataset)}")

        sentiment_correct = 0
        category_tp = 0
        category_total_predicted = 0
        category_total_expected = 0

        detailed_results = []

        for review in golden_dataset:
            full_text = f"{review.get('title', '')} {review['content']}"

            # Sentiment
            predicted_sentiment = analyze_sentiment(full_text)
            expected_sentiment = review["expected_sentiment"]
            sentiment_match = predicted_sentiment == expected_sentiment
            if sentiment_match:
                sentiment_correct += 1

            # Categories
            predicted_cats = set(categorize_review(full_text))
            expected_cats = set(review["expected_categories"])

            cat_tp = len(predicted_cats & expected_cats)
            category_tp += cat_tp
            category_total_predicted += len(predicted_cats)
            category_total_expected += len(expected_cats)

            detailed_results.append({
                "id": review["id"],
                "sentiment_match": sentiment_match,
                "predicted_sentiment": predicted_sentiment,
                "expected_sentiment": expected_sentiment,
                "predicted_categories": predicted_cats,
                "expected_categories": expected_cats,
                "category_overlap": cat_tp
            })

        # Summary
        sentiment_accuracy = sentiment_correct / len(golden_dataset)
        category_precision = category_tp / category_total_predicted if category_total_predicted > 0 else 0
        category_recall = category_tp / category_total_expected if category_total_expected > 0 else 0

        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        print(f"Sentiment Accuracy: {sentiment_accuracy:.1%} ({sentiment_correct}/{len(golden_dataset)})")
        print(f"Category Precision: {category_precision:.1%}")
        print(f"Category Recall: {category_recall:.1%}")

        # Show misclassified cases
        print(f"\n{'='*70}")
        print("MISCLASSIFIED CASES")
        print(f"{'='*70}")

        misclassified = [r for r in detailed_results if not r["sentiment_match"]]
        for result in misclassified[:10]:  # Show first 10
            print(f"\n{result['id']}:")
            print(f"  Expected: {result['expected_sentiment']}, Got: {result['predicted_sentiment']}")

        print(f"\n{'='*70}\n")

        # This test always passes - it's for reporting only
        assert True
