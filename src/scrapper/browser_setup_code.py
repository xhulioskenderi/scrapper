from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import random
import requests 
from ua_parse import parse_ua
import os 
import datetime
import json
from proxy_rotator import ScoreBasedProxyRotator
from collections import OrderedDict
import uuid
import redis
from urllib.parse import urlparse
from fake_useragent import UserAgent

script_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.join(script_dir, 'text_files')




class CustomHTTPProxy:
    def __init__(self, session_id) -> None:
        self.session_id = session_id

    def transmit_session_id(self):
        return(
            
        )

class RotateUserAgents:
    #Implement logs
    def __init__(self):
        self.supported_browsers = ["Chrome", "Firefox"]


    def get_useragents(self) -> None:

        file_path1 = target_dir+'/chrome_ua.json'
        file_path2 = target_dir+'/firefox_ua.json'
        '''
        if os.path.isfile(file_path1) == False:
            file_names = ['chrome_ua.json', 'firefox_ua.json']
            for file_name in file_names:
                try:
                    with open(f'{target_dir}/{file_name}', 'x') as f:
                        pass
                except FileExistsError:
                    print(f"The file {file_name} already exists.")

        '''
        
        file_timestamp1 = os.path.getmtime(file_path1)
        file_date1 = datetime.datetime.fromtimestamp(file_timestamp1).date()
        now = datetime.datetime.now().date()
        

        if file_date1 != now:
            try:
                r = requests.get('https://www.useragents.me/api')
            except Exception as err:
                print('There was an error when fetching the user agents')
                return
            ua = UserAgent()

            # Generate 20 Chrome user agents
            chrome_useragent = [ua.chrome for _ in range(20)]
            # Generate 20 Mozilla user agents
            mozilla_useragent = [ua.firefox for _ in range(20)]

            with open(os.path.join(target_dir, 'chrome_ua.json'), 'w') as file:
                json.dump(chrome_useragent, file)
        
            with open(os.path.join(target_dir, 'firefox_ua.json'), 'w') as file:
                json.dump(mozilla_useragent, file)

        else:
            pass
    
    def choose_chrome(self):
        with open(os.path.join(target_dir, 'chrome_ua.json'), 'r') as f:
            data = json.load(f)
        total_weight = sum(data.values())
        normalized_dict = {k: v / total_weight for k, v in data.items()}

        keys = list(normalized_dict.keys())
        weights = list(normalized_dict.values())

        chosen_key = random.choices(keys, weights, k=1)[0]
        print(chosen_key)
        return chosen_key
    
    def choose_mozilla(self):

        with open(os.path.join(target_dir, 'firefox_ua.json'), 'r') as f:
            data = json.load(f)
        total_weight = sum(data.values())
        normalized_dict = {k: v / total_weight for k, v in data.items()}

        keys = list(normalized_dict.keys())
        weights = list(normalized_dict.values())

        chosen_key = random.choices(keys, weights, k=1)[0]
        print(chosen_key)
        return chosen_key





class ProfileGenerator:

    def __init__(self, driver):
        self.driver = driver
        self.weighted_cpus = {
            4 : 32.663316582914575,
            6 : 40.74120603015076,
            8 : 26.59547738693468
        }

        self.weighted_ram = {
            8  : 20.466744457409565,
            16 : 58.98483080513418,
            32 : 20.54842473745624
        }

        self.weighted_os = {
            'MacIntel' : 37.799253239622224,
            'Win32'    : 62.20074676037777
        }
        self.list_of_profiles = []

    def weighted_choice(self, weighted_dict):
        total = sum(weighted_dict.values())
        weights = [val / total for val in weighted_dict.values()]

        choice = random.choices(
            population=list(weighted_dict.keys()),
            weights=weights,
            k=1
        )[0]

        return choice

    def inject_profiles(self):
        selected_cpu = self.weighted_choice(self.weighted_cpus)
        selected_ram = self.weighted_choice(self.weighted_ram)
        selected_os = self.weighted_choice(self.weighted_os)

        script = """
            Object.defineProperty(navigator, 'webdriver', {
             get: function() { return undefined; }
            });
                """
        self.driver.execute_script(script)

        script1 = f"""
            Object.defineProperty(navigator, 'platform', {{
             get: function () {{
                return '{selected_os}';
            }}
            }});
        """

        self.driver.execute_script(script1)

        script2 = f"""
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
             get: function () {{
                return {selected_cpu};
            }}
            }});
        """

        self.driver.execute_script(script2)


        device_memory_exists = self.driver.execute_script("return navigator.deviceMemory !== undefined;")

        if device_memory_exists:

            script3 = f"""
            Object.defineProperty(navigator, 'deviceMemory', {{
        get: function () {{
            return {selected_ram};
            }}
            }});
            
            """

            self.driver.execute_script(script3)



 

class ProfilePool:
    def __init__(self):
        self.available_profiles = [
            'Profile 1', 'Profile 2', 'Profile 3', 'Profile 4', 'Profile 5', 'Profile 6', 'Profile 7',
            'Profile 8', 'Profile 9', 'Profile 10', 'Profile 11', 'Profile 12', 'Profile 13', 'Profile 14', 'Profile 15'
            ]
        self.in_use_profiles = []

    def get_profile(self):
        if len(self.available_profiles) == 0:
            raise ValueError("No more profiles available")

        profile = self.available_profiles.pop()
        self.in_use_profiles.append(profile)
        return profile

    def release_profile(self, profile):
        if profile in self.in_use_profiles:
            self.in_use_profiles.remove(profile)
            self.available_profiles.append(profile)
        else:
            raise ValueError("Trying to release a profile that's not in use")


class MozillaProfilePool:
    def __init__(self):
        self.available_profiles = [
            '0dzjqmi8.Mozilla 1', '7wvk58qd.Moziila3', 'q5u1gaui.Mozilla4'
            ]
        self.in_use_profiles = []

    def get_profile(self):
        if len(self.available_profiles) == 0:
            raise ValueError("No more profiles available")

        profile = self.available_profiles.pop()
        self.in_use_profiles.append(profile)
        return profile

    def release_profile(self, profile):
        if profile in self.in_use_profiles:
            self.in_use_profiles.remove(profile)
            self.available_profiles.append(profile)
        else:
            raise ValueError("Trying to release a profile that's not in use")

class Mozilla:

    def randomize_resolution(self, remote=False):
        resList = [(1920,1080), (1366,768), (1440,900), (1536,864), (2560,1440), (1680,1050), (1280,720), (1280,800), (1792,1120), (1600,900)]
        randomize = random.randint(0, len(resList)-1)
        pickResolution = resList[randomize]
        return pickResolution


    def __init__(self, proxy_ip = None, proxy_port = None, remote = False) -> None:
        self.randomize_width, self.randomize_height = self.randomize_resolution()
        self.options = FirefoxOptions()
        base_dir = os.path.dirname(os.path.realpath(__file__))
        user_data_dir = os.path.join(base_dir, 'mozilla_profiles', 'Profiles')
        profiles = MozillaProfilePool()
        chosen_profile = profiles.get_profile()
        profile_path = os.path.join(user_data_dir, chosen_profile)
        self.profile = FirefoxProfile(profile_path)
        user_agent = RotateUserAgents()
        user_agent.get_useragents()
        user_agent_string = user_agent.choose_mozilla()
        self.options.set_preference("general.useragent.override",user_agent_string)
        self.options.set_preference("dom.webnotifications.serviceworker.enabled", False)
        self.options.set_preference("dom.webnotifications.enabled", False)
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.service = FirefoxService("/Users/xhulioskenderi/Desktop/CryptoP/openai-quickstart-python/scrapper/tests/geckodriver")
        

        if proxy_ip and proxy_port:
            self.profile.set_preference("network.proxy.type", 1)
            self.profile.set_preference("network.proxy.socks", proxy_ip)
            self.profile.set_preference("network.proxy.socks_port", proxy_port)
            self.profile.set_preference("network.proxy.socks_version", 5)
            self.profile.update_preferences()

        if remote:
            self.driver = webdriver.Remote(
                command_executor='http://localhost:4444',
                options=self.options,
            )
        else:
            self.driver = webdriver.Firefox(service=self.service, options=self.options)
        
        self.driver.set_window_size(self.randomize_width, self.randomize_height)
        
            

    def get_driver(self):
        return self.driver

class Chrome:
    API_ENDPOINT = "http://localhost:9000"


    #Remember that we talk to the socsks5 proxy server via this now look at chatgpt 
    def get_proxy_info(self, session_id, api_key):
        """
        Contact the FastAPI server to fetch the proxy information associated 
        with the given session_id. If the session_id does not have an associated 
        proxy, a new one will be fetched and stored in the cache.
        """
        headers = {'Authorization': api_key}
        response = requests.get(f"http://localhost:9000/get_proxy/{session_id}", headers=headers)
        response.raise_for_status()  # This will raise an error if the request fails.
        print(response.json())
        return response.json()  # Assuming your API returns proxy details in JSON format.
    
    


    def randomize_resolution(self):
        res_list = [(1920,1080), (1366,768), (1440,900), (1536,864), (2560,1440), (1680,1050), (1280,720), (1280,800), (1792,1120), (1600,900)]
        pick_resolution = random.choice(res_list)
        return pick_resolution
    # Add a port1 as argument later to handle the proxies
    def __init__(self, remote = False) -> None:
        #self.port1 = port1
        #self.randomize_width, self.randomize_height = self.randomize_resolution()
        self.options = Options()
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        #self.options.add_experimental_option("prefs", {
        #    "profile.default_content_setting_values.notifications": 2
        #})
        '''
        user_agent = RotateUserAgents()
        user_agent.get_useragents()
        user_agent_string = user_agent.choose_chrome()
        self.options.add_argument(f"user-agent={user_agent_string}")
        base_dir = os.path.dirname(os.path.realpath(__file__))
        user_data_dir = os.path.join(base_dir, 'browser_profiles')
        profiles = ProfilePool()
        fetch_profile = profiles.get_profile()
        self.options.add_argument(f'--user-data-dir={user_data_dir}')
        self.options.add_argument(f'profile-directory={fetch_profile}')
        '''
        #Put localhost in proxy_ip
        #Remember to add a check if the session id is in the cache
        
        #Remember this is where the flow described in the samsung notes points to. 
        #Remember to add the API key 
        '''
        self.proxy_info = self.get_proxy_info(self.session_id, os.environ.get('FLASK_API_KEY'))
        ip, port, username, password = self.proxy_info.values()
        
        '''
        #proxy = f'localhost:{self.port1}'
        #self.options.add_argument(f'--proxy-server={proxy}')

        if remote:
            self.driver = webdriver.Remote(
                command_executor='http://10.0.0.2:4444',
                options=self.options
            )

        else:
            
            self.driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=self.options)


        #self.driver.set_window_size(self.randomize_width, self.randomize_height)

    #Check this again it has to do with releiving the proxy from the cache once the session has ended
    def __enter__(self):
        return self

    def __exit__(self):
        self.driver.quit()

    def get_driver(self):
        return self.driver
    



agents = RotateUserAgents()
agents.get_useragents()