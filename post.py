#!/usr/bin/env python2

import lxml.html
import requests

def download_municipalities():
    '''
    Download the list of municipalities from
    https://www.phlpost.gov.ph/post-office-location.php

    >>> download_municipalities()[:3]
    [u'Agusan Del Norte', u'Agusan Del Sur', u'Basilan']

    Returns a list of strings
    '''
    r = requests.get('https://www.phlpost.gov.ph/post-office-location.php')
    html = lxml.html.fromstring(r.text)
    return map(unicode, html.xpath('//select/descendant::option/@value'))

print(download_municipalities())

if __name__ == '__main__':
    import doctest
    doctest.testmod()
