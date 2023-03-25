import scrapy
import re
import json

class MotorhomeSpider(scrapy.Spider):
    name = 'motorhome_spider'
    start_urls = ['https://www.mobile.de/es/autocaravana/peugeot/vhc:motorhome,srt:date,sro:desc,mke:19300,dmg:false']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.motorhomes_data = []

    def parse(self, response):
        for motorhome in response.css('article.list-entry'):
            title = motorhome.css('h3.vehicle-title::text').get()

            # Verifica si el título contiene una de las marcas deseadas
            if title and any(brand in title.upper() for brand in ['CITROËN JUMPER', 'PEUGEOT BOXER', 'FIAT DUCATO']):
                year_km = motorhome.css('.vehicle-information p.u-text-bold::text').get()
                hp_cv = motorhome.css('.vehicle-information p.u-text-grey-60::text').get()
                vehicle_specs = motorhome.css('.vehicle-techspecs p.u-text-grey-60::text').getall()
                price_gross = motorhome.css('.vehicle-prices p.seller-currency.u-text-bold::text').get()

                # Extrae el año, los km, los CV, el precio, el color exterior y el cambio del vehículo
                year = int(re.search(r'(\d{4})', year_km).group(1)) if year_km else None
                km = float(re.search(r'(\d+\.?\d*)\s?km', year_km).group(1).replace('.', '')) if year_km else None
                cv = int(re.search(r'(\d+)\s?cv', hp_cv, re.IGNORECASE).group(1)) if hp_cv else None
                price = float(re.search(r'(\d+\.\d+)\s?€', price_gross).group(1).replace('.', '').replace(',', '.')) if price_gross else None
                color_exterior = re.search(r'Color exterior:\s?(.+)', ' '.join(vehicle_specs)).group(1) if vehicle_specs else None
                cambio = re.search(r'(Cambio.+)', ' '.join(vehicle_specs)).group(1) if vehicle_specs else None

                self.motorhomes_data.append({
                    'title': title.strip(),
                    'year_km': year_km.strip() if year_km else None,
                    'hp': hp_cv.strip() if hp_cv else None,
                    'vehicle_specs': vehicle_specs if vehicle_specs else None,
                    'price_gross': price_gross.strip() if price_gross else None,
                    'year': year,
                    'km': km,
                    'cv': cv,
                    'price': price,
                    'color_exterior': color_exterior.strip() if color_exterior else None,
                    'cambio': cambio.strip() if cambio else None,
                })

        # Pagination: get the URL for the next page and create a new request
        next_page_url = response.css('a.pagination__controls--next::attr(href)').get()
        if next_page_url:
            yield scrapy.Request(url=response.urljoin(next_page_url), callback=self.parse)
        else:
            # Ordena los resultados por año
            self.motorhomes_data.sort(key=lambda x: int(re.search(r'(\d{4})', x['year_km']).group(1)) if re.search(r'(\d{4})', x['year_km']) else 0, reverse=True)
            # Genera los resultados ordenados
            for motorhome_data in self.motorhomes_data:
                yield motorhome_data
