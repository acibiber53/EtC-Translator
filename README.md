# EtC-Translator
This will translate English news about Turkey to Chinese. It is using Selenium WebDriver for Chrome. Could be downloaded from https://chromedriver.chromium.org/downloads. Download it according to your own Chrome version. 

Websites currently covered are:
- https://www.reuters.com/news/archive/turkey
- https://apnews.com/Turkey
- https://www.aljazeera.com/topics/country/turkey.html
- https://ahvalnews.com/news
- https://www.duvarenglish.com/
- https://www.aa.com.tr/en/turkey
- https://www.hurriyetdailynews.com/turkey/
- https://www.dailysabah.com/turkey
- https://www.turkishminute.com/

More websites could be added according to need.

To make this script work, a preparation of newslinks is needed. news-to-translate.htm file is hand-made (for now). Steps to create this file are:
1. Open all the news in seperate tabs on Chrome. Don't have any other tab open
2. Hit Ctrl + Shift + D to bookmark all the tabs.
3. Hit Ctrl + Shift + O to open bookmark manager.
4. From upper rigth Settings, export bookmarks and save it to anywhere you like.
5. Open the bookmarks html file and find the news. Copy all the links.
6. Open a word document and paste the links. Save it as htm file named 'news-to-translate.htm' to the same folder of this script.
7. Run the script
