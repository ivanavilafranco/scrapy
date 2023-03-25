# mobilede_scraper/spiders/mobilede_spider.py
import scrapy

class MotorhomeSpider(scrapy.Spider):
    name = 'motorhome_spider'
    start_urls = ['https://www.mobile.de/es/categor%C3%ADa/autocaravana/vhc:motorhome,srt:date,sro:desc']

    def parse(self, response):
        for motorhome in response.css('article.list-entry'):
            title = motorhome.css('h3.vehicle-title::text').get()
            year_km = motorhome.css('.vehicle-information p.u-text-bold::text').get()
            hp = motorhome.css('.vehicle-information p.u-text-grey-60::text').get()
            vehicle_specs = motorhome.css('.vehicle-techspecs p.u-text-grey-60::text').getall()
            price_gross = motorhome.css('.vehicle-prices p.seller-currency.u-text-bold::text').get()
            
            yield {
                'title': title.strip() if title else None,
                'year_km': year_km.strip() if year_km else None,
                'hp': hp.strip() if hp else None,
                'vehicle_specs': [spec.strip() for spec in vehicle_specs] if vehicle_specs else None,
                'price_gross': price_gross.strip() if price_gross else None,
            }

        # Pagination: get the URL for the next page and create a new request
        next_page_url = response.css('a.pagination-nav.pagination-nav-right::attr(href)').get()
        if next_page_url:
            yield scrapy.Request(url=response.urljoin(next_page_url), callback=self.parse)
