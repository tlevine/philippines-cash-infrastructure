#!/usr/bin/env python2
import json
from time import sleep

import numpy
import lxml.html
import requests
import pandas
# from omgeo import Geocoder
from pygeocoder import Geocoder

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

def geocode(df):
    g = Geocoder()

    column_sets = {
        'Municipality': ['Longitude (Geocoded Municipality)', 'Latitude (Geocoded Municipality)'],
        'Address':      ['Longitude (Geocoded Address)', 'Latitude (Geocoded Address)'],
    }

    def f(row, column):
        '''
        column must be one of "Municipality" and "Address"
        '''
        na = (numpy.nan, numpy.nan)
        if numpy.isnan(row[column]):
            return row

        result = g.geocode(row[column] + ', Philippines')

        # Validation could be improved; we could check the post code.
        # http://code.xster.net/pygeocoder/wiki/Home#!geocoding
        if result.count == 0 or result.country != 'Philippines' or result.postal_code != row['Zip Code']:
            row[column_sets[column]] = na
        else:
            row[column_sets[column]] = result.coordinates

        row['Geocode ' + column] = result
        return row

    for col in reduce(lambda a,b: a+b, column_sets.values()) + ['Geocode Address', 'Geocode Municipality']:
        df[col] = numpy.nan

    for i in df.index:
        for column in ['Municipality','Address']:
            df.ix[i] = f(df.ix[i], column)
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
            results[province] = open(province_file).read().decode('utf-8')
        else:
            results[province] = download_results(province)
            open(province_file, 'w').write(results[province].encode('utf-8'))

    # Parse results
    df = pandas.concat((parse_results(province, html_string) for province, html_string in results.items()))
    df.to_csv(os.path.join(download_dir, 'postoffices.csv'), encoding = 'utf-8', index = False)
    return df

def break_up_address(combined_address, municipality):
    '''
    >>> break_up_address("Max Suniel St., Carmen, CDeO", "Metro Cagayan De Oro")
    ("Max Suniel St.", "Carmen")

    >>> break_up_address("Municipal Bldg.,Lanuza, Surigao del Sur", "Surigao del Sur")
    ("Municipal Bldg.","Lanuza")
    '''
    return building, town

if __name__ == '__main__':
    test()
    main()
