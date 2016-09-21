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
from results import *

class TestResults(unittest.TestCase):
    
    def setUp(self):
        self.params = { 
              "user":"shendrickson@gnip.com"
            , "password":"XXXXXXXXX"
            , "stream_url":"https://gnip-api.twitter.com/search/30day/accounts/shendrickson/wayback.json" 
            }

    def tearDown(self):
        # remove stray files
        for f in os.listdir("."):
    	    if re.search("bieber.json", f):
    		os.remove(os.path.join(".", f))

    def test_get(self):
        self.g = Results(
            pt_filter = "bieber" 
            , max_results = 10
            , start = None
            , end = None
            , count_bucket = None
            , show_query = False
            , **self.params)
        self.assertEquals(len(self.g), 10)

    def test_get_activities(self):
        self.g = Results(
                 pt_filter = "bieber"
                , max_results = 10
                , start = None
                , end = None
                , count_bucket = None
                , show_query = False
                , **self.params)
        for x in self.g.get_activities():
            self.assertTrue("id" in x)
        self.assertEqual(len(list(self.g.get_activities())), 10)
        # seconds of bieber
        tmp_start =  datetime.datetime.strftime(
                    datetime.datetime.now() + datetime.timedelta(seconds = -60)
                    ,"%Y-%m-%dT%H:%M:%S")
        tmp_end = datetime.datetime.strftime(
                    datetime.datetime.now() 
                    ,"%Y-%m-%dT%H:%M:%S")
        self.g_paged = Results(
                pt_filter = "bieber"
                , max_results = 500
                , start = tmp_start
                , end = tmp_end
                , count_bucket = None
                , show_query = False
                , paged = True
                , **self.params)
        tmp = len(list(self.g_paged.get_activities())) 
        self.assertGreater(tmp, 1000)
        self.g_paged = Results(
                pt_filter = "bieber"
                , max_results = 500
                , start = tmp_start
                , end = tmp_end
                , count_bucket = None
                , show_query = False
                , paged = True
                , output_file_path = "."
                , **self.params)
        self.assertEqual(len(list(self.g_paged.get_activities())), tmp)
        
    def test_get_time_series(self):
        self.g = Results(
                pt_filter = "bieber"
                , max_results = 10
                , start = None
                , end = None
                , count_bucket = "hour"
                , show_query = False
                , **self.params)
        self.assertGreater(len(list(self.g.get_time_series())), 24*30)

    def test_get_top_links(self):
        self.g = Results(
                pt_filter = "bieber"
                , max_results = 200
                , start = None
                , end = None
                , count_bucket = None
                , show_query = False
                , **self.params)
        self.assertEqual(len(list(self.g.get_top_links(n = 5))), 5)
        self.assertEqual(len(list(self.g.get_top_links(n = 10))),10)
        #
        tmp_start = datetime.datetime.strftime(
                    datetime.datetime.now() + datetime.timedelta(seconds = -60)
                    ,"%Y-%m-%dT%H:%M:%S")
        tmp_end = datetime.datetime.strftime(
                    datetime.datetime.now() 
                    ,"%Y-%m-%dT%H:%M:%S")
        self.g_paged = Results(
                pt_filter = "bieber"
                , max_results = 500
                , start = tmp_start 
                , end = tmp_end
                , count_bucket = None
                , show_query = False
                , paged = True
                , **self.params)
        self.assertEqual(len(list(self.g_paged.get_top_links(n = 100))), 100)

    def test_top_users(self):
        self.g = Results(
                pt_filter = "bieber"
                , max_results = 200
                , start = None
                , end = None
                , count_bucket = None
                , show_query = False
                , **self.params)
        self.assertEqual(len(list(self.g.get_top_users(n = 5))), 5)
        self.assertEqual(len(list(self.g.get_top_users(n = 10))), 10)
        #
        tmp_start = datetime.datetime.strftime(
                    datetime.datetime.now() + datetime.timedelta(seconds = -60)
                    ,"%Y-%m-%dT%H:%M:%S")
        tmp_end = datetime.datetime.strftime(
                    datetime.datetime.now() 
                    ,"%Y-%m-%dT%H:%M:%S")
        self.g_paged = Results(
                pt_filter = "bieber"
                , max_results = 500
                , start = tmp_start 
                , end = tmp_end
                , count_bucket = None
                , show_query = False
                , paged = True
                , **self.params)
        self.assertEqual(len(list(self.g_paged.get_top_users(n = 100))), 100)
        self.assertEqual(len(list(self.g.get_frequency_items(8))), 8)

    def test_top_grams(self):
        self.g = Results(
                pt_filter = "bieber"
                , max_results = 200
                , start = None
                , end = None
                , count_bucket = None
                , show_query = False
                , **self.params)
        self.assertEqual(len(list(self.g.get_top_grams(n = 5)))  , 10)
        self.assertEqual(len(list(self.g.get_top_grams(n = 10))) , 20)
        self.assertEqual(len(list(self.g.get_frequency_items(8))), 16)
        #
        tmp_start = datetime.datetime.strftime(
                    datetime.datetime.now() + datetime.timedelta(seconds = -60)
                    ,"%Y-%m-%dT%H:%M:%S")
        tmp_end = datetime.datetime.strftime(
                    datetime.datetime.now() 
                    ,"%Y-%m-%dT%H:%M:%S")
        self.g_paged = Results(
                pt_filter = "bieber"
                , max_results = 500
                , start = tmp_start 
                , end = tmp_end
                , count_bucket = None
                , show_query = False
                , paged = True
                , **self.params)
        self.assertEqual(len(list(self.g_paged.get_top_grams(n = 100))), 200)
        
    def test_get_geo(self):
        self.g = Results(
                pt_filter = "bieber has:geo"
                , max_results = 200
                , start = None
                , end = None
                , count_bucket = None
                , show_query = False
                , **self.params)
        tmp = len(list(self.g.get_geo()))
        self.assertGreater(201, tmp)
        self.assertGreater(tmp, 10)

if __name__ == "__main__":
    unittest.main()
