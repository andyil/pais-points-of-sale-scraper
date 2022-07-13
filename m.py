import requests
import re
import logging
import json
import sys

class M:

    def __init__(self):
        self.cities_url = 'https://www.pais.co.il/include/autocompleteCity.ashx'
        self.per_city_url = 'https://www.pais.co.il/PointsOfSale/getMoreSP.aspx?node={city}&dist=0&lon=0&lat=0&page={page}'

        self.outf = None

        self.log = logging.getLogger('m')

    def get_cities(self):
        r = requests.get(self.cities_url)
        t = r.content.decode('utf-8')

        c = re.compile('![[]CDATA[[](.*)[]]{2}')
        matches = c.findall(t)
        cities = list(set(matches))
        return cities

    def append_records(self, records):
        if self.outf is None:
            self.outf = open('out.txt', 'w', encoding='utf-8')

        for record in records:
            self.outf.write(json.dumps(record))
            self.outf.write('\n')


    def parse_city(self, city):

        address_re = re.compile('<div class="adress_txt">(.*)</div>')

        all = []

        for i in range(1, 10000):
            self.log.info('City %s page %s', city, i)
            u = self.per_city_url.format(city=city, page=i)
            r = requests.get(u)
            t = r.text

            all_matches = address_re.findall(t)

            if len(all_matches) == 0:
                break

            for match in all_matches:
                all.append({'city': city, 'page': i, 'address': match})

        self.append_records(all)
        return all


    def parse_cities(self, cities):
        for city in cities:
            self.log.info('Doing %s', city)
            self.parse_city(city)

    def all(self):
        cities = self.get_cities()
        self.parse_cities(cities)
        if self.outf:
            self.outf.close()

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout)
    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger('m').setLevel(logging.DEBUG)
    m = M()
    m.all()
