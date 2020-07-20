from selenium import webdriver
from time import sleep
import re


class Translator:
    def __init__(self):
        self.driver = self.open_browser()

    def open_browser(self):
        """
        # options for headless Chrome instance that passes automation detection
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--window-size=1280x800')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(options=options)

        # cdp_cmd executions to stop websites from automation detection
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
        # Object.defineProperty(navigator, 'webdriver', {
        #   get: () => undefined
        # })

        """
        })
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "browser1"}})
        """
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")

        driver = webdriver.Chrome(options=options)
        sleep(3)

        return driver

    def close_driver(self):
        self.driver.quit()

    def parse_link(self):
        websites = ['reuters', 'apnews', 'aljazeera', 'ahvalnews', 'turkishminute',
                    'duvarenglish', 'aa', 'hurriyetdailynews', 'dailysabah']

        # TODO We need to add other news agencies for the headers and the bodies
        # TODO Maybe using beautiful soup will easily solve this XPath mess, gotta check that, because these two uses h1 for headers, and p for bodies
        headers = {'ahvalnews': '//*[@id="mm-0"]/div[2]/div[3]/div/section/div/div/div[3]/div[1]/h1',
                   'turkishminute': '//article/div[1]/header/h1'}

        bodies = {'ahvalnews': '//*[@id="mm-0"]/div[2]/div[3]/div/section/div/div/div[3]/div[3]/div[1]/div/div/p',
                  'turkishminute': '//article/div[3]/p'}
        for news_outlet in websites:
            if re.search(news_outlet, self.link):
                header = self.driver.find_element_by_xpath(headers[news_outlet]).text
                body = self.driver.find_elements_by_xpath(bodies[news_outlet])
                body = '\n\n'.join([item.text for item in body])
                print(header)
                print(body)
                print('\n','-'* 50,'\n')


    #TODO We got header and body, we need to implement sougou translation here.

    def translate(self, link):
        self.link = link
        self.driver.get(self.link)
        sleep(3)
        self.parse_link()

# trs = Translator()
