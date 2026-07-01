import pytest
from backend.services.normalizer import DataNormalizer

def test_clean_html():
    raw_html = "<p>Hello <b>World</b>!</p><br>Check this <a href='#'>link</a>."
    cleaned = DataNormalizer.clean_html(raw_html)
    assert cleaned == raw_html # It preserves HTML if tags are present
    
    # Handle None
    assert DataNormalizer.clean_html(None) == ""
    
    # Handle plain text (converts newlines to <br/>)
    assert DataNormalizer.clean_html("Just\ntext") == "Just<br/>text"

def test_normalize_job_employment_type():
    job1 = {"title": "Test", "employment_type": "contract"}
    norm1 = DataNormalizer.normalize_job(job1)
    assert norm1["employment_type"] == "Contract"

    job2 = {"title": "Test", "employment_type": "full-time"}
    norm2 = DataNormalizer.normalize_job(job2)
    assert norm2["employment_type"] == "Full-time"

    job3 = {"title": "Test", "employment_type": "weird-type"}
    norm3 = DataNormalizer.normalize_job(job3)
    assert norm3["employment_type"] == "Weird-Type"

def test_normalize_job_remote():
    job1 = {"title": "Remote Python Dev", "description": "remote work"}
    norm1 = DataNormalizer.normalize_job(job1)
    assert norm1["work_type"] == "Remote"

    job2 = {"title": "Onsite Dev", "location": "Remote, USA"}
    norm2 = DataNormalizer.normalize_job(job2)
    assert norm2["work_type"] == "Remote"

    job3 = {"title": "Local Dev", "location": "New York", "description": "onsite"}
    norm3 = DataNormalizer.normalize_job(job3)
    assert norm3["work_type"] == "On-site"
