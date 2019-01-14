import scrapy
import requests
import json
import os
import time

class VecteezySpider(scrapy.Spider):
    name = "vecteezyspider"
    #allowed_domains = ['www.vecteezy.com']
    
    def start_requests(self):
        urls = []
        #urls.append('https://www.vecteezy.com/free-vector/icons?license-standard=true')
        for i in range(692):
            urls.append('https://www.vecteezy.com/free-vector/icons?license-standard=true&page=%d' % i)
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            time.sleep(1)
            
    def parse(self, response):
        main_domain = 'https://www.vecteezy.com'
        all_image_link = response.xpath('//*[@class="ez-resource-thumb__img"]/../@href').extract()
        csrf = response.xpath('//head/meta/@content').extract()[-8]
        print('main CSRF:', csrf)

        for i in range(len(all_image_link)):
            url = main_domain + all_image_link[i]
            yield scrapy.Request(url=url, callback=self.DownloadImage, meta={'csrf':csrf, 'referer':url})
            time.sleep(1)

    def DownloadImage(self, response):
        main_domain = 'https://www.vecteezy.com'
        path_to_store_image = '/home/fahad/Spyder_Projects/VecteezyCrawler/images/'
        download_links = response.xpath('//*[@class="download-resource-link__subtext"]/../@href').extract()
        csrf = response.meta.get('csrf')
        referer = response.meta.get('referer')
        cookies = response.headers.getlist("Set-Cookie")
        cookie = ''
        #print('sub CSRF:', csrf)
        for i, each_cookie_element in enumerate(cookies):
            each_cookie_element = each_cookie_element.decode()
            if(i == len(cookies)-1):
                cookie = cookie + each_cookie_element.split(';')[0]
            else:
                cookie = cookie + each_cookie_element.split(';')[0] + '; '

        if not os.path.exists(path_to_store_image):
            os.makedirs(path_to_store_image)

        for i in range(len(download_links)):
            download_link = main_domain+download_links[i]
            image_id = download_link.split('/')[4].split('?')[0]
            #print(download_link, image_id)
            file_name = path_to_store_image + image_id +'.zip'

            if os.path.exists(file_name):
                print("----------------Continue = ", image_id)
                continue

            headers = {'X-CSRF-Token': csrf, 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            'referer': referer, 'cookie': cookie}
            picture_request = requests.get(download_link, headers=headers)
            
            if picture_request.status_code == 200:
                with open(file_name, 'wb') as f:
                    f.write(picture_request.content)
            else:
                print("response code %d for image id %s" % picture_request.status_code, image_id)

            #time.sleep(1)
