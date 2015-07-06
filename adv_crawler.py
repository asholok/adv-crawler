import csv
import re
from bs4 import BeautifulSoup
import time
import twill
import twill.commands as tw

STANDART_PAGE = 'https://www.erstenachhilfe.de/nachhilfelehrer?page={}'
PAGE_NUMBER = 1
LOGIN = 'arjeeee'
PASSWORD = 'RapidGrowth2015'
HOST_BLANK = 'https://www.erstenachhilfe.de{}'

class Crowler(object):
    def __init__(self):
        self.paginator = PAGE_NUMBER
        self.results = []
        self.browser = self.__create_session()

    def __create_session(self):
        browser = twill.get_browser()
        browser.go('http://www.erstenachhilfe.de/user?destination=node%2F767')
        tw.fv('2', 'edit-name', LOGIN)
        tw.fv('2', 'edit-pass', PASSWORD)
        tw.showforms()
        tw.submit('op')

        return browser

    def to_craw(self):
        adverts = self.__find_adverts()
        
        while adverts and PAGE_NUMBER < 2:
            try:
                advert_anchors = self.__find_links(adverts)
                
                self.results.extend(self.__collect_detail(advert_anchors))
            except:
                adverts = False
            else:   
                self.paginator += 1
                adverts = self.__find_adverts()
        
        self.__save_data()

    def __find_adverts(self):
        self.browser.go(STANDART_PAGE.format(str(self.paginator)))
        html = self.browser.get_html()
        soap = BeautifulSoup(html)
        
        return soap.find_all('span',{'class': 'headline'})

    def __find_links(self, content):
        advert_anchors = []
    
        for advert in content:
            anchors = advert.find_all('a')

            advert_anchors.append(anchors[0])

        return advert_anchors

    def __collect_detail(self, stack):
        result = []
        for anchor in stack:
            link = HOST_BLANK.format(anchor.get('href'))

            result.append(self.__parse_detail(link))
            time.sleep(10)
        
        return result

    def __parse_detail(self, detail_link):
        result = {}
        self.browser.go(detail_link)
        html = self.browser.get_html()
        soap = BeautifulSoup(html)
    
        result['link'] = detail_link.encode('utf-8')
        result['subjects'] = self.__get_subjects(soap).encode('utf-8')
        result['phone'] = self.__get_phone(soap).encode('utf-8')
        result['city'] = self.__get_city(soap).encode('utf-8') 
        # result['email'] = self.__get_email(soap).encode('utf-8')
        
        print result.encode('utf-8')

        return result

    def __get_subjects(self, soap):
        result = soap.find('td', {'class': 'bold'})

        return result.get_text()

    def __get_city(self, soap):
        tags = soap.find('div', {'id': 'first_block'})
        part_text = tags.get_text().split("PLZ Ort:")
        result = part_text[1].split(' ')
        """ Zip code will be result[0] """
        return result[1]

    def __get_phone_from_ajax(self, link):
        self.browser.go(link)
        html = self.browser.get_html()

        return html.split('</h3>')[1]

    
    def __get_phone(self, soap):
        anchor = soap.find('a', {'class': 'ajax_tip'})

        if anchor:
            link = HOST_BLANK.format(anchor.get('href'))
            return self.__get_phone_from_ajax(link)

        return 'N/A'

    def __save_data(self):
        with open('adverts.csv', 'wb') as f:
            fieldnames = ['link', 'subjects', 'city', 'phone']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for row in self.results:
                writer.writerow(row)



a = Crowler()

a.to_craw()