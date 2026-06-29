import pytest
from backend.services.normalizer import DataNormalizer
from backend.services.keyword_filter import KeywordFilter
from backend.services.deduplicator import Deduplicator
from backend.config import config_manager, AppConfigCache

def test_clean_html():
    raw = "<p>Hello <b>World</b>!</p>"
    assert DataNormalizer.clean_html(raw) == "Hello World !"

def test_normalize_location():
    assert DataNormalizer.normalize_location("Remote - US") == "Remote"
    assert DataNormalizer.normalize_location("New York, NY") == "New York, NY"

def test_normalize_work_type():
    assert DataNormalizer.normalize_work_type("onsite", "Remote") == "On-site"
    assert DataNormalizer.normalize_work_type("", "Remote") == "Remote"

def test_deduplicator():
    existing = [
        {"Job URL": "http://job1", "Company": "Acme", "Job Title": "Dev"}
    ]
    dedup = Deduplicator(existing)

    assert dedup.is_duplicate({"job_url": "http://job1"}) == True
    assert dedup.is_duplicate({"company": "Acme", "title": "Dev"}) == True
    assert dedup.is_duplicate({"job_url": "http://job2", "company": "Other", "title": "Dev"}) == False

def test_keyword_filter():
    config_manager.update_config(AppConfigCache(search_keywords=["python", "backend"]))
    job1 = {"title": "Python Developer", "description": ""}
    job2 = {"title": "Frontend Eng", "description": "React mostly"}
    job3 = {"title": "Engineer", "description": "Need backend experience"}

    assert KeywordFilter.is_relevant(job1) == True
    assert KeywordFilter.is_relevant(job2) == False
    assert KeywordFilter.is_relevant(job3) == True
