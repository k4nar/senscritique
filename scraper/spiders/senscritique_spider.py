# -*- coding: utf8 -*-

import re

from scrapy.spider import Spider
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector

from scraper.items import UserItem, ProductItem, RatingItem


class SenscritiqueSpider(Spider):
    name = "senscritique"
    allowed_domains = ["senscritique.com"]
    base_url = "http://www.senscritique.com/"
    start_urls = [base_url + "LeYéti"]

    def __init__(self, *args, **kwargs):
        super(SenscritiqueSpider, self).__init__(*args, **kwargs)
        self.products = set()

    def url(self, part, *args, **kwargs):
        return self.base_url + part.format(*args, **kwargs)

    def parse(self, response):
        uri = response.url.split("/")[-1]

        if not uri:
            return

        sel = Selector(response)
        uid = sel.xpath('//div[@class="uco-cover-controls"]/div/@data-sc-user-id').extract()[0]

        user = UserItem()
        user['uid'] = int(uid)
        user['uri'] = uri

        info = sel.xpath('//div[@class="d-cover-subtitle"]/text()').extract()
        if info:
            info = info[0].encode('utf-8')
            gender = info.split(',')[0].strip()
            if gender:
                user['gender'] = 'm' if gender == 'Homme' else 'f'
            age = re.search(r"(\d+)\sans", info)
            if age:
                user['age'] = age.groups()[0]
            postcode = re.search(r"\((\d{5})\)", info)
            if postcode:
                user['postcode'] = postcode.groups()[0]

        yield user

        yield Request(
            url=self.url("sc/{}/collection/rating/page-1.ajax", uri),
            headers={'X-Requested-With': 'XMLHttpRequest'},
            meta={'uid': uid, 'uri': uri},
            callback=self.parse_collection,
        )

        yield FormRequest(
            url=self.url("sc/scouts/index/index.ajax"),
            formdata={'user-id': str(uid), 'filter': 'tous'},
            headers={'X-Requested-With': 'XMLHttpRequest'},
            meta={'uid': uid},
            callback=self.parse_contacts,
        )

    def parse_contacts(self, response):
        uid = response.meta['uid']
        sel = Selector(response)

        if "index.ajax" in response.url:
            for page in xrange(2, self._get_nb_pages(sel) + 1):
                yield FormRequest(
                    url=self.url("sc/scouts/page-{}.ajax", page),
                    formdata={'user-id': uid, 'filter': 'tous'},
                    headers={'X-Requested-With': 'XMLHttpRequest'},
                    meta=response.meta,
                    callback=self.parse_contacts,
                )

        for contact in sel.xpath('//li[@class="esli-item"]/a/@href').extract():
            url = self.url(contact.encode('utf-8').split("/")[-1])
            if not url in self.start_urls:
                yield Request(
                    url=url,
                    callback=self.parse
                )

    def parse_collection(self, response):
        uid = response.meta['uid']
        uri = response.meta['uri']
        sel = Selector(response)

        if "page-1.ajax" in response.url:
            for page in xrange(2, self._get_nb_pages(sel) + 1):
                yield Request(
                    url=self.url("/sc/{}/collection/rating/page-{}.ajax", uri, page),
                    headers={'X-Requested-With': 'XMLHttpRequest'},
                    meta=response.meta,
                    callback=self.parse_collection,
                )

        for item in sel.xpath('//li[@class="elco-collection-item"]'):
            pid = int(item.xpath('figure/@data-sc-product-id').extract()[0].encode('utf-8'))
            if not pid in self.products:
                self.products.add(pid)
                product = ProductItem()
                product['pid'] = pid
                title = item.xpath('div/h2/a[@class="elco-anchor"]')
                url = title.xpath("@href").extract()[0].encode('utf-8').split('/')
                product['category'] = url[1]
                product['uri'] = url[-2]
                product['name'] = title.xpath("text()").extract()[0].encode('utf-8')
                yield product

            node = item.xpath('div/div[@class="erra user"]/a/div')
            rating = RatingItem()
            rating['pid'] = pid
            rating['uid'] = int(uid)
            rating['score'] = int(node.xpath('span/text()').extract()[0].encode('utf-8'))
            rating['recommended'] = bool(node.xpath('span/span[contains(@class, "eins-recommend")]'))
            yield rating

    def _get_nb_pages(self, sel):
        nb_pages = sel.xpath('//ul[@class="eipa-pages"][1]/li[last()]/a/@data-sc-pager-page').extract()
        return int(nb_pages[0]) if nb_pages else 1
