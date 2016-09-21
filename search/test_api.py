#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__="Scott Hendrickson, Josh Montague" 

import requests
import unittest
import os

# establish import context and then import explicitly 
#from .context import gpt
#from gpt.rules import rules as gpt_r
from api import *

class TestQuery(unittest.TestCase):
    
    def setUp(self):
        self.g = Query("shendrickson@gnip.com"
            , "XXXXXXXXX"
            , "https://gnip-api.twitter.com/search/30day/accounts/shendrickson/wayback.json")
        self.g_paged = Query("shendrickson@gnip.com"
            , "XXXXXXXXX"
            , "https://gnip-api.twitter.com/search/30day/accounts/shendrickson/wayback.json"
            , paged = True
            , output_file_path = ".")

    def tearDown(self):
        # remove stray files
        for f in os.listdir("."):
    	    if re.search("bieber.json", f):
    		os.remove(os.path.join(".", f))

    def test_set_dates(self):
        s = "2014-11-01T00:00:30"
        e = "2014-11-02T00:20:00"
        self.g.set_dates(s,e)
        self.assertEquals(self.g.fromDate, "201411010000")
        self.assertEquals(self.g.toDate, "201411020020")
        with self.assertRaises(ValueError) as cm:
            self.g.set_dates(e,s)
        e = "201/1/0T00:20:00"
        with self.assertRaises(ValueError) as cm:
            self.g.set_dates(s,e)

    def test_name_munger(self):
        self.g.name_munger("adsfadsfa")
        self.assertEquals("adsfadsfa", self.g.file_name_prefix)
        self.g.name_munger('adsf"adsfa')
        self.assertEquals("adsf_Q_adsfa", self.g.file_name_prefix)
        self.g.name_munger("adsf(dsfa")
        self.assertEquals("adsf_p_dsfa", self.g.file_name_prefix)
        self.g.name_munger("adsf)dsfa")
        self.assertEquals("adsf_p_dsfa", self.g.file_name_prefix)
        self.g.name_munger("adsf:dsfa")
        self.assertEquals("adsf_dsfa", self.g.file_name_prefix)
        self.g.name_munger("adsf dsfa")
        self.assertEquals("adsf_dsfa", self.g.file_name_prefix)
        self.g.name_munger("adsf  dsfa")
        self.assertEquals("adsf_dsfa", self.g.file_name_prefix)

    def test_req(self):
        self.g.rule_payload = {'query': 'bieber', 'maxResults': 10, 'publisher': 'twitter'}
        self.g.stream_url = self.g.end_point
        self.assertEquals(10, len(json.loads(self.g.request())["results"]))
        self.g.stream_url = "adsfadsf"
        with self.assertRaises(requests.exceptions.MissingSchema) as cm:
            self.g.request()
        self.g.stream_url = "http://ww.thisreallydoesn'texist.com"
        with self.assertRaises(requests.exceptions.ConnectionError) as cm:
            self.g.request()
        self.g.stream_url = "https://ww.thisreallydoesntexist.com"
        with self.assertRaises(requests.exceptions.ConnectionError) as cm:
            self.g.request()
        
    def test_parse_responses(self):
        self.g.rule_payload = {'query': 'bieber', 'maxResults': 10, 'publisher': 'twitter'}
        self.g.stream_url = self.g.end_point
        self.assertEquals(len(self.g.parse_responses()), 10)
        self.g.rule_payload = {'maxResults': 10, 'publisher': 'twitter'}
        self.g.stream_url = self.g.end_point
        with self.assertRaises(ValueError) as cm:
            self.g.parse_responses()
        #TODO graceful way to test write to file functionality here

    def test_get_activity_set(self):
        self.g.execute("bieber", max_results=10)
        self.assertEquals(len(list(self.g.get_activity_set())), 10)
        # seconds of bieber
        tmp_start =  datetime.datetime.strftime(
                    datetime.datetime.now() + datetime.timedelta(seconds = -60)
                    ,"%Y-%m-%dT%H:%M:%S")
        tmp_end = datetime.datetime.strftime(
                    datetime.datetime.now() 
                    ,"%Y-%m-%dT%H:%M:%S")
        print >> sys.stderr, "bieber from ", tmp_start, " to ", tmp_end
        self.g_paged.execute("bieber"
                , start = tmp_start
                , end = tmp_end)
        self.assertGreater(len(list(self.g_paged.get_activity_set())), 500)

    def test_execute(self):
        #
        tmp = { "pt_filter": "bieber"
                , "max_results" : 100
                , "start" : None
                , "end" : None
                , "count_bucket" : None # None is json
                , "show_query" : False }
        self.g.execute(**tmp)
        self.assertEquals(len(self.g), 100)
        self.assertEquals(len(self.g.rec_list_list), 100)
        self.assertEquals(len(self.g.rec_dict_list), 100)
        self.assertEquals(self.g.rule_payload, {'query': 'bieber', 'maxResults': 100, 'publisher': 'twitter'})
        #
        tmp = { "pt_filter": "bieber"
                , "max_results" : 600
                , "start" : None
                , "end" : None
                , "count_bucket" : None # None is json
                , "show_query" : False }
        self.g.execute(**tmp)
        self.assertEquals(len(self.g), 500)
        self.assertEquals(len(self.g.time_series), 500)
        self.assertEquals(len(self.g.rec_list_list), 500)
        self.assertEquals(len(self.g.rec_dict_list), 500)
        self.assertEquals(self.g.rule_payload, {'query': 'bieber', 'maxResults': 500, 'publisher': 'twitter'})
        #
        tmp = datetime.datetime.now() + datetime.timedelta(seconds = -60)
        tmp_start = datetime.datetime.strftime(
                    tmp
                    , "%Y-%m-%dT%H:%M:%S")
        tmp_start_cmp =  datetime.datetime.strftime(
                    tmp
                    ,"%Y%m%d%H%M")
        tmp = datetime.datetime.now() 
        tmp_end = datetime.datetime.strftime(
                    tmp
                    ,"%Y-%m-%dT%H:%M:%S")
        tmp_end_cmp = datetime.datetime.strftime(
                    tmp
                    ,"%Y%m%d%H%M")
        tmp = { "pt_filter": "bieber"
                , "max_results" : 500
                , "start" : tmp_start 
                , "end" : tmp_end
                , "count_bucket" : None # None is json
                , "show_query" : False }
        self.g.execute(**tmp)
        self.assertEquals(len(self.g), 500)
        self.assertEquals(len(self.g.time_series), 500)
        self.assertEquals(len(self.g.rec_list_list), 500)
        self.assertEquals(len(self.g.rec_dict_list), 500)
        self.assertEquals(self.g.rule_payload, {'query': 'bieber'
                                    , 'maxResults': 500
                                    , 'toDate': tmp_end_cmp
                                    , 'fromDate': tmp_start_cmp
                                    , 'publisher': 'twitter'})
        self.assertIsNotNone(self.g.fromDate)
        self.assertIsNotNone(self.g.toDate)
        self.assertGreater(self.g.delta_t, 0) # delta_t in minutes 
        self.assertGreater(1.1, self.g.delta_t) # delta_t in minutes 
        #
        tmp = { "pt_filter": "bieber"
                , "max_results" : 100
                , "start" : None
                , "end" : None
                , "count_bucket" : "fortnight"
                , "show_query" : False }
        with self.assertRaises(ValueError) as cm:
            self.g.execute(**tmp)
        #
        tmp = { "pt_filter": "bieber"
                , "start" : None
                , "end" : None
                , "count_bucket" : "hour"
                , "show_query" : False }
        self.g.execute(**tmp)
        self.assertEquals(len(self.g), 24*30 + datetime.datetime.utcnow().hour + 1)
        self.assertGreater(self.g.delta_t, 24*30*60) # delta_t in minutes 

    def test_get_rate(self):
        self.g.res_cnt = 100
        self.g.delta_t = 10
        self.assertEquals(self.g.get_rate(), 10)
        self.g.delta_t = 11
        self.assertAlmostEquals(self.g.get_rate(), 9.09090909091)

    def test_len(self):
        self.assertEquals(0, len(self.g))
        tmp = { "pt_filter": "bieber"
                , "max_results" : 500
                , "count_bucket" : None # None is json
                , "show_query" : False }
        self.g.execute(**tmp)
        self.assertEquals(self.g.res_cnt, len(self.g))

    def test_repr(self):
        self.assertIsNotNone(str(self.g))
        tmp = { "pt_filter": "bieber"
                , "max_results" : 500
                , "count_bucket" : None # None is json
                , "show_query" : False }
        self.g.execute(**tmp)
        self.assertIsNotNone(str(self.g))
        self.assertTrue('\n' in str(self.g))
        self.assertEquals(str(self.g).count('\n'), len(self.g)-1)

if __name__ == "__main__":
    unittest.main()
