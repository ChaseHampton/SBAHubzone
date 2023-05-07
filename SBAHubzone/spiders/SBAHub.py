import scrapy
import json
from ..hubdb import HubDB
from ..models.batch import Batch


class SbahubSpider(scrapy.Spider):
    name = "SBAHub"
    allowed_domains = ["dsbs.sba.gov", "batchsearch.bs"]
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
        batch = self.db.get_batch_of_businesses(limit=10)
        if batch.recs:
            yield scrapy.Request(url='https://dsbs.sba.gov/search/dsp_dsbs.cfm', dont_filter=True, callback=self.dispatch_batch_searches, cb_kwargs={'batch': batch})
                

    def collect_businesses(self, response):
        table = response.css('table#ProfileTable tbody')
        rows = table.css('tr')
        businesses = []
        for row in rows:
            business = (row.css('td a::text').get(), row.css('td a::attr(href)').get(), row.css('td a::attr(href)').re_first(r'.*\?.*=(.*)$'))
            businesses.append(business)
        self.db.insert_businesses(businesses)
        self.db.update_search_is_searched(response.meta['search'])


    def dispatch_batch_searches(self, response, batch):
        for business in batch.recs:
            if business['uei']:
                yield scrapy.FormRequest.from_response(
                    response,
                    method="POST",
                    formname="SearchForm",
                    dont_click=True,
                    formdata={'UEI': business['uei'], 'State': ''},
                    callback=self.search_results_page,
                    cb_kwargs={'business': business}
                )
            else:
                yield scrapy.FormRequest.from_response(
                    response,
                    method="POST",
                    formname="SearchForm",
                    dont_click=True,
                    formdata={'CompanyName': business['bus_name'], 'State': ''},
                    callback=self.search_results_page,
                    cb_kwargs={'business': business}
                )
        batch = self.db.get_batch_of_businesses(batch.limit, batch.offset + batch.limit)
        if batch:
            yield scrapy.Request('https://dsbs.sba.gov/search/dsp_dsbs.cfm', callback=self.dispatch_batch_searches, dont_filter=True, cb_kwargs={'batch': batch})

    def search_results_page(self, response, business:dict):
        bus_link = response.css('td a::attr(href)').get()
        if bus_link:
            yield scrapy.Request(response.urljoin(bus_link), callback=self.parse_business_page, cb_kwargs={'business': business})

    def parse_business_page(self, response, business:dict):
        html = response.text
        self.db.insert_html(html, business)
        return
