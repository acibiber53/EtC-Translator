from selenium import webdriver
from time import sleep
from datetime import date
import re
from docx import Document
import os

class Translator:
    def open_output_file(self):
        self.outputfile = Document()
        self.outputfile_name = str(date.today()) + '.docx'
        if os.path.exists(self.outputfile_name):
            os.remove(self.outputfile_name)
        self.outputfile.save(self.outputfile_name)

    def __init__(self):
        self.driver = self.open_browser()
        self.translator = self.open_browser()
        self.translator.get('https://fanyi.sogou.com/')
        self.open_output_file()

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
        self.translator.quit()

    def parse_link(self):
        websites = ['reuters', 'apnews', 'aljazeera', 'ahvalnews', 'turkishminute',
                    'duvarenglish', 'aa', 'hurriyetdailynews', 'dailysabah']

        # TODO We need to add other news agencies for the headers and the bodies
        # TODO Maybe using beautiful soup will easily solve this XPath mess, gotta check that, because these two uses h1 for headers, and p for bodies
        headers = {'reuters':'//*[@id="USKCN24J0M1"]/div[1]/div[1]/div/div/div[1]/div/h1','ahvalnews': '//*[@id="mm-0"]/div[2]/div[3]/div/section/div/div/div[3]/div[1]/h1',
                   'turkishminute': '//article/div[1]/header/h1'}

        bodies = {'ahvalnews': '//*[@id="mm-0"]/div[2]/div[3]/div/section/div/div/div[3]/div[3]/div[1]/div/div/p',
                  'turkishminute': '//article/div[3]/p'}
        for news_outlet in websites:
            if re.search(news_outlet, self.link):
                header = self.driver.find_element_by_xpath(headers[news_outlet]).text
                body = self.driver.find_elements_by_xpath(bodies[news_outlet])
                body = '\n'.join([item.text for item in body])
                self.translate_write(header, body)

        self.outputfile.save(self.outputfile_name)

    def translate_write(self, header, body):
        self.outputfile.add_heading(header)

        fulltext = header + '\n' + body

        # Finding the input element and sending the text in
        stinput = self.translator.find_element_by_id("trans-input")
        stinput.send_keys(fulltext)
        sleep(3)

        # Finding the output element
        stoutput = self.translator.find_element_by_class_name("output")

        # Sending the text paragraph by paragraph
        parcre = stoutput.text.split('\n')

        for string in parcre:
            self.outputfile.add_paragraph(string)

        # Cleaning the text area for next translation
        stinput.clear()

        self.outputfile.add_paragraph(self.driver.current_url + '\n')

    def translate(self, link):
        self.link = link
        self.driver.get(self.link)
        sleep(3)
        self.parse_link()

# trs = Translator()
