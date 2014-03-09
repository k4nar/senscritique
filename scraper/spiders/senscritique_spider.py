# -*- coding: utf8 -*-

import re

from scrapy.spider import Spider
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector

from scraper.items import UserItem


class SenscritiqueSpider(Spider):
    name = "senscritique"
    allowed_domains = ["senscritique.com"]
    start_urls = ['http://www.senscritique.com/LeYéti']

    def parse(self, response):
        sel = Selector(response)
        uid = sel.xpath('//div[@class="uco-cover-controls"]/div/@data-sc-user-id').extract()[0]
        uri = response.url.split("/")[-1]

        info = sel.xpath('//div[@class="d-cover-subtitle"]/text()').extract()[0]

        user = UserItem()
        user['uri'] = uri
        user['uid'] = uid
        if info:
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
            url="http://www.senscritique.com/sc/{}/collection/rating/page-1.ajax".format(uri),
            headers={'X-Requested-With': 'XMLHttpRequest'},
            meta={'uid': uid, 'name': name},
            callback=self.parse_collection,
        )

        yield FormRequest(
            url="http://www.senscritique.com/sc/scouts/index/index.ajax",
            formdata={'user-id': uid, 'filter': 'tous'},
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
                    url="http://www.senscritique.com/sc/scouts/page-{}.ajax".format(page),
                    formdata={'user-id': uid, 'filter': 'tous'},
                    headers={'X-Requested-With': 'XMLHttpRequest'},
                    meta=response.meta,
                    callback=self.parse_contacts,
                )

        for contact in sel.xpath('//li[@class="esli-item"]/a/@href').extract():
            yield Request(
                url="http://senscritique.com" + contact,
                callback=self.parse
            )

    def parse_collection(self, response):
        uid = response.meta['uid']
        name = response.meta['name']
        sel = Selector(response)

        if "page-1.ajax" in response.url:
            for page in xrange(2, self._get_nb_pages(sel) + 1):
                yield Request(
                    url="http://www.senscritique.com/sc/{}/collection/rating/page-{}.ajax".format(name, page),
                    headers={'X-Requested-With': 'XMLHttpRequest'},
                    meta=response.meta,
                    callback=self.parse_collection,
                )

        for item in sel.xpath('//div[@class="elco-collection-content"]'):
            uri = item.xpath('h2/a[@class="elco-anchor"]/@href').extract()[0].encode('utf-8')
            score = int(item.xpath('div[@class="erra user"]/a/div/span/text()').extract()[0].encode('utf-8'))
            print uri, score

    def _get_nb_pages(self, sel):
        nb_pages = sel.xpath('//ul[@class="eipa-pages"][1]/li[last()]/a/@data-sc-pager-page').extract()
        return int(nb_pages[0]) if nb_pages else 1
