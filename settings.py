#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Homotypus Team'
SITENAME = u'Homotypus'
SITEURL = ''

# Directory containing site content; needs to be consistent with the makefile
PATH = 'content'

# Theme setup
THEME = 'simple'

# Locale information
DEFAULT_LANG = u'en'
TIMEZONE = 'Australia/Sydney'

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
