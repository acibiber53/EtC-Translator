"""
How to create exe file from this script
On terminal write this.
pyinstaller main.py -n EtC-translator-v0.99 --onefile --distpath EtC-translator-for-all-v0.99 --add-data "venv/Lib/site-packages/google_api_python_client-1.12.8.dist-info;google_api_python_client-1.12.8.dist-info" --add-data "Creds;Creds"
pyinstaller should be installed beforehand. It is the main executable maker.
main.py is the entrance point for the project.
-n is for name
--onefile reduces everything into one exe file
--distpath creates the file into desired directory
X in vX shows the version.
--debug=all is for debugging purposes. Add if needed.
--add-data source_path;dest_path -> This one is required because we are using Google API. This API uses
google-api-python-client. We need to find its path, write it, then put that file into the package.

After making the exe file, one other file should be put into same directory:
1- news-to-translate.htm. This should be made daily.


"""

from credentials import trello_upload_board_id
from translating_engine import Translator, htm_to_urllist
from gdapi_controller import GoogleDriveAPIController as GDAPIC
from trello_controller import TrelloController
from wechat import Wechat
from wordpress import WordpressController as WPC
import time
import os
import PySimpleGUI as sg
import re
from newsapi_controller import NewsAPIController
from uploading_engine import UploadingEngine
import datetime
import threading

DOC_PATH = os.path.expanduser("~\Downloads\exported-bookmarks.html")
WIDTH = 1024
HEIGHT = 768
PADDING = 20


class EtcTranslatorForAll:
    def __init__(self):
        # Translation variables
        self.url_title_list, self.url_list = htm_to_urllist(
            DOC_PATH
        )
        self.translation_engine = "sogou"
        self.gdapi = self.trs = self.trel = self.upen = None

        # GUI variables
        self.main_window_name = "EtC Translator for all"

        # News selection variables
        self.nac = None
        self.table_data = None
        self.daily_news_selection_list = None

        # Layouts needed
        self.welcome_layout = (
            self.news_selection_layout
        ) = (
            self.translation_layout_before
        ) = (
            self.translation_layout_during
        ) = (
            self.sunday_collector_layout
        ) = self.working_window_layout = self.upload_layout = None

        self.set_layouts()
        self.window = self.current_visible = self.print = None

        # Uploading variables
        self.upload_news_list = list()
        self.wc = None
        self.number_of_news_to_upload = 0

    def set_layouts(self):
        def sidebar_maker():
            return [
                [sg.Text("Menu")],
                [sg.HSeparator()],
                [sg.Button("News Feed", key="-NEWS FEED SBB-")],
                [sg.Button("Translator", key="-TRANSLATOR SBB-")],
                [sg.Button("Sunday Collector", key="-SUNDAY COL SBB-")],
                [sg.Button("Uploader", key="-UPLOADER SBB-")],
                [sg.Button("Settings", key="-SETTINGS SBB-")],
                [sg.Button("Exit", key="-EXIT-")],
            ]

        # Title maker for main working column
        def title_maker(title):
            return ([sg.Text(f"{title}", justification="right")], [sg.HSeparator()])

        # Different layouts for main working window
        # Opening Layout
        self.welcome_layout = [
            *title_maker(self.main_window_name),
            [
                sg.Text(
                    "Welcome to this beautiful app! Thank you for your endless support!",
                    justification="center",
                )
            ],
        ]

        empty_list = [["This is a placeholder for a title of a news.", "This is their Source"], ["", ""]]
        self.news_selection_layout = [
            *title_maker("Translator"),
            [sg.Text("News list for selection")],
            [
                sg.Table(
                    values=empty_list,
                    headings=["Title", "Source"],
                    justification="left",
                    # vertical_scroll_only=True,
                    enable_events=True,
                    num_rows=15,
                    def_col_width=100,
                    # auto_size_columns=True,
                    col_widths=[100, 15],
                    select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                    key="-NEWS SELECTION TABLE-",
                )
            ],
            [sg.Button("Save", key="-SELECTION COMPLETE-")],
        ]

        # Translation Layout Before
        self.translation_layout_before = [
            *title_maker("Translator"),
            [sg.Text("News list for translation")],
            [
                sg.Listbox(
                    values=empty_list[0],
                    enable_events=True,
                    size=(100, 15),
                    key="-NEWS LIST-",
                )
            ],
            # [sg.Text(f"Translation engine being used : {self.translation_engine}")],
            [
                sg.Radio("Sogou", "RADIO2", key="-SOGOU-", default=True),
                sg.Radio("Baidu", "RADIO2", key="-BAIDU-"),
            ],
            [sg.Button("Start Translating", key="-TRANSLATE BUTTON-")],
        ]

        # Translation Layout During
        self.translation_layout_during = [
            *title_maker("Translator"),
            [sg.Text("News are being translated now!")],
            [
                sg.Multiline(
                    default_text="Currently translating news info will show here",
                    size=(100, 10),
                    key="-NEWS INFO-",
                    write_only=True,
                    auto_refresh=True,
                )
            ],
            [
                sg.ProgressBar(
                    max_value=5,
                    size=(70, 25),
                    key="-PROG-",
                    pad=((0, 0), (15, 15)),
                )
            ],
        ]

        # TODO Translation Layout After

        # Sunday Collector Layout
        self.sunday_collector_layout = [
            *title_maker("Sunday Collector"),
            [sg.Text("Select the mode for sunday collector to work:")],
            [
                sg.Radio(
                    "Just weekly news", "RADIO1", key="-JUST WEEKLY-", default=True
                ),
                sg.Radio("With daily news", "RADIO1", key="-WITH DAILY-"),
            ],
            [sg.Button("Start Fetching", key="-SCOL FETCH BUTTON-")],
        ]

        # Uploading Layout
        self.upload_layout = [
            *title_maker("Uploader"),
            [sg.Text("Select upload Medium:")],
            [sg.Checkbox("Wechat", default=True, key="-WECHAT UPLOAD-")],
            [sg.Checkbox("WordPress", default=False, key="-WORDPRESS UPLOAD-")],
            [sg.Text("Selecting only WordPress will get the news from '在上传 - 只WP' list, any other selection will get "
                     "the news from '在上传'.")],
            [sg.Button("Show Upload Content", key="-UPLOAD REFRESH-")],
            [sg.Text("News Titles to upload:")],
            [
                sg.Multiline(
                    size=(80, 10),
                    key="-UPLOAD INFO-",
                    write_only=True,
                    auto_refresh=True,
                )
            ],

            [sg.Button("Start Uploading", key="-UPLOAD BUTTON-")],
        ]

        # Main working window layout
        SIDEBAR_WIDTH = int(WIDTH/4-PADDING)
        REST_WIDTH = int((WIDTH/4)*3-PADDING)
        REAL_HEIGHT = int(HEIGHT-3*PADDING)
        self.working_window_layout = [
            [
                sg.Column(layout=sidebar_maker(), size=(SIDEBAR_WIDTH, REAL_HEIGHT)),
                sg.VSeparator(),
                sg.Column(layout=self.welcome_layout, size=(REST_WIDTH, REAL_HEIGHT), key="-WELCOME-"),
                sg.Column(
                    layout=self.news_selection_layout,
                    size=(REST_WIDTH, REAL_HEIGHT),
                    key="-NEWS SELECTION-",
                    visible=False,
                ),
                sg.Column(
                    layout=self.translation_layout_before,
                    size=(REST_WIDTH, REAL_HEIGHT),
                    key="-TRANSLATOR BEFORE-",
                    visible=False,
                ),
                sg.Column(
                    layout=self.translation_layout_during,
                    size=(REST_WIDTH, REAL_HEIGHT),
                    key="-TRANSLATOR DURING-",
                    visible=False,
                ),
                sg.Column(
                    layout=self.sunday_collector_layout,
                    size=(REST_WIDTH, REAL_HEIGHT),
                    key="-SUNDAY COLLECTOR-",
                    visible=False,
                ),
                sg.Column(
                    layout=self.upload_layout,
                    size=(REST_WIDTH, REAL_HEIGHT),
                    key="-UPLOADER PAGE-",
                    visible=False,
                ),
            ]
        ]

    def print_set(self, multiline_key):
        def mprint(*args, **kwargs):
            self.window[multiline_key].print(*args, **kwargs)

        return mprint

    def change_layout(self, target):
        self.window[self.current_visible].update(visible=False)
        self.window[target].update(visible=True)
        self.current_visible = target

    def create_card_with_trello(self, news):
        self.print("Creating Trello card at 准备中 list!")
        desc = f"[{news.title_english}]({news.source_link})"
        response = self.trel.create_card_then_attach_link(
            name=news.title_english, desc=desc, url_source=news.google_upload_link
        )
        self.print(f"Trello card created!\nCard Link:{response.get('url')}\n")

    def upload_daily_news_to_trello(self, trello_daily_card, date):
        self.print("Adding daily news list to the 新闻列表 list！")
        daily_card_desc = "\n".join(
            [f"[{elem[0]}]({elem[1]})" for elem in trello_daily_card]
        )
        self.trel.target_list = self.trel.get_target_list("新闻列表")
        response = self.trel.create_a_card(name=date, desc=daily_card_desc, due="")
        self.print(
            f"Trello daily news list card created!\nCard Link:{response.get('url')}\n"
        )

    def translate_news(self, t_engine):
        if self.url_list == -1:
            return

        self.trs = Translator(t_engine)
        self.trel = TrelloController()
        trello_daily_card = list()

        try:
            for index, link in enumerate(self.url_list):
                start_time = time.time()
                self.print(f"Translation begins for {link}")
                self.trs.translate_main(link)
                self.print(
                    f"Translation ends, it took {time.time() - start_time} seconds.\n"
                )

                trello_daily_card.append(
                    (
                        self.trs.current_news.title_english,
                        self.trs.current_news.source_link,
                    )
                )

                self.print("Uploading to Google Drive!")
                (
                    news_title,
                    self.trs.current_news.google_upload_link,
                ) = self.gdapi.docx_to_gdocs_uploader(
                    self.trs.current_news.document_name,
                    self.trs.current_news.document_path,
                )
                self.print(
                    f"Uploaded!\nFile Name: {news_title}\nFile URL: {self.trs.current_news.google_upload_link}\n"
                )

                self.create_card_with_trello(self.trs.current_news)
                self.window["-PROG-"].update(index + 1)

        except Exception as error:
            sg.popup_error(error)

        finally:
            self.upload_daily_news_to_trello(
                trello_daily_card, self.trs.current_news.translation_date
            )
            self.trs.close_driver()
            sg.popup("All translation job has finished!")

    def get_news_from_trello(self, target_list="在上传"):
        def fix_descriptions_to_news_url(url_list):
            tmp_list = list()
            for desc in url_list:
                info = desc.get("_value")
                link = info[info.find("(") + 1:info.find(")")]
                tmp_list.append(link)
            return tmp_list

        if self.trel is None:
            self.trel = TrelloController(trello_upload_board_id, target_list)
        else:
            self.trel.set_target_board(trello_upload_board_id)
            self.trel.set_target_list(target_list)

        if self.gdapi is None:
            self.gdapi = GDAPIC()

        news_urls_to_upload = self.trel.get_all_urls_from_a_lists_attachments()
        news_descs_to_upload = self.trel.get_all_descriptions_from_target_list()
        self.news_source_urls_to_upload = fix_descriptions_to_news_url(news_descs_to_upload)

        news_docs_urls_to_upload = [elem for elem in news_urls_to_upload if "google" in elem]

        for news_url in news_docs_urls_to_upload:
            doc_id = self.gdapi.doc_id_from_url(news_url)
            text = self.gdapi.get_a_documents_content(doc_id)  # text is a list
            self.upload_news_list.append(text)
        self.number_of_news_to_upload = len(self.upload_news_list)

    def upload_news_to_wechat(self):
        def make_abstract(source):
            temp = "\n".join(source[1:3])
            # remove names in the parantheses
            # Source: https://stackoverflow.com/questions/640001/how-can-i-remove-text-within-parentheses-with-a-regex
            re.sub(r"\([^)]*\)", "", temp)
            # re.sub(r'\（[^)]*\）', '', temp) Not working for Chinese characters
            temp = temp[:115]
            return temp

        self.wc.start_the_system()
        self.wc.enter_to_wechat()
        self.wc.open_text_editor_from_home()
        for index, news in enumerate(self.upload_news_list):
            try:
                abstract = make_abstract(news)
                self.wc.daily_news_adder(
                    news[0], news[-1], "", news[1:-1], abstract
                )  # Title, news_url, image_url, content, abstract
            except Exception as error:
                print(error)
                print("it happened around daily news")
            self.wc.save()
            time.sleep(3)

            if index == self.number_of_news_to_upload - 1:
                break
            try:
                self.wc.open_next_news()
            except Exception as error:
                print(error)
                print("It happened when clicking next news")

        sg.popup("Everything is uploaded to Wechat!")
        self.wc.close_browser()

    def upload_news_to_wordpress(self):
        minutes = (self.number_of_news_to_upload * 10) - 10
        publish_date = datetime.datetime.now().strftime("%Y-%m-%dT")
        for news in self.upload_news_list:
            text = '\n\n'.join(news[1:-1])
            exc = '\n\n'.join(news[1:3])
            publish_time = publish_date + f"18:{minutes}:00+08:00"
            self.wordpress.upload_a_post(title=news[0], content=text, excerpt=exc, status='draft', date=publish_time)
            minutes = int(minutes) - 10
            if minutes == 0:
                minutes = "00"

    def selected_news_listing(self, nlist):
        selected_news = list()
        for news_index in nlist:
            news = self.table_data[news_index]
            for elem in self.daily_news_selection_list:
                if news[0] in elem:
                    selected_news.append(elem)
                    break
        self.url_list = [elem[4] for elem in selected_news]
        self.url_title_list = [elem[2] for elem in selected_news]

    def sunday_collect_and_upload(self):
        self.wc.start_the_system()
        self.wc.enter_to_wechat()
        self.wc.get_news_links()
        self.wc.title_image_text_extract()
        self.wc.open_text_editor_from_home()
        self.wc.add_weekly_news()
        sg.Popup("Sunday Collector uploaded all news!")

    def table_data_maker(self):
        # putting titles and sources into one table
        sources = [elem[0].get("name") for elem in self.daily_news_selection_list]
        titles = [elem[2] for elem in self.daily_news_selection_list]
        table_data = [[title, source] for (title, source) in zip(titles, sources)]
        return table_data

    def main_loop(self):
        while True:
            event, values = self.window.read()
            print(event, values)
            if event in (None, "-EXIT-"):
                break
            if event == "-NEWS FEED SBB-":
                self.nac = NewsAPIController()
                try:
                    self.daily_news_selection_list = self.nac.get_eveything_turkey()
                    print(self.daily_news_selection_list)
                    # Format of this list:
                    # 0: dict{id, source_name} 1:Author, 2:title, 3: desc, 4:url, 5:img_url, 6:date, 7:excerpt
                    self.table_data = self.table_data_maker()
                    self.window["-NEWS SELECTION TABLE-"].update(values=self.table_data)
                except Exception as error:
                    sg.PopupError(
                        f"{error}\nThere was a problem with the NewsAPI, check your credentials"
                    )
                    self.table_data = list()
                self.window["-PROG-"].update(current_count=0, max=len(self.url_title_list))
                self.change_layout("-NEWS SELECTION-")

            if event == "-SELECTION COMPLETE-":
                news_selected = values["-NEWS SELECTION TABLE-"]
                self.selected_news_listing(news_selected)

            if event == "-TRANSLATOR SBB-":
                self.url_title_list, self.url_list = htm_to_urllist(
                    DOC_PATH
                )
                self.window["-NEWS LIST-"].Update(values=self.url_title_list)
                self.change_layout("-TRANSLATOR BEFORE-")

            if event == "-TRANSLATE BUTTON-":
                if self.current_visible == "-TRANSLATOR DURING-":
                    sg.popup(
                        "News are currently being translated, please wait until it finishes!"
                    )
                    continue
                self.print = self.print_set("-NEWS INFO-")
                self.change_layout("-TRANSLATOR DURING-")
                self.gdapi = GDAPIC()
                # threading.Thread(target=translate_news, args=(window, urlinfo[1],), daemon=True).start()
                if values.get("-SOGOU-"):
                    self.translate_news("sogou")
                elif values.get("-BAIDU-"):
                    self.translate_news("baidu")

            if event == "-SUNDAY COL SBB-":
                self.change_layout("-SUNDAY COLLECTOR-")

            if event == "-SCOL FETCH BUTTON-":
                self.wc = Wechat()
                if values.get("-JUST WEEKLY-"):
                    self.sunday_collect_and_upload()
                    pass
                else:
                    # Do all together
                    pass

                self.wc.close_browser()

            if event == "-UPLOADER SBB-":
                self.change_layout("-UPLOADER PAGE-")
                self.print = self.print_set("-UPLOAD INFO-")

            if event == "-UPLOAD REFRESH-":
                self.upload_news_list = list()
                self.window["-UPLOAD INFO-"].update("")
                self.upen = UploadingEngine()
                if not values.get("-WECHAT UPLOAD-") and values.get("-WORDPRESS UPLOAD-"):
                    self.get_news_from_trello(target_list="在上传 - 只WP")
                else:  # TODO The case where both options not been chosen should be added here
                    self.get_news_from_trello()
                for elem in self.upload_news_list:
                    self.print(elem[0])

            if event == "-UPLOAD BUTTON-":
                # self.change_layout("-UPLOAD DURING-")
                self.upen.do_daily_download_for_images(self.news_source_urls_to_upload)
                if values.get("-WORDPRESS UPLOAD-"):
                    self.wordpress = WPC()
                    try:
                        self.upload_news_to_wordpress()
                    except Exception as error:
                        print(error)
                        print("Happened while uploading to the wordpress")

                if values.get("-WECHAT UPLOAD-"):
                    self.wc = Wechat()
                    try:
                        self.upload_news_to_wechat()
                    except Exception as error:
                        print(error)
                        self.wc.close_browser()

        self.window.close()

    def start_the_program(self):
        self.window = sg.Window(
            f"{self.main_window_name}", self.working_window_layout, size=(WIDTH, HEIGHT)
        )
        self.current_visible = "-WELCOME-"
        self.main_loop()


if __name__ == "__main__":
    EtC = EtcTranslatorForAll()
    EtC.start_the_program()
