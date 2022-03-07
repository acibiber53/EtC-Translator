base_urls = {
    "ahvalnews": "https://ahvalnews.com/"
}

image_paths = {
    "reuters": "//img[1]/@src",
    "apnews": "//meta[@property='twitter:image']/@content",
    "aljazeera": "//div[@class='l-col.l-col--8']/div[2]/*[self::p or self::h2]",
    "ahvalnews": "//div[@class='field-content']/picture/img/@src",
    "turkishminute": "//div[@class='td-post-featured-image']/a/@href",
    "duvarenglish": "//picture",
    "aa": "//div[@class='col-md-10']/img/@src",
    "hurriyetdailynews": "//div[@class='content']/img/@data-src",
    "dailysabah": "//div[@class='article_top_image_widget']/div/a/@href",
    "trtworld": "//figure[@class='content-image']/img/@src",
    "nordicmonitor": "//div[@class='content-inner ']/p",
}

headers = {
    "reuters": "//h1",
    "apnews": "//div[@class='CardHeadline']/div[1]/h1",
    "aljazeera": "//header[@class='article-header']/h1",
    "ahvalnews": "//section[@class='col-sm-12']/div/div/div[3]/div[1]/h1",
    "turkishminute": "//header/h1",
    "duvarenglish": "//header/h1",
    "aa": "//div[@class='detay-spot-category']/h1",
    "hurriyetdailynews": "//div[@class='content']/h1",
    "dailysabah": "//h1[@class='main_page_title']",
    "trtwold": "//h1[@class='article-title']",
    "nordicmonitor": "//div[@class='entry-header']/h1",
}

bodies = {
    "reuters": "//p",
    "apnews": "//div[@class='Article']/p",
    "aljazeera": "//div[@class='l-col.l-col--8']/div[2]/*[self::p or self::h2]",
    "ahvalnews": "//div[@class='field--item']/div/div/p",
    "turkishminute": "//div[@class='td-ss-main-content']/div[4]/p",
    "duvarenglish": "//div[@class='content-text']/*[self::p or self::h2 or self::h3]",
    "aa": "//div[@class='detay-icerik']/div[1]/p",
    "hurriyetdailynews": "//div[@class='content']/p",
    "dailysabah": "//div[@class='article_body']/p",
    "trtworld": "//div[@class='contentBox.bg-w.noMedia']/p",
    "nordicmonitor": "//div[@class='content-inner ']/p",
}