import functools
from selenium import webdriver
import selenium.common.exceptions as sce
from time import sleep
import os


class UEditorControl:
    def __init__(self, driver):
        self.driver = driver
        self.is_initialized = False
        self.ueditor_iframe = self.driver.find_element_by_id("ueditor_0")
        self.editor_body = self.driver.find_element_by_tag_name("body")

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
        self.driver.execute_script(f"arguments[0].innerHTML = ''", self.editor_body)
        self.is_initialized = True

    def inject_the_html(self, html):
        if not self.is_initialized:
            self.initialize()
        self.driver.execute_script(f"arguments[0].innerHTML += '{html}'", self.editor_body)

    @switcher
    def add_blank_line(self):
        blank_html = """<p><br></p>"""
        self.inject_the_html(blank_html)

    @switcher
    def add_follow_header(self):
        header_html = """<section style="white-space: normal;box-sizing: border-box;font-size: 16px;">\
                         <section style="margin-top: 10px;margin-bottom: 10px;box-sizing: border-box;">\
                         <section style="padding: 6px;display: inline-block;width: 578px;vertical-align: top;background-image: linear-gradient(90deg, rgb(235, 198, 159) 0%, rgb(246, 223, 195) 100%);border-width: 0px;border-radius: 5px;border-style: none;border-color: rgb(62, 62, 62);overflow: hidden;box-shadow: rgb(0, 0, 0) 0px 0px 0px;box-sizing: border-box;">\
                         <section style="box-sizing: border-box;"><section style="display: inline-block;width: 566px;vertical-align: top;background-image: linear-gradient(90deg, rgb(235, 198, 159) 0%, rgb(246, 223, 195) 100%);border-width: 1px;border-radius: 3px;border-style: solid;border-color: rgba(255, 243, 206, 0.45);overflow: hidden;box-shadow: rgba(213, 178, 122, 0.3) 0px 0px 15px inset;box-sizing: border-box;">\
                         <section style="padding-right: 10px;padding-left: 10px;color: rgb(132, 94, 34);font-size: 14px;letter-spacing: 2px;line-height: 1.6;box-sizing: border-box;">\
                         <p style="box-sizing: border-box;">点击\
                         <span style="font-size: 17px;box-sizing: border-box;"><strong style="box-sizing: border-box;">蓝字</strong></span>\
                         关注我们</p>\
                         </section></section></section></section></section></section>"""
        self.inject_the_html(header_html)
        # <mpchecktext contenteditable="false" id="1601800808780_0.8768842537050756"></mpchecktext>
        # This was after 关注我们 before </p>

    @switcher
    def add_click_title_notice(self):
        notice_html = """<section style="white-space: normal;box-sizing: border-box;font-size: 16px;">\
                         <section style="margin-top: 10px;margin-bottom: 10px;box-sizing: border-box;">\
                         <section style="display: flex;align-items: center;box-sizing: border-box;">\
                         <section style="flex: 1 1 auto;height: 2px;background-image: linear-gradient(270deg, rgb(213, 182, 123) 0%, rgba(213, 182, 123, 0) 100%);box-sizing: border-box;line-height: 0;"><br></section>\
                         <section style="flex: 0 0 auto;height: 10px;width: 10px;border-width: 2px;border-style: solid;border-color: rgb(213, 182, 123);transform: matrix(0.707, 0.707, -0.707, 0.707, 0, 0);box-sizing: border-box;line-height: 0;"><br></section>\
                         <section style="flex: 0 1 auto;box-sizing: border-box;">\
                         <section opera-tn-ra-cell="_$.pages:0.layers:0.comps:0.col1" style="padding-right: 15px;padding-left: 15px;box-sizing: border-box;">\
                         <section style="text-align: center;color: rgb(215, 175, 81);font-size: 19px;box-sizing: border-box;">\
                         <p style="box-sizing: border-box;"><strong style="box-sizing: border-box;">轻触标题阅读原文</strong></p>\
                         </section></section></section>\
                         <section style="flex: 0 0 auto;height: 10px;width: 10px;border-width: 2px;border-style: solid;border-color: rgb(213, 182, 123);transform: matrix(0.707, 0.707, -0.707, 0.707, 0, 0);box-sizing: border-box;line-height: 0;"><br></section>\
                         <section style="flex: 1 1 auto;height: 2px;transform: matrix(-1, 0, 0, 1, 0, 0);background-image: linear-gradient(270deg, rgb(213, 182, 123) 0%, rgba(213, 182, 123, 0) 100%);box-sizing: border-box;line-height: 0;"><span style="font-size: 15px;"></span><br></section>\
                         </section></section></section>\
                         <p><br></p>"""
        self.inject_the_html(notice_html)

    @switcher
    def add_one_news_for_weekly(self, title="这里是标题", title_url="https://mp.weixin.qq.com/", img_url="https://mmbiz.qpic.cn/mmbiz_jpg/NbdIoiaT5xuFPxDeYugXZ4n4sEq95FHMtibw1aE9KgWRcfQibGpyzdJriaY9QXXU7bWXleRyNteYC1E6TjTJu6e5jA/640?wx_fmt=jpeg", text="这里写正文吧"):
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

    def add_daily_news(self, title="标题", url="", img_url="", text="这里应该有个内容"):
        self.add_follow_header()
        for i in range(5):
            self.add_blank_line()
        self.add_end_qr()

    @switcher
    def add_before_weeklies_title(self):
        before_html = """<section style="white-space: normal;box-sizing: border-box;font-size: 16px;">\
                         <section style="margin-top: 10px;margin-bottom: 10px;text-align: center;box-sizing: border-box;">\
                         <section style="display: inline-block;vertical-align: middle;width: 100px;box-sizing: border-box;">\
                         <section style="margin-top: 15px;margin-bottom: 15px;box-sizing: border-box;">\
                         <section style="border-top: 1px dotted rgb(62, 62, 62);box-sizing: border-box;height: 1px;line-height: 0;">\
                         </section></section></section>\
                         <section style="display: inline-block;vertical-align: middle;width: 330px;box-sizing: border-box;">\
                         <section style="box-sizing: border-box;">\
                         <section style="margin-top: 7px;margin-bottom: 7px;display: inline-block;line-height: 1.2;background-color: rgb(249, 110, 87);box-sizing: border-box;">\
                         <section style="margin: -7px 5px;padding: 2px 8px;display: inline-block;vertical-align: top;border-width: 2px;border-style: solid;border-color: rgb(249, 110, 87);background-color: rgb(248, 110, 87);font-size: 20px;letter-spacing: 1.5px;line-height: 2;color: rgb(255, 255, 255);box-sizing: border-box;">\
                         <p style="box-sizing: border-box;">点击链接，进入一周速览</p>\
                         </section></section></section></section>\
                         <section style="display: inline-block;vertical-align: middle;width: 100px;box-sizing: border-box;">\
                         <section style="margin-top: 15px;margin-bottom: 15px;box-sizing: border-box;">\
                         <section style="border-top: 1px dotted rgb(62, 62, 62);box-sizing: border-box;height: 1px;line-height: 0;">\
                         </section></section></section></section></section>\
                         <p><br></p>\
                         <p><br></p>\
                         <p><br></p>"""
        self.inject_the_html(before_html)

    @switcher
    def add_end_qr(self):
        qr_html = """<section style="white-space: normal;box-sizing: border-box;font-size: 16px;">\
                     <section style="margin-top: 10px;margin-bottom: 10px;box-sizing: border-box;">\
                     <section style="display: inline-block;width: 578px;vertical-align: top;background-position: 0% 0%;background-repeat: repeat-y;background-size: 100%;background-attachment: scroll;border-width: 0px;border-radius: 1px;border-style: none;border-color: rgb(62, 62, 62);overflow: hidden;background-image: url(&quot;https://mmbiz.qpic.cn/mmbiz_jpg/NbdIoiaT5xuFPxDeYugXZ4n4sEq95FHMtlG9f3UBEsbY7uyj3ASOIEWedWGmapPdVibFkjFRmyskR3wFq8O1YIVg/640?wx_fmt=jpeg&quot;);box-sizing: border-box;">\
                     <section style="margin-bottom: -5px;text-align: center;opacity: 0.99;box-sizing: border-box;">\
                     <section style="max-width: 100%;vertical-align: middle;display: inline-block;line-height: 0;box-sizing: border-box;">\
                     <img data-ratio="0.0933707" src="https://mmbiz.qpic.cn/mmbiz_png/NbdIoiaT5xuFPxDeYugXZ4n4sEq95FHMtjz7dWfpcLmowFoCjurIKAhnJyTJHbeJNTkthh5vzgCGur3ZnZ2bP6w/640?wx_fmt=png" data-type="png" data-w="1071" style="vertical-align: middle;box-sizing: border-box;">\
                     </section></section>\
                     <section style="margin-top: -40px;text-align: center;box-sizing: border-box;">\
                     <section style="display: inline-block;width: 156.05px;vertical-align: top;height: auto;background-color: rgb(165, 118, 74);box-sizing: border-box;">\
                     <section style="box-sizing: border-box;">\
                     <section style="display: inline-block;width: 140.438px;vertical-align: top;height: auto;background-color: rgb(255, 255, 255);box-sizing: border-box;">\
                     <section style="margin-top: 30px;box-sizing: border-box;">\
                     <section style="max-width: 100%;vertical-align: middle;display: inline-block;line-height: 0;box-sizing: border-box;">\
                     <img data-cropselx1="0" data-cropselx2="141" data-cropsely1="0" data-cropsely2="141" data-ratio="1" src="https://mmbiz.qpic.cn/mmbiz_jpg/NbdIoiaT5xuFPxDeYugXZ4n4sEq95FHMtibw1aE9KgWRcfQibGpyzdJriaY9QXXU7bWXleRyNteYC1E6TjTJu6e5jA/640?wx_fmt=jpeg" data-type="jpeg" data-w="258" style="height: 141px;vertical-align: middle;box-sizing: border-box;width: 141px;">\
                     </section></section></section></section></section></section>\
                     <section style="box-sizing: border-box;">\
                     <section style="display: inline-block;width: 578px;vertical-align: top;line-height: 0;box-sizing: border-box;">\
                     <section style="text-align: center;box-sizing: border-box;">\
                     <section style="max-width: 100%;vertical-align: middle;display: inline-block;line-height: 0;width: 156.05px;height: auto;box-sizing: border-box;">\
                     <img data-ratio="0.2179104" src="https://mmbiz.qpic.cn/mmbiz_png/NbdIoiaT5xuFPxDeYugXZ4n4sEq95FHMt3HE7YL7lHZfMric2dwpxAR1WCiaQTs4IEbX1fqXAkeBHgicVspKziaPicjw/640?wx_fmt=png" data-type="png" data-w="335" style="vertical-align: middle;width: 156.05px;box-sizing: border-box;">\
                     </section></section></section></section>\
                     <section style="box-sizing: border-box;">\
                     <section style="padding-right: 20px;padding-left: 20px;text-align: center;color: rgb(73, 33, 0);font-size: 12px;letter-spacing: 1px;box-sizing: border-box;">\
                     <p style="box-sizing: border-box;">实时土耳其公众号</p>\
                     <p style="box-sizing: border-box;">微信号 : shishituerqi</p>\
                     <p style="box-sizing: border-box;"><strong style="box-sizing: border-box;">\
                     <span style="font-size: 15px;box-sizing: border-box;">▇&nbsp;扫码关注我们\
                     </span></strong></p></section></section>\
                     <section style="margin-top: -10px;text-align: center;opacity: 0.99;box-sizing: border-box;">\
                     <section style="max-width: 100%;vertical-align: middle;display: inline-block;line-height: 0;box-sizing: border-box;">\
                     <img data-ratio="0.1064426" src="https://mmbiz.qpic.cn/mmbiz_png/NbdIoiaT5xuFPxDeYugXZ4n4sEq95FHMtta3wlyfEiclnLPyJopqibic3QEoClGASrkX1Lka2b8rmCz1WJNXnicbRew/640?wx_fmt=png" data-type="png" data-w="1071" style="vertical-align: middle;box-sizing: border-box;">\
                     </section></section>\
                     </section></section></section>"""
        self.inject_the_html(qr_html)


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    try:
        driver = webdriver.Chrome(options=options)
    except sce.SessionNotCreatedException:
        print("Please download newer version of ChromeDriver!")

    driver.get("https://coderliguoqing.github.io/ueditor-web/dist/#/ueditor")
    sleep(3)
    UE = UEditorControl(driver)
    try:
        UE.add_follow_header()
    finally:
        os.system("pause")
        UE.driver.quit()
