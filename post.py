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

def download_results(municipality):
    '''
    >>> download_municipalities(u'Agusan Del Norte').split('\n')[0]
    <h2>Result(s)</h2>
    '''

def parse_results(html_result_string):
    '''
    HTML string -> [dict]
    '''
    return [{}]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
