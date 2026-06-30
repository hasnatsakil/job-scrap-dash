class CaptchaDetectedException(Exception):
    """Raised when a CAPTCHA challenge is detected in the scraped page."""
    def __init__(self, source: str, message: str = "CAPTCHA detected"):
        self.source = source
        self.message = f"{message} on {source}"
        super().__init__(self.message)

class CaptchaDetector:
    """Detects CAPTCHA challenges in HTML content."""
    
    # Common strings found in CAPTCHA pages (Cloudflare, generic, etc.)
    INDICATORS = [
        "verify you are human",
        "security check",
        "complete the captcha",
        "cf-browser-verification",
        "cloudflare-nginx",
        "please solve this captcha",
        "checking if the site connection is secure"
    ]

    @classmethod
    def detect_html(cls, html_content: str) -> bool:
        """
        Check the HTML content for known CAPTCHA indicators.
        Returns True if a CAPTCHA is detected, False otherwise.
        """
        if not html_content:
            return False
            
        lower_html = html_content.lower()
        for indicator in cls.INDICATORS:
            if indicator in lower_html:
                return True
                
        return False

captcha_detector = CaptchaDetector()
