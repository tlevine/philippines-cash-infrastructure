#!/usr/bin/env python2
import json

import lxml.html
import requests
import pandas

def download_parse_provinces():
    '''
    Download the list of provinces from
    https://www.phlpost.gov.ph/post-office-location.php

    >>> download_parse_provinces()[:3]
    [u'Agusan Del Norte', u'Agusan Del Sur', u'Basilan']

    Returns a list of strings
    '''
    r = requests.get('https://www.phlpost.gov.ph/post-office-location.php')
    html = lxml.html.fromstring(r.text)
    return map(unicode, html.xpath('//select/descendant::option/@value'))

def download_results(province):
    '''
    >>> download_results(u'Agusan Del Norte').split('\n')[0]
    <h2>Result(s)</h2>
    '''
    r = requests.post(
        'https://www.phlpost.gov.ph/postoffice-province.php',
        data = {u'id': province},
        headers = {u'X-Requested-With': u'XMLHttpRequest'})

    return r.text

def parse_results(province, html_result_string):
    '''
    HTML string -> [dict]

    >>> parse_results(open('Fixture: Agusan Del Norte.html').read()).shape
    '''
    df = pandas.read_html(html_result_string)
    df['province'] = province
    return df

def test():
    print list(sorted(parse_results(open('Fixture: Agusan Del Norte.html').read())[0].items()))
    # import doctest
    # doctest.testmod()

def main():
    import os
    import datetime
    download_dir = os.path.join('data',datetime.date.today().isoformat())
    try:
        os.makedirs(download_dir)
    except OSError:
        pass

    # Download provinces
    provinces = download_parse_provinces()
    json.dump(provinces, open(os.path.join(download_dir, 'provinces.json'), 'w'))

    # Download results
    results = {}
    for province in provinces:
        province_file = os.path.join(download_dir, province.replace('/','|') + u'.html')
        if os.path.exists(province_file):
            results[province] = open(province_file).read()
        else:
            results[province] = download_results(province)
            open(province_file, 'w').write(results[province])

    # Parse results
    dfs = (parse_results(province, html_string) for province, html_string in results)
    big_df = reduce(lambda a,b: a.concat(b), dfs)
    return big_df

if __name__ == '__main__':
    df = main()
