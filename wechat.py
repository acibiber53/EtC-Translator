from selenium import webdriver
import selenium.common.exceptions as sce
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from datetime import date, timedelta
import pandas as pd
from openpyxl import load_workbook
from ueditor_control import UEditorControl
from webdriver_manager.chrome import ChromeDriverManager
import re
import os


class Wechat:
    """
    Source for decorators with arguments:
    https://stackoverflow.com/questions/5929107/decorators-with-parameters?noredirect=1&lq=1
    """
    def sleeper(argument):
        def decorator(function):
            def wrapper(*args, **kwargs):
                result = function(*args, **kwargs)
                sleep(argument)
                return result

            return wrapper

        return decorator

    def __init__(self):
        self.driver = None
        self.main_handle = None
        self.text_editor_handle = None
        self.news_info = self.read_links()
        self.is_logged_in = False
        self.time_tag = self.make_time_for_history()
        self.system_started = False
        self.ueditor = None

    def start_the_system(self):
        """
            UI Drawing requires this method. I initially open the browser when I create an instance of Wechat. When I
            create the instance of Wechat before drawing UI, it opens and makes you wait. This method will require
            additional click to initialize the Wechat instance.
        :return:
        """
        self.driver = self.open_browser()
        self.driver.get("https://mp.weixin.qq.com/")
        self.main_handle = self.driver.current_window_handle
        self.text_editor_handle = None
        sleep(3)
        self.open_submit()
        self.system_started = True

    @staticmethod
    def make_time_for_history():
        """
            We collect weekly data, from last sunday till yesterday--saturday, both included. This method create that
            time tag for the historical data preservation.
        :return:  string : "one_week-ago - yesterday"
        """
        yesterday = date.today() - timedelta(days=1)
        one_week_ago = str(yesterday - timedelta(days=6))
        yesterday = str(yesterday)
        return one_week_ago + ' - ' + yesterday

    @staticmethod
    @sleeper(1)
    def open_browser():
        """
        This method opens a Chrome webdriver
        :return: webdriver
        """
        # TODO Use a package manager for ChromeDriver
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        return driver

    @sleeper(2)
    def open_submit(self):
        # Sometimes the website opens QR login, this is to change it into username-password login
        try:
            if EC.presence_of_element_located((By.LINK_TEXT, "使用帐号登录"))(self.driver):
                try:
                    self.driver.find_element_by_link_text("使用帐号登录").click()
                except sce.ElementClickInterceptedException:
                    print(
                        "There is something on the place we need to click. Please make it clickable!"
                    )
        except sce.NoSuchElementException:
            print("Maybe page is not open yet?")

    @sleeper(2)
    def enter_to_wechat(self):
        """
        This method reads the username and password from a userpass.txt file and opens related wechat account. After
        entering username and password, it also waits one minute for user to scan QR code.
        :return:
        """
        if self.sys_start_check():
            return

        with open("Creds/userpass.txt") as f:
            name = f.readline().strip()
            passw = f.readline().strip()

        self.driver.find_element_by_name("account").send_keys(name)
        self.driver.find_element_by_name("password").send_keys(passw)

        self.driver.find_element_by_link_text("登录").click()

        print("Scan the QR code please! You have 1 minute. ")
        # Wait until QR scan
        try:
            wait_elem = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "weui-desktop-panel__hd"))
            )
        except sce.TimeoutException:
            print("You've failed to login in time, try again!")
            self.close_browser()
            return

        self.is_logged_in = True
        print("QR Code Scanned!!!")

    @sleeper(1)
    def get_news_links(self):
        if self.sys_start_check():
            return

        if self.log_check():
            return

        days = self.driver.find_elements_by_xpath("//ul[@id='list']/li")[::-1]
        all_news = list()
        i = 0
        for day in days:
            new = day.find_elements_by_xpath("div[2]/div/div[2]/a")
            for n in new:
                if re.search("土耳其新闻一周速览", n.text):
                    print("Weekly news has been removed from the news link!")
                    continue
                i += 1
                all_news.append([i, n.text, n.get_attribute("href")])

        self.news_info = pd.DataFrame(all_news, columns=["ID", "标题", "链接"])

    @sleeper(1)
    def title_image_text_extract(self):
        def abstract_preparer(pd_data):
            return ['\n'.join(elem.split('\n')[0:2]) for elem in pd_data]

        images = list()
        texts = list()

        for index, news_link in enumerate(self.news_info["链接"]):
            print(f"Extracting news no {index+1}. Link for it is this:\n{news_link}\n")
            self.driver.get(news_link)
            sleep(3)
            try:
                image = self.driver.find_element_by_class_name("rich_pages")
            except sce.NoSuchElementException as error:
                print(error)
                print("Couldn't find the image, so passing this one!")
                print(news_link)
                images.append("None found!")
                texts.append("None found!")
                continue
            content = self.driver.find_elements_by_xpath("//p")
            content = content[5:-9]  # beginning and endings removed
            res = list()
            for line in content:
                if line.text.strip():  # Skip the empty lines
                    res.append(line.text.strip())
            parag = "\n".join(res)
            """
            content = self.driver.find_elements_by_xpath(
                "//*[@id='js_content']/section/section[2]/p"
            )
            if not content:
                content = self.driver.find_elements_by_xpath(
                    "//*[@id='js_content']/section[2]/p"
                )
            if not content:
                content = self.driver.find_elements_by_xpath(
                    "//*[@id='js_content']/p"
                )
            """
            images.append(image.get_attribute("src"))
            texts.append(parag)

        self.news_info["图片链接"] = images
        self.news_info["正文"] = texts
        self.news_info["摘要"] = abstract_preparer(self.news_info["正文"])
        self.print_links()

    @sleeper(3)
    def open_text_editor_from_home(self):
        if self.sys_start_check():
            return

        if self.log_check():
            return
        try:
            text_editor = self.driver.find_element_by_xpath("//div[@class='new-creation__menu']/div[1]")
        except sce.NoSuchElementException:
            self.driver.get("https://mp.weixin.qq.com/")
            wait_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "weui-desktop-panel__hd")))
            text_editor = self.driver.find_element_by_xpath("//div[@class='new-creation__menu']/div[1]")

        text_editor.click()
        self.text_editor_handle = self.driver.window_handles[-1]
        self.driver.switch_to.window(self.text_editor_handle)
        wait_elem = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "js_plugins_list")))

        self.ueditor = UEditorControl(self.driver)
        print("Text Editor fully opened!")

    @sleeper(1)
    def add_weekly_news(self):
        self.ueditor.add_follow_header()
        self.ueditor.add_click_title_notice()
        for row in zip(self.news_info['标题'], self.news_info['链接'], self.news_info['图片链接'], self.news_info['摘要']):
            self.ueditor.add_one_news_for_weekly(row[0], row[1], row[2], ''.join(row[3].split()))
        self.ueditor.add_before_weeklies_title()
        self.ueditor.add_end_qr()
        self.save()

    @sleeper(1)
    def daily_news_adder(self, title="", url="", img_url="", text="", abstract="", author="实时土耳其"):
        try:
            title_element = self.driver.find_element_by_xpath("//textarea[@id='title']")
            title_element.send_keys(title)
        except Exception as error:
            print(error)
            print("Title place couldn't been found!")
        try:
            author_element = self.driver.find_element_by_xpath("//input[@id='author']")
            author_element.send_keys(author)
        except Exception as error:
            print(error)
            print("Author place couldn't been found!")
        self.ueditor.add_daily_news(img_url, text)
        try:
            abstract_element = self.driver.find_element_by_id("js_description")
            abstract_element.send_keys(abstract)
        except Exception as error:
            print(error)
            print("Abstract element couldn't been found!")

    @sleeper(1)
    def open_next_news(self):
        """
            It opens the next content page in the main Wechat editor. Hovering is required to open the "next content"
            button.
            Resources:
            https://www.geeksforgeeks.org/action-chains-in-selenium-python/
        """

        element_to_hover_over = self.driver.find_element_by_id("js_add_appmsg")
        hover_action = ActionChains(self.driver).move_to_element(element_to_hover_over)
        hover_action.perform()
        print("Hovered over")
        sleep(1)
        element_to_click = self.driver.find_element_by_xpath("//li[@title='写新图文']/a")
        click_action = ActionChains(self.driver).click(element_to_click)
        click_action.perform()
        print("Clicked")

    @sleeper(2)
    def save(self):
        save_element = self.driver.find_element_by_id("js_submit")
        save_element.click()

    @sleeper(1)
    def print_links(self):
        filename = "weekly_news_info.xlsx"
        self.news_info.to_excel(filename, index=False, sheet_name=self.time_tag)
        print(f"All the data printed into {filename}")
        self.log_news()

    @sleeper(1)
    def log_news(self):
        """
            This function logs every weeks news into new sheet at a document called historical_news_data.xlsx

        :return: None
        """
        filename = 'historical_news_data.xlsx'
        book = load_workbook(filename)
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            writer.book = book
            writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
            self.news_info.to_excel(writer, sheet_name=self.time_tag)
            writer.save()
        print("Long term data recording completed")

    @sleeper(1)
    def read_links(self, pathe="weekly_news_info.xlsx"):
        if os.path.exists(pathe):
            self.news_info = pd.read_excel(pathe)
            print(self.news_info)
            return self.news_info
        else:
            print("You need to get news links first!")
            return

    def log_check(self):
        if not self.is_logged_in:
            print("Please login first and try again")
            return True
        return False

    def sys_start_check(self):
        if not self.system_started:
            print("Please start the system first and try again")
            return True
        return False

    def close_browser(self):
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    pass
