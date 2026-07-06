from backend.config import AppConfigCache, config_manager
from backend.services.content_validator import content_validator


def test_ai_keyword_keeps_ai_role(monkeypatch):
    config = AppConfigCache()
    config.relevance_strict_mode = True
    monkeypatch.setattr(config_manager, "get_config", lambda: config)

    jobs = [{
        "title": "AI Engineer",
        "company": "Acme AI",
        "description": "Build LLM and machine learning systems for production.",
    }]

    result = content_validator.validate_batch(jobs, keyword="AI Engineer")
    assert result[0].get("AI Decision") != "Reject"


def test_ai_keyword_rejects_generic_software_role(monkeypatch):
    config = AppConfigCache()
    config.relevance_strict_mode = True
    monkeypatch.setattr(config_manager, "get_config", lambda: config)

    jobs = [{
        "title": "Software Developer",
        "company": "Acme Tech",
        "description": "Build web APIs and CRUD dashboards.",
    }]

    result = content_validator.validate_batch(jobs, keyword="AI Engineer")
    assert result[0].get("AI Decision") == "Reject"
    assert "relevance gate" in result[0].get("AI Reason", "").lower()


def test_ai_keyword_allows_generic_title_with_explicit_ai_specialization(monkeypatch):
    config = AppConfigCache()
    config.relevance_strict_mode = True
    monkeypatch.setattr(config_manager, "get_config", lambda: config)

    jobs = [{
        "title": "Software Engineer, Applied AI",
        "company": "Acme Labs",
        "description": "Build AI copilots and evaluate LLM systems.",
    }]

    result = content_validator.validate_batch(jobs, keyword="AI Engineer")
    assert result[0].get("AI Decision") != "Reject"
