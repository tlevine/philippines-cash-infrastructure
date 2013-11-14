#!/usr/bin/env python2
import json
from time import sleep

import numpy
import lxml.html
import requests
import pandas

ALIASES = {
    'Metro Cagayan De Oro': 'CDeO',
    'Cotabato City': "Cotabato Citu",
    'North Cotabato': 'Cotabato',
}

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
    df = pandas.read_html(html_result_string, header = 0, match = 'Post Office Name', infer_types = False, flavor = 'bs4')[0]
    df.columns = [u'#', u'Post Office Name', u'Municipality', u'Address', u'Zip Code']
    del(df['#'])
    df['Province'] = province
    for column in df.columns:
        df[column] = df[column].astype(unicode)
    return df

def test():
    import doctest
    # doctest.testmod()
    doctest.run_docstring_examples(building_from_address, globals())

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
            results[province] = open(province_file).read().decode('utf-8')
        else:
            results[province] = download_results(province)
            open(province_file, 'w').write(results[province].encode('utf-8'))

    # Parse results
    df = pandas.concat((parse_results(province, html_string) for province, html_string in results.items()))
    df.to_csv(os.path.join(download_dir, 'postoffices.csv'), encoding = 'utf-8', index = False)
    return df

import re
def building_from_address(combined_address, municipality, province):
    '''
    >>> building_from_address('Max Suniel St., Carmen, CDeO', 'Carmen', 'Metro Cagayan De Oro')
    'Max Suniel St.'

    >>> building_from_address('Municipal Bldg.,Lanuza, Surigao del Sur', 'Lanuza', 'Surigao del Sur')
    'Municipal Bldg.'

,Cotabato City,"Bonifacio St., Cotabato Citu",9600,Maguindanao
    >>> building_from_address("Poblacion Isulan, Sultan Kudarat", "Isulan", "Sultan Kudarat")

    >>> building_from_address("Bonifacio St., Cotabato Citu", 'Cotabato City', 'Maguindanao')
    'Bonifacio St.'

    >>> building_from_address("Municipal Bldg.,Boston, Davao Oriental","Boston","Davao Oriental")
    'Municipal Bldg.'

    >>> building_from_address("Municipal Hall Bldg., Malalag, Davao del Sur", "Malalag","Davao Del Sur")
    'Municipal Hall Bldg.'

    >>> building_from_address("Poblacion Kabacan, Cotabato",'Kabacan', 'North Cotabato')

    >>> building_from_address("Ipil, Zambo. Sibugay", "Zamboanga", "Sibugay")
    'Ipil'

    >>> building_from_address("Mintal Proper, Tugbok District, Davao City",'Davao City', 'Metro Davao')
    'Mintal Proper'
    '''

    full_address = re.split(r', ?', combined_address)
    no_province = _maybe_remove(full_address, province)
    no_municipality_neither = _maybe_remove(no_province, municipality)
    broken_up = _maybe_remove(no_municipality_neither, 'District')

    if len(broken_up) == 0:
        return None
    elif len(broken_up) == 1:
        return broken_up[0]
    else:
        raise NotImplementedError("I couldn't handle this address.")

def _maybe_remove(full_address, thing):
    if len(full_address) > 0 and thing.lower() in full_address[-1].lower() or (thing in ALIASES and ALIASES[thing].lower() in full_address[-1].lower()):
        return full_address[:-1]
    else:
        return full_address

if __name__ == '__main__':
    test()
    # main()
