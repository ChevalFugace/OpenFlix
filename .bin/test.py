#!/usr/bin/env python3

"""
 ▄████▄   ██▓     ▒█████   █    ██ ▓█████▄   █████▒██▓    ▄▄▄       ██▀███  ▓█████     ██ ▄█▀ ██▓ ██▓     ██▓    ▓█████  ██▀███  
▒██▀ ▀█  ▓██▒    ▒██▒  ██▒ ██  ▓██▒▒██▀ ██▌▓██   ▒▓██▒   ▒████▄    ▓██ ▒ ██▒▓█   ▀     ██▄█▒ ▓██▒▓██▒    ▓██▒    ▓█   ▀ ▓██ ▒ ██▒
▒▓█    ▄ ▒██░    ▒██░  ██▒▓██  ▒██░░██   █▌▒████ ░▒██░   ▒██  ▀█▄  ▓██ ░▄█ ▒▒███      ▓███▄░ ▒██▒▒██░    ▒██░    ▒███   ▓██ ░▄█ ▒
▒▓▓▄ ▄██▒▒██░    ▒██   ██░▓▓█  ░██░░▓█▄   ▌░▓█▒  ░▒██░   ░██▄▄▄▄██ ▒██▀▀█▄  ▒▓█  ▄    ▓██ █▄ ░██░▒██░    ▒██░    ▒▓█  ▄ ▒██▀▀█▄  
▒ ▓███▀ ░░██████▒░ ████▓▒░▒▒█████▓ ░▒████▓ ░▒█░   ░██████▒▓█   ▓██▒░██▓ ▒██▒░▒████▒   ▒██▒ █▄░██░░██████▒░██████▒░▒████▒░██▓ ▒██▒
░ ░▒ ▒  ░░ ▒░▓  ░░ ▒░▒░▒░ ░▒▓▒ ▒ ▒  ▒▒▓  ▒  ▒ ░   ░ ▒░▓  ░▒▒   ▓▒█░░ ▒▓ ░▒▓░░░ ▒░ ░   ▒ ▒▒ ▓▒░▓  ░ ▒░▓  ░░ ▒░▓  ░░░ ▒░ ░░ ▒▓ ░▒▓░
  ░  ▒   ░ ░ ▒  ░  ░ ▒ ▒░ ░░▒░ ░ ░  ░ ▒  ▒  ░     ░ ░ ▒  ░ ▒   ▒▒ ░  ░▒ ░ ▒░ ░ ░  ░   ░ ░▒ ▒░ ▒ ░░ ░ ▒  ░░ ░ ▒  ░ ░ ░  ░  ░▒ ░ ▒░
░          ░ ░   ░ ░ ░ ▒   ░░░ ░ ░  ░ ░  ░  ░ ░     ░ ░    ░   ▒     ░░   ░    ░      ░ ░░ ░  ▒ ░  ░ ░     ░ ░      ░     ░░   ░ 
░ ░          ░  ░    ░ ░     ░        ░               ░  ░     ░  ░   ░        ░  ░   ░  ░    ░      ░  ░    ░  ░   ░  ░   ░     
░                                   ░     
"""

import time
import os
import re
from selenium import webdriver
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# url = "http://31.220.0.115/engine/search?name=lol&do=search"
url = "http://www2.yggtorrent.se/engine/search?name=lol&do=search"

# options = Options()
# options.headless = True
# browser = webdriver.Firefox(options=options)
# browser.get(url)
# time.sleep(5)

# page_source = browser.page_source
# browser.close()

# print(page_source)

# import cloudscraper

# scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
# # Or: scraper = cloudscraper.CloudScraper()  # CloudScraper inherits from requests.Session
# for i in range(3):
#     print(scraper.get(url).text)  # => "<!DOCTYPE html><html><head>..."
#     print(i)
#     time.sleep(4)

# import cfscrape

# scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance
# # Or: scraper = cfscrape.CloudflareScraper()  # CloudflareScraper inherits from requests.Session
# print(scraper.get(url).content)

# import requests

# print(requests.get(url,headers={"Host":"www2.yggtorrent.se"}, allow_redirects=False).content)
# print(requests.get(url,headers={"Host":"www.yggtorrent.se"}).content)

# from selenium import webdriver

# driver = webdriver.Firefox(options=options)
# driver.get("http://yggtorrent.se/")
# cookies_list = driver.get_cookies()
# cookies_dict = {}
# for cookie in cookies_list:
#     cookies_dict[cookie['name']] = cookie['value']

# print(cookies_dict)
useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
timeout = 20

driverpath = os.path.join(os.path.dirname(__file__), "chromedriver")

def create_driver() -> webdriver.Chrome :

    return Chrome()

def cookies_present(driver):

    cookie = driver.get_cookie("cf_clearance")
    if cookie:
        return cookie
    return False

options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = Chrome(options=options)

driver.get(url)

try:
    WebDriverWait(driver, timeout).until(cookies_present)
except TimeoutException:
    print("timeout")
else:
    print(driver.get_cookie("cf_clearance"))

# cookies_dict = {
#  "__cf_bm":	"a96d39602a304fa29acf03d800ca9886fa2adefa-1586909561-1800-AXm2XISoipv8Nu4Zk7IROO+vnf27ZTurxRqOUQHSAhPh2iSgwoz41oTHuKb1NULA1ZxhbW6yJNLlQkyds3+ls8xrURaiAEyhkrwPLNgrTbG6",
# "__cfduid":	"d2e240032f0722a41013cc0e043906d971586214014",
# "__cfduid":	"d838ba153dd09d83add9638439fd951971584543547",
# "__ga":	"8db903921defd58ec35beb7ddd9651d0"		,
# "_gaexp":	"GAX1.2.F1TUXwUUT0Se6Gfj12LK3w.18444.1!J9hmXvOBR-KK-m03BeD2Ug.18454.0",
# "cf_clearance":	"2640c96aa5c5d764817f87de1be4c2cdc37a9543-1586908195-0-150"}

# import pychrome

# browser = pychrome.Browser()


# def get_cookie(cookies, name, domain=None):

#     for cookie in cookies:
#         if cookie.get("name") == name:
#             if domain is None or cookie.get("domain") == domain:
#                 return name, cookie.get("value")
#     return "", ""

# def get_cookies(cookies):

#     items= (get_cookie(cookies, "__cf_bm",   ".yggtorrent.se"),
#             get_cookie(cookies, "__cfduid",  ".yggtorrent.se"),
#             get_cookie(cookies, "__ga",      ".yggtorrent.se"),
#             get_cookie(cookies, "_gaexp",    ".cloudflare.com"),
#             get_cookie(cookies, "cf_clearance",".yggtorrent.se"),
#             get_cookie(cookies, "cfmrk_userLangRedirect",".cloudflare.com")
#             )
#     return {k:v for k,v in items}

# def is_cookie_ready(cookies):
#     for cookie in cookies:
#         if (cookie["name"] == "__cfduid" and 
#             cookie["domain"] == ".yggtorrent.se"):
#             return True
#     return False

# try:
#     _ = browser.version()
# except Exception as e:
#     print(e)
# else:
#     # for tab in browser.list_tab():
#     #     tab_url = tab._kwargs.get("url")
#     #     if tab_url.startswith(url):
#     #         tab.start()
#     #         tab.Page.reload(ignorecache=True)
#     #         browser.activate_tab(tab)
#     #         break
#     for tab in browser.list_tab():
#         tab_url = tab._kwargs.get("url")
#         if re.match(r'https?://www2?\.yggtorrent\..*', tab_url):
#             break
#     else:
#         browser.new_tab(url)

#     for tab in browser.list_tab():
#         tab_url = tab._kwargs.get("url")
#         print(tab_url)
#         if re.match(r'https?://www2?\.yggtorrent\..*', tab_url):
#             print("ok")
#             tab.start()
#             cookies = []

#             while True:

#                 cookies = tab.call_method("Network.getCookies").get("cookies")
                
#                 if is_cookie_ready(cookies):
#                     break

#                 time.sleep(1)
            
#             cookies = get_cookies(cookies)
            
#             resp = requests.get(url, cookies=cookies, headers={"User-Agent":useragent})
#             print(resp.content)
#             break

