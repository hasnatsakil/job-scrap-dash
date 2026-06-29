import pytest
from unittest.mock import AsyncMock, patch
from backend.scrapers.base import JobResult
from backend.scrapers.duckduckgo_html import LeverScraper
from backend.scrapers.linkedin import LinkedInScraper

def test_job_result():
    job = JobResult(title="Test", company="Corp", location="Remote", job_url="http://x")
    data = job.to_dict()
    assert data["title"] == "Test"
    assert "scraped_date" in data

@pytest.mark.asyncio
async def test_lever_scraper_html_parsing():
    scraper = LeverScraper()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_context.new_page.return_value = mock_page

    html_content = """
    <div class="result__body">
        <h2 class="result__title"><a class="result__a" href="https://jobs.lever.co/test">Python Developer</a></h2>
        <div class="result__snippet">Great python job here</div>
    </div>
    """
    mock_page.content.return_value = html_content

    jobs = await scraper.scrape(mock_context, "python")
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Python Developer"
    assert jobs[0]["job_url"] == "https://jobs.lever.co/test"

@pytest.mark.asyncio
async def test_linkedin_scraper_public():
    with patch('backend.scrapers.linkedin.env_settings') as mock_env:
        mock_env.linkedin_li_at_cookie = None
        scraper = LinkedInScraper()

        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_context.new_page.return_value = mock_page

        html_content = """
        <div class="job-search-card">
            <h3 class="base-search-card__title">Data Engineer</h3>
            <h4 class="base-search-card__subtitle">Tech Inc</h4>
            <span class="job-search-card__location">New York</span>
            <a class="base-card__full-link" href="https://linkedin.com/jobs/view/123?trk=public"></a>
        </div>
        """
        mock_page.content.return_value = html_content

        jobs = await scraper.scrape(mock_context, "data")
        assert len(jobs) == 1
        assert jobs[0]["title"] == "Data Engineer"
        assert jobs[0]["company"] == "Tech Inc"
        assert jobs[0]["job_url"] == "https://linkedin.com/jobs/view/123"
