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
from bs4 import BeautifulSoup
from translating_engine import Translator
from gdapi_controller import GoogleDriveAPIController as GDAPIC
from trello_controller import TrelloController
from wechat import Wechat
import time
import os
import PySimpleGUI as sg
import re
from newsapi_controller import NewsAPIController
import threading


class EtcTranslatorForAll:
    def __init__(self, news_link_document_path="news-to-translate.htm"):
        # Translation variables
        self.url_title_list, self.url_list = self.htm_to_urllist(news_link_document_path)
        self.translation_engine = "sogou"
        self.gdapi = GDAPIC()
        self.trs = self.trel = None

        # GUI variables
        self.main_window_name = "EtC Translator for all"

        # News selection variables
        self.nac = NewsAPIController()
        self.daily_news_selection_list = self.nac.get_eveything_turkey()
        # Format of this list:
        # 0: dict{id, source_name} 1:Author, 2:title, 3: desc, 4:url, 5:img_url, 6:date, 7:excerpt
        self.table_data = self.table_data_maker(self.daily_news_selection_list)

        # Layouts needed
        self.welcome_layout = \
            self.news_selection_layout = \
            self.translation_layout_before = \
            self.translation_layout_during = \
            self.sunday_collector_layout = \
            self.working_window_layout = \
            self.upload_layout = None

        self.set_layouts()
        self.window = self.current_visible = self.print = None

        # Uploading variables
        self.upload_news_list = list()
        self.wc = None
        self.number_of_news_to_upload = 0

    def table_data_maker(self, news_list):
        #putting titles and sources into one table
        sources = [elem[0].get('name') for elem in self.daily_news_selection_list]
        titles = [elem[2] for elem in self.daily_news_selection_list]
        table_data = [[title, source] for (title, source) in zip(titles, sources)]
        return table_data

    @staticmethod
    def htm_to_urllist(doc_name):
        """This method opens a predetermined htm file that is extracted from the bookmarks of chrome, and
        lists every link inside of it.

        Preparation for the htm file should be done well. Steps for that:
        1 - Put all your websites you want to translate into one bookmark folder. Ctrl + Shift + D for short.
        2 - Open the file, find your folder, copy the content.
        3 - Open MS Word, paste the content, save the folder as .htm/ .html"""
        try:
            with open(doc_name, encoding='utf-8') as file:
                soup = BeautifulSoup(file, "lxml")
        except FileNotFoundError:
            print(f"We couldn't find your document, please make sure to have a document named {doc_name}. "
                  f"Add the required htm file and try again!")
            os.system("pause")
            return -1, -1

        urllist = list()
        url_title_list = list()
        for link in soup.find_all('a'):
            urllist.append(link.get('href'))
            url_title_list.append(link.get_text().replace("\n", " "))
        return url_title_list, urllist

    def set_layouts(self):
        def sidebar_maker():
            return [[sg.Text("Menu")],
                    [sg.HSeparator()],
                    [sg.Button('News Feed', key='-NEWS FEED SBB-')],
                    [sg.Button('Translator', key='-TRANSLATOR SBB-')],
                    [sg.Button('Sunday Collector', key='-SUNDAY COL SBB-')],
                    [sg.Button('Uploader', key='-UPLOADER SBB-')],
                    [sg.Button('Settings', key='-SETTINGS SBB-')],
                    [sg.Button('Exit', key='-EXIT-')]]

        # Title maker for main working column
        def title_maker(title):
            return ([
                        sg.Text(f"{title}", justification='right')
                    ],
                    [
                        sg.HSeparator()
                    ])

        # Different layouts for main working window
        # Opening Layout
        self.welcome_layout = [
            *title_maker(self.main_window_name),
            [
                sg.Text("Welcome to this beautiful app! Thank you for your endless support!", justification="center")
            ]
        ]

        self.news_selection_layout = [*title_maker("Translator"),
                                      [sg.Text("News list for selection")],
                                      [sg.Table(
                                          values=self.table_data,
                                          headings=["Title", "Source"],
                                          justification='left',
                                          #vertical_scroll_only=True,
                                          enable_events=True,
                                          num_rows=15,
                                          #def_col_width=50,
                                          # auto_size_columns=True,
                                          col_widths=[100, 15],
                                          select_mode=sg.TABLE_SELECT_MODE_EXTENDED,
                                          key="-NEWS SELECTION TABLE-"
                                      )],
                                      [sg.Button("Save", key="-SELECTION COMPLETE-")]]

        # Translation Layout Before
        self.translation_layout_before = [*title_maker("Translator"),
                                          [sg.Text("News list for translation")],
                                          [sg.Listbox(
                                              values=self.url_title_list, enable_events=True, size=(100, 15),
                                              key="-NEWS LIST-"
                                          )],
                                          [sg.Text(f"Translation engine being used : {self.translation_engine}")],
                                          [sg.Button("Start Translating", key="-TRANSLATE BUTTON-")]]

        # Translation Layout During
        self.translation_layout_during = [*title_maker("Translator"),
                                          [sg.Text("News are being translated now!")],
                                          [sg.Multiline(default_text="Currently translating news info will show here",
                                                        size=(100, 10),
                                                        key="-NEWS INFO-",
                                                        write_only=True,
                                                        auto_refresh=True)],
                                          [sg.ProgressBar(max_value=len(self.url_title_list),
                                                          size=(70, 25),
                                                          key='-PROG-',
                                                          pad=((0, 0), (15, 15)), )]
                                          ]

        # TODO Translation Layout After

        # Sunday Collector Layout
        self.sunday_collector_layout = [*title_maker("Sunday Collector"),
                                        [sg.Text("Select the mode for sunday collector to work:")],
                                        [sg.Radio("Just weekly news", "RADIO1", key="-JUST WEEKLY-", default=True),
                                         sg.Radio("With daily news", "RADIO1", key="-WITH DAILY-")],
                                        [sg.Button("Start Fetching", key="-SCOL FETCH BUTTON-")]
        ]

        # Uploading Layout
        self.upload_layout = [*title_maker("Uploader"),
                              [sg.Text("News Titles to upload:")],
                              [sg.Multiline(size=(80, 10),
                                            key="-UPLOAD INFO-",
                                            write_only=True,
                                            auto_refresh=True)],
                              [sg.Checkbox("Wechat", default=True, key="-WECHAT UPLOAD-")],
                              [sg.Checkbox("WordPress", default=False, key="-WORDPRESS UPLOAD-")],
                              [sg.Button("Start Uploading", key="-UPLOAD BUTTON-")]]

        # Main working window layout
        self.working_window_layout = [
            [
                sg.Column(layout=sidebar_maker(), size=(180, 540)),
                sg.VSeparator(),
                sg.Column(layout=self.welcome_layout, size=(580, 540), key='-WELCOME-'),
                sg.Column(layout=self.news_selection_layout, size=(580, 540),
                          key='-NEWS SELECTION-', visible=False),
                sg.Column(layout=self.translation_layout_before, size=(580, 540),
                          key='-TRANSLATOR BEFORE-', visible=False),
                sg.Column(layout=self.translation_layout_during, size=(580, 540),
                          key='-TRANSLATOR DURING-', visible=False),
                sg.Column(layout=self.sunday_collector_layout, size=(580, 540),
                          key='-SUNDAY COLLECTOR-', visible=False),
                sg.Column(layout=self.upload_layout, size=(580, 540),
                          key='-UPLOADER PAGE-', visible=False)
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
        response = self.trel.create_card_then_attach_link(name=news.title_english, desc=desc,
                                                          url_source=news.google_upload_link)
        self.print(f"Trello card created!\nCard Link:{response.get('url')}\n")

    def upload_daily_news_to_trello(self, trello_daily_card, date):
        self.print("Adding daily news list to the 被选新闻 list！")
        daily_card_desc = '\n'.join([f"[{elem[0]}]({elem[1]})" for elem in trello_daily_card])
        self.trel.target_list = self.trel.get_target_list("被选新闻")
        response = self.trel.create_a_card(name=date, desc=daily_card_desc, due='')
        self.print(f"Trello daily news list card created!\nCard Link:{response.get('url')}\n")

    def translate_news(self):
        if self.url_list == -1:
            return

        self.trs = Translator(self.translation_engine)
        self.trel = TrelloController()
        trello_daily_card = list()

        try:
            for index, link in enumerate(self.url_list):
                start_time = time.time()
                self.print(f"Translation begins for {link}")
                self.trs.translate_main(link)
                self.print(f"Translation ends, it took {time.time() - start_time} seconds.\n")

                trello_daily_card.append((self.trs.current_news.title_english, self.trs.current_news.source_link))

                self.print("Uploading to Google Drive!")
                news_title, self.trs.current_news.google_upload_link = self.gdapi.docx_to_gdocs_uploader(
                    self.trs.current_news.document_name, self.trs.current_news.document_path)
                self.print(
                    f"Uploaded!\nFile Name: {news_title}\nFile URL: {self.trs.current_news.google_upload_link}\n")

                self.create_card_with_trello(self.trs.current_news)
                self.window["-PROG-"].update(index + 1)

        except Exception as error:
            sg.popup_error(error)

        finally:
            self.upload_daily_news_to_trello(trello_daily_card, self.trs.current_news.translation_date)
            self.trs.close_driver()
            sg.popup("All translation job has finished!")

    def get_news_from_trello(self):
        if self.trel is None:
            self.trel = TrelloController("在上传")
        else:
            self.trel.set_target_list("在上传")
        news_urls_to_upload = self.trel.get_all_urls_from_a_lists_attachments()
        news_urls_to_upload = [elem for elem in news_urls_to_upload if 'google' in elem]
        for news_url in news_urls_to_upload:
            doc_id = self.gdapi.doc_id_from_url(news_url)
            text = self.gdapi.get_a_documents_content(doc_id) # text is a list
            self.upload_news_list.append(text)
        self.number_of_news_to_upload = len(self.upload_news_list)

    def upload_news(self):
        def make_abstract(source):
            temp = "\n".join(source[1:3])
            # remove names in the parantheses
            # Source: https://stackoverflow.com/questions/640001/how-can-i-remove-text-within-parentheses-with-a-regex
            re.sub(r'\([^)]*\)', '', temp)
            # re.sub(r'\（[^)]*\）', '', temp) Not working for Chinese characters
            temp = temp[:120]
            return temp

        self.wc.start_the_system()
        self.wc.enter_to_wechat()
        self.wc.open_text_editor_from_home()
        for index, news in enumerate(self.upload_news_list):
            try:

                abstract = make_abstract(news)
                self.wc.daily_news_adder(news[0],
                                         news[-1],
                                         "",
                                         news[1:-1],
                                         abstract)  # Title, news_url, image_url, content, abstract
            except Exception as error:
                print(error)
                print("it happened around daily news")
            self.wc.save()
            time.sleep(3)

            if index == self.number_of_news_to_upload-1:
                break
            try:
                self.wc.open_next_news()
            except Exception as error:
                print(error)
                print("It happened when clicking next news")

        sg.popup("Everything is uploaded to Wechat!")
        self.wc.close_browser()

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

    def main_loop(self):
        while True:
            event, values = self.window.read()
            print(event, values)
            if event in (None, '-EXIT-'):
                break
            if event == '-NEWS FEED SBB-':
                self.change_layout("-NEWS SELECTION-")

            if event == "-SELECTION COMPLETE-":
                news_selected = values['-NEWS SELECTION TABLE-']
                self.selected_news_listing(news_selected)

            if event == '-TRANSLATOR SBB-':
                self.window["-NEWS LIST-"].Update(values=self.url_title_list)
                self.change_layout("-TRANSLATOR BEFORE-")

            if event == "-TRANSLATE BUTTON-":
                if self.current_visible == "-TRANSLATOR DURING-":
                    sg.popup("News are currently being translated, please wait until it finishes!")
                    continue
                self.print = self.print_set("-NEWS INFO-")
                self.change_layout("-TRANSLATOR DURING-")
                # threading.Thread(target=translate_news, args=(window, urlinfo[1],), daemon=True).start()
                self.translate_news()

            if event == '-SUNDAY COL SBB-':
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

                self.get_news_from_trello()
                for elem in self.upload_news_list:
                    self.print(elem[0])

            if event == "-UPLOAD BUTTON-":
                # self.change_layout("-UPLOAD DURING-")
                if values.get('-WECHAT UPLOAD-'):
                    self.wc = Wechat()
                    try:
                        self.upload_news()
                    except Exception as error:
                        print(error)
                    finally:
                        self.wc.close_browser()

                if values.get('-WORDPRESS UPLOAD-'):
                    # TODO do wordpress uploading
                    pass
        self.window.close()

    def start_the_program(self):
        self.window = sg.Window(f'{self.main_window_name}', self.working_window_layout, size=(800, 600))
        self.current_visible = '-WELCOME-'
        self.main_loop()


if __name__ == '__main__':
    EtC = EtcTranslatorForAll(os.path.expanduser("~\Downloads\exported-bookmarks.html"))
    EtC.start_the_program()
