import os
import random
import zipfile
from pathlib import Path

from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

try:
    from .gologin import GoLogin
    from .automator_snippets import GetProxy
except:
    from gologin import GoLogin
    from automator_snippets import GetProxy
    pass



class Create_Profile():
    def __init__(self):
        load_dotenv()
        self.gologin_token = os.environ.get('GOLOGIN_TOKEN')
        self.profile_id:str
        self.os_for_profile = 'win'
        self.gl = GoLogin({"token":self.gologin_token})
        self.proxy_password = self.get_proxy_password()
        self.proxy = str(os.environ.get('PROXY')).lower() == 'true'
    def get_proxy_password(self):
        proxy_string = GetProxy().get_proxy()
        proxy_string = proxy_string['server'].split('@')[0].split(':')[-1]
        return proxy_string

    def get_profile(self):
        if not self.proxy:
            profile_id = self.gl.create({
                "name": f'profile_{random.randint(1, 100000)}',
                "os": self.os_for_profile,
                "navigator": {
                    "language": 'en-US',
                    "userAgent": 'random',
                    "resolution": 'random',
                    "platform": self.os_for_profile,
                },
                'proxyEnabled': False,  # Specify 'false' if not using proxy
                'proxy': {
                    'mode': 'none',
                    'autoProxyRegion': 'us'
                    # 'host': '',
                    # 'port': '',
                    # 'username': '',
                    # 'password': '',
                },
                "webRTC": {
                    "mode": "alerted",
                    "enabled": True,
                },
            })
        else:
            profile_id = self.gl.create({
                "name": f'profile_{random.randint(1, 100000)}',
                "os": self.os_for_profile,
                "navigator": {
                    "language": 'en-US',
                    "userAgent": 'random',
                    "resolution": 'random',
                    "platform": self.os_for_profile,
                },
                'proxyEnabled': True,  # Specify 'false' if not using proxy
                'proxy': {
                    'mode': 'http',
                    "host": 'geo.iproyal.com',
                    "port": 12321,
                    "username": f'goroyal',
                    "password": self.proxy_password,
                },
                "webRTC": {
                    "mode": "alerted",
                    "enabled": True,
                },
            })
        return profile_id



class Create_Browser():
    def __init__(self):
        load_dotenv()
        self.gologin_token = os.environ.get('GOLOGIN_TOKEN')
        self.PATH = os.path.abspath(os.path.dirname(__file__))
        self.profile=Create_Profile()
        self.profile_id = self.profile.get_profile()
        self.proxy_password = self.profile.proxy_password
        self.gl = GoLogin({"token":self.gologin_token,"profile_id":self.profile_id})
        self.proxy = str(os.environ.get('PROXY')).lower() == 'true'
    def get_driver(self):
        debugger_address = self.gl.start()
        print(debugger_address)
        driver_path = Path(self.PATH).joinpath('chromedriver.exe')
        service = Service(executable_path=str(driver_path))
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        if self.proxy:
            chrome_options.add_extension(self.get_chromedriver())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    def delete_profile(self):
        try:
            GoLogin({"token":self.gologin_token}).delete(self.profile_id)
            return True
        except:
            return False

    def get_chromedriver(self):
        PROXY_HOST = 'geo.iproyal.com'  # rotating proxy or host
        PROXY_PORT = 12321  # port
        PROXY_USER = 'goroyal'  # username
        PROXY_PASS = self.proxy_password  # password
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        return pluginfile

if __name__ == '__main__':
    Create_Browser()