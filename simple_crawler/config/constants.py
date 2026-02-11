"""Configuration constants for Doxygen crawler."""

# Doxygen common pages to check
DOXYGEN_SEED_PAGES = [
    'index.html',
    'modules.html',
    'namespaces.html',
    'classes.html',
    'files.html',
    'annotated.html',
    'functions.html',
    'globals.html',
    'pages.html',
]

# User agent for requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Default output directory
DEFAULT_OUTPUT_DIR = 'doxygen_crawl'

# Default crawling parameters
DEFAULT_MAX_PAGES = 500
DEFAULT_DELAY = 1.0
