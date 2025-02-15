"""
Functions related to URL manipulation and extraction of URL parts.
"""

import re

from functools import lru_cache
from typing import Any, List, Optional, Set, Tuple, Union
from urllib.parse import urlparse, urlunsplit, ParseResult

from tld import get_tld


DOMAIN_REGEX = re.compile(
    r"(?:http|ftp)s?://"  # protocols
    r"(?:[^/?#]{,63}\.)?"  # subdomain, www, etc.
    r"([^/?#.]{4,63}\.[^/?#]{2,63}|"  # domain and extension
    r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|"  # IPv4
    r"[0-9a-f:]{16,})"  # IPv6
    r"(?:/|$)"  # slash or end of string
)
NO_EXTENSION_REGEX = re.compile(r"(^[^.]+)")
STRIP_DOMAIN_REGEX = re.compile(r"^.+?:.*?@|(?<=[^0-9]):[0-9]+")
CLEAN_FLD_REGEX = re.compile(r"^www[0-9]*\.")
INNER_SLASH_REGEX = re.compile(r"(.+/)+")
FEED_WHITELIST_REGEX = re.compile(r"(feedburner|feedproxy)", re.I)


@lru_cache(maxsize=1024)
def get_tldinfo(
    url: str, fast: bool = False
) -> Union[Tuple[None, None], Tuple[str, str]]:
    """Cached function to extract top-level domain info"""
    if not url or not isinstance(url, str):
        return None, None
    if fast:
        # try with regexes
        domain_match = DOMAIN_REGEX.match(url)
        if domain_match:
            full_domain = STRIP_DOMAIN_REGEX.sub("", domain_match[1])
            clean_match = NO_EXTENSION_REGEX.match(full_domain)
            if clean_match:
                return clean_match[0], full_domain
    # fallback
    tldinfo = get_tld(url, as_object=True, fail_silently=True)
    if tldinfo is None:
        return None, None
    # this step is necessary to standardize output
    return tldinfo.domain, CLEAN_FLD_REGEX.sub("", tldinfo.fld)  # type: ignore[union-attr]


def extract_domain(
    url: str, blacklist: Optional[Set[str]] = None, fast: bool = False
) -> Optional[str]:
    """Extract domain name information using top-level domain info"""
    if blacklist is None:
        blacklist = set()
    # new code: Python >= 3.6 with tld module
    domain, full_domain = get_tldinfo(url, fast=fast)
    # invalid input
    if full_domain is None:
        return None
    # blacklisting
    if domain in blacklist or full_domain in blacklist:
        return None
    # return domain
    return full_domain


def _parse(url: Any) -> ParseResult:
    "Parse a string or use urllib.parse object directly."
    if isinstance(url, str):
        parsed_url = urlparse(url)
    elif isinstance(url, ParseResult):
        parsed_url = url
    else:
        raise TypeError("wrong input type:", type(url))
    return parsed_url


def get_base_url(url: Any) -> str:
    """Strip URL of some of its parts to get base URL.
    Accepts strings and urllib.parse ParseResult objects."""
    parsed_url = _parse(url)
    if parsed_url.scheme:
        scheme = parsed_url.scheme + "://"
    else:
        scheme = ""
    return scheme + parsed_url.netloc


def get_host_and_path(url: Any) -> Tuple[str, str]:
    """Decompose URL in two parts: protocol + host/domain and path.
    Accepts strings and urllib.parse ParseResult objects."""
    parsed_url = _parse(url)
    hostname = get_base_url(parsed_url)
    pathval = urlunsplit(
        ["", "", parsed_url.path, parsed_url.query, parsed_url.fragment]
    )
    # correction for root/homepage
    if pathval == "":
        pathval = "/"
    if not hostname or not pathval:
        raise ValueError(f"incomplete URL: {url}")
    return hostname, pathval


def get_hostinfo(url: str) -> Tuple[Optional[str], str]:
    "Convenience function returning domain and host info (protocol + host/domain) from a URL."
    domainname = extract_domain(url, fast=True)
    base_url = get_base_url(url)
    return domainname, base_url


def fix_relative_urls(baseurl: str, url: str) -> str:
    "Prepend protocol and host information to relative links."
    if url.startswith("//"):
        return "https:" + url if baseurl.startswith("https") else "http:" + url
    if url.startswith("/"):
        # imperfect path handling
        return baseurl + url
    if url.startswith("."):
        # don't try to correct these URLs
        return baseurl + "/" + INNER_SLASH_REGEX.sub("", url)
    if not url.startswith(("http", "{")):
        return baseurl + "/" + url
    # todo: handle here
    # if url.startswith('{'):
    return url


def filter_urls(link_list: List[str], urlfilter: Optional[str]) -> List[str]:
    "Return a list of links corresponding to the given substring pattern."
    if urlfilter is None:
        return sorted(set(link_list))
    # filter links
    filtered_list = [l for l in link_list if urlfilter in l]
    # feedburner option: filter and wildcards for feeds
    if not filtered_list:
        filtered_list = [l for l in link_list if FEED_WHITELIST_REGEX.search(l)]
    return sorted(set(filtered_list))


def is_external(url: str, reference: str, ignore_suffix: bool = True) -> bool:
    """Determine if a link leads to another host, takes a reference URL and
    a URL as input, returns a boolean"""
    stripped_ref, ref = get_tldinfo(reference, fast=True)
    stripped_domain, domain = get_tldinfo(url, fast=True)
    # comparison
    if ignore_suffix:
        return stripped_domain != stripped_ref
    return domain != ref


def is_known_link(link: str, known_links: Set[str]) -> bool:
    "Compare the link and its possible variants to the existing URL base."
    # check exact link
    if link in known_links:
        return True

    # check link and variants with trailing slashes
    test_links = [link.rstrip("/"), link.rstrip("/") + "/"]
    if any(test_link in known_links for test_link in test_links):
        return True

    # check link and variants with modified protocol
    if link.startswith("http"):
        if link.startswith("https"):
            testlink = link[:4] + link[5:]
        else:
            testlink = "".join([link[:4], "s", link[4:]])
        if any(
            test in known_links
            for test in [testlink, testlink.rstrip("/"), testlink.rstrip("/") + "/"]
        ):
            return True

    return False
