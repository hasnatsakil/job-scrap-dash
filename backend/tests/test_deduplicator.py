import pytest
from backend.services.deduplicator import Deduplicator

def test_deduplicator_empty():
    dedup = Deduplicator([])
    job = {"job_url": "http://test.com", "company": "Test", "title": "Dev"}
    assert dedup.is_duplicate(job) == False

def test_deduplicator_by_url():
    existing = [{"job_url": "http://test.com/job123"}]
    dedup = Deduplicator(existing)
    
    # Exact match
    assert dedup.is_duplicate({"job_url": "http://test.com/job123"}) == True
    # Different URL
    assert dedup.is_duplicate({"job_url": "http://test.com/job999"}) == False
    # Missing URL but matching nothing else
    assert dedup.is_duplicate({"company": "Test", "title": "Dev"}) == False

def test_deduplicator_by_signature():
    existing = [{"company": "Tech Corp", "title": "Software Engineer"}]
    dedup = Deduplicator(existing)
    
    # Exact match case-insensitive
    assert dedup.is_duplicate({"company": "tech corp", "title": "SOFTWARE ENGINEER"}) == True
    # Different title
    assert dedup.is_duplicate({"company": "Tech Corp", "title": "Data Scientist"}) == False
    # Different company
    assert dedup.is_duplicate({"company": "Other Corp", "title": "Software Engineer"}) == False

def test_deduplicator_strip_whitespace():
    existing = [{"job_url": "  http://test.com  ", "company": "  Tech  ", "title": " Dev  "}]
    dedup = Deduplicator(existing)
    
    assert dedup.is_duplicate({"job_url": "http://test.com"}) == True
    assert dedup.is_duplicate({"company": "Tech", "title": "Dev"}) == True
