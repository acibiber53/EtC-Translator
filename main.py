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
import os
import winreg
import PySimpleGUI as sg
from translating_engine import htm_to_urllist, translate_news
from newsapi_controller import selected_news_listing, get_all_news_about_turkey
from uploading_engine import (
    UploadingEngine,
    get_news_from_trello,
    sunday_collect_and_upload,
    upload_news_to_wordpress,
    upload_news_to_wechat,
)

reg_key = winreg.OpenKey(
    winreg.HKEY_CURRENT_USER,
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
)
downloads_path = winreg.QueryValueEx(reg_key, "{374DE290-123F-4565-9164-39C4925E467B}")[
    0
]
winreg.CloseKey(reg_key)

DOC_PATH = downloads_path + "\exported-bookmarks.html"

WIDTH = 1024
HEIGHT = 768
PADDING = 20


class EtcTranslatorForAll:
    def __init__(self):
        # Translation variables
        self.url_title_list, self.url_list = htm_to_urllist(DOC_PATH)
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

        empty_list = [
            ["This is a placeholder for a title of a news.", "This is their Source"],
            ["", ""],
        ]
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
            [sg.Checkbox("WordPress", default=True, key="-WORDPRESS UPLOAD-")],
            [sg.Checkbox("Wechat", default=True, key="-WECHAT UPLOAD-")],
            [
                sg.Text(
                    "Selecting only WordPress will get the news from '在上传 - 只WP' list, any other selection will get "
                    "the news from '在上传'."
                )
            ],
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
        SIDEBAR_WIDTH = int(WIDTH / 4 - PADDING)
        REST_WIDTH = int((WIDTH / 4) * 3 - PADDING)
        REAL_HEIGHT = int(HEIGHT - 3 * PADDING)
        self.working_window_layout = [
            [
                sg.Column(layout=sidebar_maker(), size=(SIDEBAR_WIDTH, REAL_HEIGHT)),
                sg.VSeparator(),
                sg.Column(
                    layout=self.welcome_layout,
                    size=(REST_WIDTH, REAL_HEIGHT),
                    key="-WELCOME-",
                ),
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

    def main_loop(self):
        # This flag is not being reverted back, so it only works one way. Might create problems in the future
        selected_from_news_api = False
        while True:
            event, values = self.window.read()
            print(event, values)
            if event in (None, "-EXIT-"):
                break
            if event == "-NEWS FEED SBB-":
                try:
                    # Format of the list daily_news_selection_list:
                    # 0: dict{id, source_name} 1:Author, 2:title, 3: desc, 4:url, 5:img_url, 6:date, 7:excerpt
                    (
                        self.daily_news_selection_list,
                        self.table_data,
                    ) = get_all_news_about_turkey()
                    self.window["-NEWS SELECTION TABLE-"].update(values=self.table_data)

                except Exception as error:
                    sg.PopupError(
                        f"{error}\nThere was a problem with the NewsAPI, check your credentials"
                    )
                    self.table_data = list()
                self.window["-PROG-"].update(
                    current_count=0, max=len(self.url_title_list)
                )
                self.change_layout("-NEWS SELECTION-")

            if event == "-SELECTION COMPLETE-":
                news_selected = values["-NEWS SELECTION TABLE-"]
                self.url_list, self.url_title_list = selected_news_listing(
                    news_selected, self.table_data, self.daily_news_selection_list
                )
                selected_from_news_api = True

            if event == "-TRANSLATOR SBB-":
                if not selected_from_news_api:
                    self.url_title_list, self.url_list = htm_to_urllist(DOC_PATH)
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
                # threading.Thread(target=translate_news, args=(window, urlinfo[1],), daemon=True).start()
                if values.get("-SOGOU-"):
                    translate_news("sogou", self.url_list, self.print, self.window)
                elif values.get("-BAIDU-"):
                    translate_news("baidu", self.url_list, self.print, self.window)
                sg.popup("All translation job has finished!")

            if event == "-SUNDAY COL SBB-":
                self.change_layout("-SUNDAY COLLECTOR-")

            if event == "-SCOL FETCH BUTTON-":
                if values.get("-JUST WEEKLY-"):
                    wc = sunday_collect_and_upload()
                else:
                    # Do all together
                    pass
                sg.Popup("Sunday Collector uploaded all news!")
                wc.close_browser()

            if event == "-UPLOADER SBB-":
                self.change_layout("-UPLOADER PAGE-")
                self.print = self.print_set("-UPLOAD INFO-")

            if event == "-UPLOAD REFRESH-":
                self.upload_news_list = list()
                self.window["-UPLOAD INFO-"].update("")
                self.upen = UploadingEngine()
                if not values.get("-WECHAT UPLOAD-") and not values.get(
                    "-WORDPRESS UPLOAD-"
                ):
                    sg.popup("Please select an option to continue!")
                    continue
                else:  # TODO The case where both options not been chosen should be added here
                    a, b, c = get_news_from_trello(self.upload_news_list)
                self.upload_news_list = a
                self.number_of_news_to_upload = b
                self.news_source_urls_to_upload = c

                for elem in self.upload_news_list:
                    self.print(elem[0])

            if event == "-UPLOAD BUTTON-":
                # self.change_layout("-UPLOAD DURING-")
                if self.number_of_news_to_upload == 0:
                    sg.popup(
                        "Please click 'Show Upload Content' button first, in order to start Uploading!"
                    )
                    continue
                image_paths = self.upen.do_daily_download_for_images(
                    self.news_source_urls_to_upload
                )
                if values.get("-WORDPRESS UPLOAD-"):
                    try:
                        upload_news_to_wordpress(
                            image_paths,
                            self.number_of_news_to_upload,
                            self.upload_news_list,
                        )
                        sg.popup("Everything is uploaded to Wordpress!")
                    except Exception as error:
                        print(error)
                        print("Happened while uploading to the wordpress")

                if values.get("-WECHAT UPLOAD-"):
                    # I needed to send wechat controller back because popup should stop you from closing the page,
                    # sometimes wechat doesn't upload properly, and you need to see it change something before closing,
                    # everything down.
                    wc = upload_news_to_wechat(
                        self.upload_news_list, self.number_of_news_to_upload
                    )
                    sg.popup("Everything is uploaded to Wechat!")
                    wc.close_browser()

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
