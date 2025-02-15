"""
Utilities dedicated to URL sampling
"""


import logging

# from functools import cmp_to_key
from random import sample
from typing import List, Optional

from .urlstore import UrlStore

LOGGER = logging.getLogger(__name__)


def sample_urls(
    input_urls: List[str],
    samplesize: int,
    exclude_min: Optional[int] = None,
    exclude_max: Optional[int] = None,
    strict: bool = False,
    verbose: bool = False,
) -> List[str]:
    """Sample a list of URLs by domain name, optionally using constraints on their number"""
    # logging
    if verbose:
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.ERROR)
    # store
    output_urls = []
    use_compression = len(input_urls) > 10**6
    urlstore = UrlStore(
        compressed=use_compression, language=None, strict=strict, verbose=verbose
    )
    urlstore.add_urls(sorted(input_urls))
    # iterate
    for domain in urlstore.urldict:  # key=cmp_to_key(locale.strcoll)
        urlpaths = [
            p.urlpath
            for p in urlstore._load_urls(domain)
            if p.urlpath not in ("/", None)
        ]
        # too few or too many URLs
        if (
            not urlpaths
            or exclude_min is not None
            and len(urlpaths) < exclude_min
            or exclude_max is not None
            and len(urlpaths) > exclude_max
        ):
            LOGGER.warning("discarded (size): %s\t\turls: %s", domain, len(urlpaths))
            continue
        # sample
        if len(urlpaths) > samplesize:
            mysample = sorted(sample(urlpaths, k=samplesize))
        else:
            mysample = urlpaths
        output_urls.extend([domain + p for p in mysample])
        LOGGER.debug(
            "%s\t\turls: %s\tprop.: %s",
            domain,
            len(mysample),
            len(mysample) / len(urlpaths),
        )
    # return gathered URLs
    return output_urls
