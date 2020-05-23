#!/usr/bin/env python3

#
#   /$$$$$$  /$$$$$$$$       /$$                                                       
#  /$$__  $$| $$_____/      | $$                                                       
# | $$  \__/| $$            | $$$$$$$  /$$   /$$  /$$$$$$   /$$$$$$   /$$$$$$$ /$$$$$$$
# | $$      | $$$$$         | $$__  $$| $$  | $$ /$$__  $$ |____  $$ /$$_____//$$_____/
# | $$      | $$__/         | $$  \ $$| $$  | $$| $$  \ $$  /$$$$$$$|  $$$$$$|  $$$$$$ 
# | $$    $$| $$            | $$  | $$| $$  | $$| $$  | $$ /$$__  $$ \____  $$\____  $$
# |  $$$$$$/| $$            | $$$$$$$/|  $$$$$$$| $$$$$$$/|  $$$$$$$ /$$$$$$$//$$$$$$$/
#  \______/ |__/            |_______/  \____  $$| $$____/  \_______/|_______/|_______/ 
#                                      /$$  | $$| $$                                   
#                                     |  $$$$$$/| $$                                   
#                                      \______/ |__/ 
#

import time
import os
import atexit
import logging
from threading import Event

from selenium import webdriver
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from requests.sessions import Session
from requests.cookies import create_cookie
from requests.compat import urlparse
from requests import Response


class CFBypass(Session):

    def __init__(self, *args, **kwargs):

        super().__init__()

        self.load_config(kwargs)
        self._event = Event()
        self._event.set()
        
        options = ChromeOptions()
        options.add_argument("headless")
        self.driver = Chrome(options=options)

        self.update_useragent()
        self.solve_challenge(kwargs.get("url"))
        
        atexit.register(self.driver.quit)

    def __del__(self):
        self.driver.quit()

    def update_useragent(self):

        user_agent = self.driver.execute_script(
            "return navigator.userAgent"
        )

        self.headers["User-Agent"] = user_agent
    
    @staticmethod
    def is_iuam_challenge(resp):
        return (
            resp.status_code in (503, 429)
            and resp.headers.get("Server", "").startswith("cloudflare")
            and b"jschl_vc" in resp.content
            and b"jschl_answer" in resp.content
        )

    def request(self, method, url, *args, **kwargs):

        resp = super().request(method, url, *args, **kwargs)

        if self.is_iuam_challenge(resp):
            if self._event.is_set():
                self.solve_challenge(url)
                resp = super().request(method, url, *args, **kwargs)
            else:
                self._event.wait()
                self.request(method, url, *args, **kwargs)
    
        return resp

    def load_config(self, options):

        self.config = options
        self.config.setdefault("cookies", ( "__cf_bm", "__cfduid", "__ga",
                                            "_gaexp", "cf_clearance"))
        self.config.setdefault("timeout",20)

    def test_finished(self, driver):

        cookie = driver.get_cookie("cf_clearance")
        if cookie:
            return cookie
        return False

    def create_response(self, status):

        response = Response()

        if status:
            response.code = "ok"
            response.status_code = 200
            response._content = self.driver.page_source.encode()
        else:
            response.code = "expired"
            response.status_code = 400
            response._content = b""
        
        return response

    def set_cookies(self):

        for cookie in self.cookies:
            self.driver.add_cookie({"name": cookie.name,
                                    "value": cookie.value,
                                    "domain": cookie.domain})

    def update_cookies(self):

        domain = urlparse(self.driver.current_url).netloc
        cookie_names = self.config.get("cookies",())

        for cookie_name in cookie_names:
            cookie = self.driver.get_cookie(cookie_name)

            if not cookie:
                continue

            cookie_domain   = cookie.get("domain")
            cookie_name     = cookie.get("name")     
            cookie_value    = cookie.get("value")  

            if domain.endswith(cookie_domain):
                cookie_object = create_cookie(cookie_name,cookie_value)
                self.cookies.set_cookie(cookie_object)

    def solve_challenge(self, url):

        self._event.clear()

        if url is None:
            self._event.set()
            return
        
        self.driver.get(url)

        try:
            wait = WebDriverWait(self.driver, self.config["timeout"])
            wait.until(self.test_finished)
        except TimeoutException:
            logging.info("could not bypass cf : timeout")
        else:
            self.update_cookies()
        
        self._event.set()


def create_cfhandler(*args, **kwargs):
    return CFBypass(*args, **kwargs)

# url = "http://www2.yggtorrent.se/engine/search?name=lol&do=search"

# g = create_cfhandler()

# r = g.get(url)
# print(r.content)


