#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__="Scott Hendrickson, Josh Montague" 

import requests
import unittest
import os
import copy
import time

# establish import context and then import explicitly 
#from .context import gpt
#from gpt.rules import rules as gpt_r
from data_elements import *

class TestQueryElements(unittest.TestCase):
    
    def setUp(self):
        self.g = QueryElements("shendrickson@gnip.com"
            , "XXXXXXXXXXXXX"
            , "https://search.gnip.com/accounts/shendrickson/search/wayback.json")
        self.g_paged = QueryElements("shendrickson@gnip.com"
            , "XXXXXXXXXXXXX"
            , "https://search.gnip.com/accounts/shendrickson/search/wayback.json"
            , paged = True
            , output_file_path = ".")

    def tearDown(self):
        # remove stray files
        for f in os.listdir("."):
    	    if re.search("bieber.json", f):
    		os.remove(os.path.join(".", f))

    def test_get(self):
        self.g.get(pt_filter = "bieber" 
            , max_results = 10
            , start = None
            , end = None
            , count_bucket = None
            , query = False)
        self.assertEquals(len(self.g), 10)
        tmp = copy.copy(self.g.rec_list_list)
        time.sleep(3)
        self.g.get(pt_filter = "bieber" 
            , max_results = 10
            , start = None
            , end = None
            , count_bucket = None
            , query = False)
        self.assertEquals(len(self.g), 10)
        # make sure we have exactly the same data set, not a new one
        self.assertEquals(tmp, self.g.rec_list_list)

    def test_get_activities(self):
        for x in self.g.get_activities(pt_filter = "bieber" 
                , max_results = 10
                , start = None
                , end = None
                , count_bucket = None
                , query = False):
            self.assertTrue("id" in x)
        self.assertEqual(len(list( self.g.get_activities(pt_filter = "bieber" 
                , max_results = 10
                , start = None
                , end = None
                , count_bucket = None
                , query = False))), 10)
        # seconds of bieber
        tmp_start =  datetime.datetime.strftime(
                    datetime.datetime.now() + datetime.timedelta(seconds = -60)
                    ,"%Y-%m-%dT%H:%M:%S")
        tmp_end = datetime.datetime.strftime(
                    datetime.datetime.now() 
                    ,"%Y-%m-%dT%H:%M:%S")
        self.assertGreater(len(list(self.g_paged.get_activities(pt_filter = "bieber"
                , start = tmp_start
                , end = tmp_end))), 1000)
        
    def test_get_time_series(self):
        self.assertGreater(len(list(self.g.get_time_series(pt_filter = "bieber" 
                , max_results = 10
                , start = None
                , end = None
                , count_bucket = "hour" 
                , query = False))), 24*30)

    def test_get_top_links(self):
        self.assertEqual(len(list(self.g.get_top_links(n = 5
                , pt_filter = "bieber" 
                , max_results = 200
                , start = None
                , end = None
                , count_bucket = None 
                , query = False))), 5)
        self.assertEqual(len(list(self.g.get_top_links(n = 10
                , pt_filter = "bieber" 
                , max_results = 200
                , start = None
                , end = None
                , count_bucket = None
                , query = False))), 10)
        #
        tmp_start = datetime.datetime.strftime(
                    datetime.datetime.now() + datetime.timedelta(seconds = -60)
                    ,"%Y-%m-%dT%H:%M:%S")
        tmp_end = datetime.datetime.strftime(
                    datetime.datetime.now() 
                    ,"%Y-%m-%dT%H:%M:%S")
        self.assertEqual(len(list(self.g_paged.get_top_links(n = 100
                , pt_filter = "bieber" 
                , max_results = 500
                , start = tmp_start
                , end = tmp_end
                , count_bucket = None
                , query = False))), 100)

    def test_top_users(self):
        self.assertEqual(len(list(self.g.get_top_users(n = 5
                , pt_filter = "bieber" 
                , max_results = 200
                , start = None
                , end = None
                , count_bucket = None 
                , query = False))), 5)
        self.assertEqual(len(list(self.g.get_top_users(n = 10
                , pt_filter = "bieber" 
                , max_results = 200
                , start = None
                , end = None
                , count_bucket = None
                , query = False))), 10)
        #
        tmp_start = datetime.datetime.strftime(
                    datetime.datetime.now() + datetime.timedelta(seconds = -60)
                    ,"%Y-%m-%dT%H:%M:%S")
        tmp_end = datetime.datetime.strftime(
                    datetime.datetime.now() 
                    ,"%Y-%m-%dT%H:%M:%S")
        self.assertEqual(len(list(self.g_paged.get_top_users(n = 100
                , pt_filter = "bieber" 
                , max_results = 500
                , start = tmp_start
                , end = tmp_end
                , count_bucket = None
                , query = False))), 100)
        self.assertEqual(len(list(self.g.get_frequency_items(8))), 8)

    def test_top_grams(self):
        self.assertEqual(len(list(self.g.get_top_grams(n = 5
                , pt_filter = "bieber" 
                , max_results = 200
                , start = None
                , end = None
                , count_bucket = None 
                , query = False))), 10)
        self.assertEqual(len(list(self.g.get_top_grams(n = 10
                , pt_filter = "bieber" 
                , max_results = 200
                , start = None
                , end = None
                , count_bucket = None
                , query = False))), 20)
        self.assertEqual(len(list(self.g.get_frequency_items(8))), 16)
        #
        tmp_start = datetime.datetime.strftime(
                    datetime.datetime.now() + datetime.timedelta(seconds = -60)
                    ,"%Y-%m-%dT%H:%M:%S")
        tmp_end = datetime.datetime.strftime(
                    datetime.datetime.now() 
                    ,"%Y-%m-%dT%H:%M:%S")
        self.assertEqual(len(list(self.g_paged.get_top_grams(n = 100
                , pt_filter = "bieber" 
                , max_results = 500
                , start = tmp_start
                , end = tmp_end
                , count_bucket = None
                , query = False))), 200)
        
    def test_get_geo(self):
        tmp = len(list(self.g.get_geo(
                pt_filter = "bieber has:geo" 
                , max_results = 200
                , start = None
                , end = None
                , count_bucket = None 
                , query = False)))
        self.assertGreater(201, tmp)
        self.assertGreater(tmp, 10)


if __name__ == "__main__":
    unittest.main()
