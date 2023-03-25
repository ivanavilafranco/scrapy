import scrapy
import re

class MotorhomeSpider(scrapy.Spider):
    name = 'motorhome_spider'
    start_urls = ['https://www.mobile.de/es/categor%C3%ADa/autocaravana/vhc:motorhome,srt:date,sro:desc']

    motorhomes_data = []

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
                year = re.search(r'(\d{4})', year_km).group(1) if year_km else None
                km = re.search(r'(\d+\.?\d*)\s?km', year_km).group(1) if year_km else None
                cv = re.search(r'(\d+)\s?cv', hp_cv, re.IGNORECASE).group(1) if hp_cv else None
                price = re.search(r'(\d+\.\d+)\s?€', price_gross).group(1) if price_gross else None
                color_exterior = re.search(r'Color exterior:\s?(.+)', ' '.join(vehicle_specs)).group(1) if vehicle_specs else None
                cambio = re.search(r'(Cambio.+)', ' '.join(vehicle_specs)).group(1) if vehicle_specs else None

                # Agrega los datos del vehículo a la lista, evitando duplicados
                motorhome_data = {
                    'title': title.strip(),
                    'year': int(year) if year else None,
                    'km': float(km.replace('.', '')) if km else None,
                    'cv': int(cv) if cv else None,
                    'price': float(price.replace('.', '').replace(',', '.')) if price else None,
                    'color_exterior': color_exterior.strip() if color_exterior else None,
                    'cambio': cambio.strip() if cambio else None,
                }
                if motorhome_data not in self.motorhomes_data:
                    self.motorhomes_data.append(motorhome_data)

        # Pagination: get the URL for the next page and create a new request
        next_page_url = response.css('a.pagination__controls--next::attr(href)').get()
        if next_page_url:
            yield scrapy.Request(url=response.urljoin(next_page_url), callback=self.parse)
        else:
            # Genera los resultados ordenados por año
            self.motorhomes_data.sort(key=lambda x: x['year'], reverse=True)

            # Genera los resultados ordenados
            for motorhome_data in self.motorhomes_data:
                yield motorhome_data
