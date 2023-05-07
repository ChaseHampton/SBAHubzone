import scrapy
import json
from ..hubdb import HubDB
from ..models.batch import Batch


class SbahubSpider(scrapy.Spider):
    name = "SBAHub"
    allowed_domains = ["dsbs.sba.gov"]
    start_urls = ["https://dsbs.sba.gov/"]

    def __init__(self, reset=False, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.db = HubDB()
        self.reset = reset
        if self.reset:
            self.db.reset_businesses()
            self.db.reset_search_is_searched()


    def parse(self, response):
        for search in self.db.get_all_searches():
            request = scrapy.FormRequest.from_response(
                response,
                formdata=json.loads(search['body']),
                meta={'search': search},
                dont_click=True,
                formname="SearchForm",
                callback=self.collect_businesses
            )
            yield request
        batch = self.db.get_batch_of_businesses()
        if batch.recs:
            yield scrapy.Request(url='http://BatchSearch.bs', meta={'batch': batch}, callback=self.dispatch_batch_searches)
                

    def collect_businesses(self, response):
        table = response.css('table#ProfileTable tbody')
        rows = table.css('tr')
        businesses = []
        for row in rows:
            business = (row.css('td a::text').get(), row.css('td a::attr(href)').get(), row.css('td a::attr(href)').re_first(r'.*\?.*=(.*)$'))
            businesses.append(business)
        self.db.insert_businesses(businesses)
        self.db.update_search_is_searched(response.meta['search'])


    def dispatch_batch_searches(self, response):
        for business in response.meta['batch'].recs:
            yield scrapy.Request(url=response.urljoin(business['url']), meta=response.meta, callback=self.parse_business_page)
        batch = self.db.get_batch_of_businesses(response.meta['batch'].limit, response.meta['batch'].offset)
        if batch:
            yield scrapy.Request('http://BatchSearch.bs', meta={'batch': batch}, callback=self.dispatch_batch_searches)

    def parse_business_page(self, response):
        return
