#!/usr/bin/env python2
import json
from time import sleep

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

    >>> len(lxml.html.fromstring(download_results(u'Agusan Del Norte')).xpath('//tr')) > 0
    True
    '''

    url = 'https://www.phlpost.gov.ph/postoffice-municipality.php'
    r = requests.post(url, data = {u'id': province})

    return r.text

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
    # res = download_results(u'Agusan Del Norte')
    # df = main()
    test()
