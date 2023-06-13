base_urls = {
    "ahvalnews": "https://ahvalnews.com/"
}

image_paths = {
    "reuters": "//img[1]/@src",
    "apnews": "//meta[@property='twitter:image']/@content",
    "aljazeera": "//div[@class='l-col.l-col--8']/div[2]/*[self::p or self::h2]",
    "ahvalnews": "//div[@class='field-content']",
    "turkishminute": "//div[@class='tdb-block-inner td-fix-index']/img/@src",
    "duvarenglish": "//meta[@property='og:image']/@content",
    "aa": "//meta[@name='twitter:image:src']/@content",
    "hurriyetdailynews": "//div[@class='content']/img/@data-src",
    "dailysabah": "//div[@class='image_holder ']/a/div[1]/img/@src",
    "trtworld": "//div[@class='image']//source/@data-srcset",
    "nordicmonitor": "//div[@class='jeg_inner_content']/div/a/@href",
    "stockholmcf": "//div[@class='td-post-featured-image']/a/@href",
}

headers = {
    "reuters": "//h1",
    "apnews": "//div[@class='CardHeadline']/div[1]/h1",
    "aljazeera": "//header[@class='article-header']/h1",
    "ahvalnews": "//section[@class='col-sm-12']/div/div/div[3]/div[1]/h1",
    "turkishminute": "//h1[@class='tdb-title-text']",
    "duvarenglish": "//header/h1",
    "aa": "//div[@class='detay-spot-category']/h1",
    "hurriyetdailynews": "//div[@class='content']/h1",
    "dailysabah": "//h1[@class='main_page_title']",
    "trtworld": "//h1[@class='article-title']",
    "nordicmonitor": "//div[@class='entry-header']/h1",
}

bodies = {
    "reuters": "//p",
    "apnews": "//div[@class='Article']/p",
    "aljazeera": "//div[@class='l-col.l-col--8']/div[2]/*[self::p or self::h2]",
    "ahvalnews": "//div[@class='field--item']/div/div/p",
    "turkishminute": "//div[@class='tdb-block-inner td-fix-index']/p",
    "duvarenglish": "//div[@class='content-text']/*[self::p or self::h2 or self::h3]",
    "aa": "//div[@class='detay-icerik']/div[1]/p",
    "hurriyetdailynews": "//div[@class='content']/p",
    "dailysabah": "//div[@class='article_body']/p",
    "trtworld": "//div[@class='Article-List']/div/div/div/p",
    "nordicmonitor": "//div[@class='content-inner ']/p",
}

outlet_chinese_names = {
    "reuters": "路透社",
    "apnews": "美联社",
    "aljazeera": "《半岛电视台》",
    "ahvalnews": "Ahval新闻",
    "turkishminute": "土耳其分钟",
    "duvarenglish": "《墙报》",
    "aa": "阿纳多卢通讯社",
    "hurriyetdailynews": "《自由报》",
    "dailysabah": "《每日晨报》",
    "trtworld": "TRTWorld ",
    "nordicmonitor": "北欧观察 ",
}