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

def download_results(province, session = None):
    '''
    Mimic this Javascript

        $(".province").change(function(){
          var id=$(this).val();
          var dataString = 'id='+ id;
          $.ajax ({
            type: "POST",
            url: "postoffice-municipality.php",
            data: dataString,
            cache: false,
            success: function(html) { $("#result").html(html); }
          });
        });

    Note the lack of url-encoding.

    >>> len(lxml.html.parse(download_results(u'Agusan Del Norte')).xpath('//tr'))
    7
    '''
    if session == None:
        session = requests.session()
        session.get('https://www.phlpost.gov.ph/post-office-location.php')

    headers = {
        u'Accept-Encoding': u'gzip,deflate,sdch',
        u'Accept-Language': u'en-US,en;q=0.8,fr;q=0.6,sv;q=0.4,zh;q=0.2,zh-CN;q=0.2,zh-TW;q=0.2',
        u'Host': u'www.phlpost.gov.ph',
        u'Origin': u'https://www.phlpost.gov.ph',
        u'Referer': u'https://www.phlpost.gov.ph/post-office-location.php',
        u'User-Agent': u'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.76 Safari/537.36',
        u'X-Requested-With': u'XMLHttpRequest',
    }

    r = session.post(
        'https://www.phlpost.gov.ph/postoffice-province.php',
        data = u'id=' + province, headers = headers)

    print r.request.headers
    print r.request.body

    return r #.text

def parse_results(province, html_result_string):
    '''
    HTML string -> [dict]

    >>> parse_results(u'Agusan Del Norte', open('Fixture: Agusan Del Norte.html').read().decode('utf-8')).shape
    (6, 5)

    >>> parse_results(u'Agusan Del Norte', open('Fixture: Agusan Del Norte.html').read().decode('utf-8')).columns
    Index([u'Post Office Name', u'Municipality', u'Address', u'Zip Code', u'Province'], dtype=object)

    >>> list(parse_results(u'Agusan Del Norte', open('Fixture: Agusan Del Norte.html').read().decode('utf-8')).ix[4])
    [u'Fr. S. Urios University', u'Butuan City', u'Butuan City', u'8600', u'Agusan Del Norte']
    '''
    df = pandas.read_html(html_result_string, header = 0, match = 'Post Office Name', infer_types = False, flavor = 'lxml')[0]
    df.columns = [u'#', u'Post Office Name', u'Municipality', u'Address', u'Zip Code']
    del(df['#'])
    df['Province'] = province
    for column in df.columns:
        df[column] = df[column].astype(unicode)
    return df

def test():
    import doctest
    doctest.testmod()

def main():
    import os
    import datetime
    download_dir = os.path.join('data', 'postoffices',datetime.date.today().isoformat())
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
    dfs = (parse_results(province, html_string) for province, html_string in results.items())
    big_df = reduce(lambda a,b: a.concat(b), dfs)
    return big_df

if __name__ == '__main__':
    res = download_results(u'Agusan Del Norte')
    # df = main()
    # test()
