"""
General settings for package execution.
"""

## This file is available from https://github.com/adbar/courlan
## under GNU GPL v3 license


# https://www.alexa.com/topsites
# https://www.alexa.com/topsites/countries/DE
# https://www.alexa.com/topsites/countries/US
BLACKLIST = {'360', 'akamai', 'aliexpress', 'amzn', 'amazon', 'amazonaws', 'baidu', 'bit', 'bongacams', 'chaturbate', 'cloudfront', 'daftsex', 'delicious', 'digg', 'ebay', 'ebay-kleinanzeigen', 'facebook', 'feedburner', 'flickr', 'gettyimages', 'gmx', 'google', 'gravatar', 'http', 'imgur', 'immobilienscout24', 'instagr', 'instagram', 'jd', 'last', 'linkedin', 'live', 'livejasmin', 'localhost', 'mail', 'naver', 'netflix', 'office', 'ok', 'onlyfans', 'otto', 'paypal', 'pinterest', 'pornhub', 'postbank', 'qq', 'reddit', 'redtube', 'sina', 'sohu', 'soundcloud', 'spankbang', 'taobao', 'telegram', 'tiktok', 'tmall', 'tnaflix', 'twitch', 'twitter', 'twitpic', 'txxx', 'vk', 'vkontakte', 'vimeo', 'web', 'weibo', 'whatsapp', 'xhamster', 'xnxx', 'xvideos', 'yahoo', 'yandex', 'youjizz', 'youporn', 'youtube', 'youtu', 'zoom'}

ALLOWED_PARAMS = {'aid', 'article_id', 'artnr', 'id', 'itemid', 'objectid', 'p', 'page', 'pagenum', 'page_id', 'pid', 'post', 'postid', 'product_id'}
CONTROL_PARAMS = {'lang', 'language'}
TARGET_LANG_DE = {'de', 'deutsch', 'ger', 'german'}
TARGET_LANG_EN = {'en', 'english', 'eng'} # 'en_US', ''
# accepted_lang = ('en')
