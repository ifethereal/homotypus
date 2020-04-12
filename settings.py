#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Homotypus Team'
SITENAME = u'Homotypus'
SITEURL = ''

DEFAULT_CATEGORY = 'Sundry'

# Directory containing site content; needs to be consistent with the makefile
PATH = 'content'

# Theme setup
THEME = 'theme' # Pelicanyan
DIRECT_TEMPLATES = ('index', 'categories', 'authors', 'tags', 'archives',
                    'sitemap', 'robots', 'humans')
STATIC_PATHS = [
    'images',
    '../extra/symbol-defs.svg',
    '../extra/symbols.css',
]
ICONS_SVG_PATH = 'theme/img/symbol-defs.svg'
    # This setting is referenced in Jinja templates

EXTRA_PATH_METADATA = {
    '../extra/symbol-defs.svg': {'path': ICONS_SVG_PATH},
    '../extra/symbols.css': {'path': 'theme/css/symbols.css'},
}

# Locale information
DEFAULT_LANG = u'en'
TIMEZONE = 'Australia/Sydney'
DEFAULT_DATE_FORMAT = '%a, %-d %b %Y'

# Disable feed generation for now
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Layout for pages and posts
ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'posts/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'
PAGE_URL = 'pages/{slug}/'
PAGE_SAVE_AS = 'pages/{slug}/index.html'
YEAR_ARCHIVE_SAVE_AS = 'posts/{date:%Y}/index.html'

# Site directives; these happen to have templates in Pelicanyan
ROBOTS_SAVE_AS = 'robots.txt'
HUMANS_SAVE_AS = 'humans.txt'
SITEMAP_SAVE_AS = 'sitemap.xml'
