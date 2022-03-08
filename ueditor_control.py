import functools
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import selenium.common.exceptions as sce
from time import sleep
import os
import wechat_html_templates


class UEditorControl:
    def __init__(self, driver):
        self.driver = driver
        self.is_initialized = False
        self.ueditor_iframe = self.driver.find_element_by_id("ueditor_0")
        self.iframe_body = None  # We need to find body in the iframe after switching to the iframe. Otherwise we
        # can't use it. Iframes are different content than whole page, and to use them you need to switch first.

    def switcher(func):
        """
        This decorator switches to the ueditor iframe,
        then does the function,
        then switches out to the default content.
        """

        @functools.wraps(func)
        def wrapper_decorator(self, *args, **kwargs):
            self.driver.switch_to.frame(self.ueditor_iframe)
            value = func(self, *args, **kwargs)
            self.driver.switch_to.default_content()
            return value

        return wrapper_decorator

    def initialize(self):
        self.iframe_body = self.driver.find_element_by_tag_name("body")
        self.driver.execute_script(f"arguments[0].innerHTML = ''", self.iframe_body)
        self.is_initialized = True

    def inject_the_html(self, html):
        if not self.is_initialized:
            self.initialize()
        self.iframe_body = self.driver.find_element_by_tag_name("body")
        self.driver.execute_script(
            f"arguments[0].innerHTML += '{html}'", self.iframe_body
        )

    @switcher
    def add_blank_line(self):
        blank_html = """<p><br></p>"""
        self.inject_the_html(blank_html)

    @switcher
    def add_a_paragraph(self, text="Test"):
        paragraph_html = f"<p>{text}</p>"
        self.inject_the_html(paragraph_html)

    @switcher
    def add_an_image(
        self,
        img_url="https://mmbiz.qpic.cn/mmbiz_jpg/NbdIoiaT5xuFPxDeYugXZ4n4sEq95FHMtibw1aE9KgWRcfQibGpyzdJriaY9QXXU7bWXleRyNteYC1E6TjTJu6e5jA/640?wx_fmt=jpeg",
    ):
        img_html = f"""<p style="text-align: center">\
                       <img data-s="300,640" data-galleryid="" data-type="jpeg" class="rich_pages" src={img_url} style="" data-ratio="0.6104815864022662" data-w="706" data-imgqrcoded="1">\
                       </p>"""
        self.inject_the_html(img_html)

    @switcher
    def add_follow_header(self):
        self.inject_the_html(wechat_html_templates.header_html)
        # <mpchecktext contenteditable="false" id="1601800808780_0.8768842537050756"></mpchecktext>
        # This was after 关注我们 before </p>

    @switcher
    def add_click_title_notice(self):
        self.inject_the_html(wechat_html_templates.notice_html)

    @switcher
    def add_one_news_for_weekly(
        self,
        title="这里是标题",
        title_url="https://mp.weixin.qq.com/",
        img_url="https://mmbiz.qpic.cn/mmbiz_jpg/NbdIoiaT5xuFPxDeYugXZ4n4sEq95FHMtibw1aE9KgWRcfQibGpyzdJriaY9QXXU7bWXleRyNteYC1E6TjTJu6e5jA/640?wx_fmt=jpeg",
        text="这里写正文吧",
    ):
        one_news_for_weekly_html = f"""<section style="margin-top: 10px;white-space: normal;font-size: 16px;text-align: center;box-sizing: border-box;">\
                                     <section style="padding: 10px;display: inline-block;width: 491.292px;vertical-align: top;border-style: solid solid none;border-width: 1px;border-radius: 0px;border-color: rgb(62, 62, 62);box-sizing: border-box;">\
                                     <section style="margin-top: 10px;margin-bottom: 10px;box-sizing: border-box;">\
                                     <img data-cropselx1="0" data-cropselx2="469" data-cropsely1="0" data-cropsely2="215" data-ratio="1" src="{img_url}" data-type="jpeg" data-w="258" style="height: 469px;vertical-align: middle;box-sizing: border-box;width: 469px;">\
                                     </section></section></section>\
                                     <section style="white-space: normal;box-sizing: border-box;font-size: 16px;text-align: center;">\
                                     <section style="padding: 5px 10px;display: inline-block;width: 578px;background-color: rgb(255, 243, 224);vertical-align: middle;align-self: center;box-sizing: border-box;">\
                                     <section style="text-align: center;font-size: 20px;color: rgb(0, 0, 0);box-sizing: border-box;">\
                                     <p style="box-sizing: border-box;">\
                                     <a target="_blank" href="{title_url}" textvalue="{title}" data-itemshowtype="0" tab="innerlink">\
                                     <span style="text-decoration: underline;">{title}</span>\
                                     </a></p></section></section>\
                                     <section style="margin-bottom: 10px;text-align: center;box-sizing: border-box;">\
                                     <section style="padding: 10px;display: inline-block;width: 491.295px;vertical-align: top;border-style: none solid solid;border-width: 1px;border-radius: 0px;border-color: rgb(62, 62, 62);box-sizing: border-box;">\
                                     <section style="margin-bottom: 10px;box-sizing: border-box;">\
                                     <section style="text-align: justify;font-size: 15px;line-height: 1.8;box-sizing: border-box;">\
                                     <p style="box-sizing: border-box;">{text}</p>\
                                     </section></section></section></section></section>"""
        self.inject_the_html(one_news_for_weekly_html)

    def add_daily_news(self, img_url="", text=["这里应该有个内容", "里面会有一些新闻"]):
        self.add_follow_header()
        self.add_blank_line()
        self.add_an_image(img_url)
        sleep(0.5)
        for par in text:
            self.add_blank_line()
            self.add_a_paragraph(par)
            sleep(0.5)
        self.add_blank_line()
        self.add_end_qr()
        sleep(0.5)

    @switcher
    def add_before_weeklies_title(self):
        self.inject_the_html(wechat_html_templates.before_html)

    @switcher
    def add_end_qr(self):
        self.inject_the_html(wechat_html_templates.qr_html)


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("start-maximized")

    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    except sce.SessionNotCreatedException as error:
        print(error)
        os.system("pause")
    sleep(1)

    driver.get("https://coderliguoqing.github.io/ueditor-web/dist/#/ueditor")
    sleep(3)
    UE = UEditorControl(driver)
    try:
        UE.add_daily_news()
    finally:
        os.system("pause")
        UE.driver.quit()
