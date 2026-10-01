"""
Test Suite for Micro-Influencer Outreach System.
Validates:
1. Filtering thresholds (followers, engagement rate, category fit)
2. Email sanitization and enrichment
3. Word count compliance for generated pitches (60-90 words email, 15-30 words DM)
4. Duplicate prevention in outreach tracking
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from src.filtering.classifier import InfluencerClassifier
from src.enrichment.enricher import ProfileEnricher
from src.personalization.generator import MessagePersonalizer
from src.sending.tracker import OutreachTracker

@pytest.fixture
def classifier():
    return InfluencerClassifier(target_niche="Fashion & Beauty")

@pytest.fixture
def enricher():
    return ProfileEnricher()

@pytest.fixture
def personalizer():
    return MessagePersonalizer()

@pytest.fixture
def temp_tracker(tmp_path):
    db_file = tmp_path / "test_tracker.db"
    return OutreachTracker(db_path=db_file)

def test_follower_boundary_filtering(classifier):
    # Below floor (< 5,000)
    low_fol = {
        "id": "t1", "name": "Under", "category": "Fashion & Beauty",
        "followers": 3200, "engagement_rate": 3.5, "content_themes": ["Skincare"]
    }
    res_low = classifier.evaluate_candidate(low_fol)
    assert res_low["filter_status"] == "FAILED"
    assert "below micro-influencer floor" in res_low["filter_reason"]

    # Above ceiling (> 100,000)
    high_fol = {
        "id": "t2", "name": "Over", "category": "Fashion & Beauty",
        "followers": 150000, "engagement_rate": 3.5, "content_themes": ["Skincare"]
    }
    res_high = classifier.evaluate_candidate(high_fol)
    assert res_high["filter_status"] == "FAILED"
    assert "exceeds micro-influencer ceiling" in res_high["filter_reason"]

def test_engagement_rate_filtering(classifier):
    low_eng = {
        "id": "t3", "name": "LowEng", "category": "Fashion & Beauty",
        "followers": 25000, "engagement_rate": 1.2, "content_themes": ["Skincare"]
    }
    res = classifier.evaluate_candidate(low_eng)
    assert res["filter_status"] == "FAILED"
    assert "below minimum threshold" in res["filter_reason"]

def test_category_fit_filtering(classifier):
    off_niche = {
        "id": "t4", "name": "Gamer", "category": "Gaming",
        "followers": 25000, "engagement_rate": 4.0, "content_themes": ["Valorant"]
    }
    res = classifier.evaluate_candidate(off_niche)
    assert res["filter_status"] == "FAILED"
    assert "does not match target niche" in res["filter_reason"]

def test_successful_qualification(classifier):
    ideal = {
        "id": "t5", "name": "Good Creator", "category": "Fashion & Beauty",
        "followers": 35000, "engagement_rate": 3.8, "content_themes": ["Clean Beauty", "Hydration"],
        "recent_content": "Best Barrier Creams"
    }
    res = classifier.evaluate_candidate(ideal)
    assert res["filter_status"] == "PASSED"
    assert "[PASSED]" in res["filter_reason"]

def test_email_sanitization(enricher):
    # Missing email
    assert enricher.sanitize_email(None) == "Not Found"
    assert enricher.sanitize_email("") == "Not Found"
    assert enricher.sanitize_email("not found") == "Not Found"
    assert enricher.sanitize_email("random_invalid_text") == "Not Found"

    # Valid email
    assert enricher.sanitize_email("creator@agency.com") == "creator@agency.com"

def test_message_word_counts(personalizer):
    creator = {
        "id": "inf_test",
        "name": "Sarah Jenkins",
        "platform": "Instagram",
        "category": "Fashion & Beauty",
        "content_themes": ["Barrier Repair", "Glass Skin"],
        "recent_content": "5 Drugstore Serums for Sensitive Skin",
        "content_style": "Educational and candid",
        "audience_geography": "United States",
        "audience_age": "20-30",
        "filter_status": "PASSED"
    }
    result = personalizer.personalize_for_influencer(creator)

    email_wc = result["email_word_count"]
    dm_wc = result["dm_word_count"]

    # Strict requirement: Email 60-90 words
    assert 60 <= email_wc <= 90, f"Email word count {email_wc} outside [60, 90]"

    # Strict requirement: DM 15-30 words
    assert 15 <= dm_wc <= 30, f"DM word count {dm_wc} outside [15, 30]"

def test_duplicate_prevention_logic(temp_tracker):
    # Initially not contacted
    assert not temp_tracker.is_already_contacted("test@domain.com", "c_1")

    # Record outreach
    temp_tracker.log_outreach(
        influencer_name="Test Creator",
        influencer_id="c_1",
        email="test@domain.com",
        channel="EMAIL",
        message_content="Sample pitch",
        status="SENT"
    )

    # Now duplicate check should trigger
    assert temp_tracker.is_already_contacted("test@domain.com", "c_1")
    assert temp_tracker.is_already_contacted("OTHER@domain.com", "c_1")  # ID matched
    assert temp_tracker.is_already_contacted("test@domain.com", "other_id")  # Email matched
