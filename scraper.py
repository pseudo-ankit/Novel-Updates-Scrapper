from codecs import StreamWriter
from email.policy import strict
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import re


class ScraperNovelUpdates:

    def __init__(self, query_string) -> None:
        self.query_string = '-'.join(query_string.split(' ')).lower()
        self.novel_updates_url = "https://www.novelupdates.com/series/"+self.query_string
        self.status = 200
        self.page_soup = None
        self.title = None
        self.cover_url = None
        self.discription = None
        self.genre = None
        self.associated_names = None
        self.comments = []


    def scrape(self):
        
        req = Request(self.novel_updates_url , headers={'User-Agent': 'Mozilla/5.0'})
        try:
            res = urlopen(req) ## getting the response from server
        except:
            self.status = -1
            return 

        webpage = res.read()
        self.page_soup = soup(webpage, "html.parser")

        self.__get_title()
        self.__get_genre()
        self.__get_cover_url()
        self.__get_associated_names()
        self.__get_discription()
        # self.__get_comments_on_all_pages()
        self.__get_comments_on_current_page(page_soup=self.page_soup)


    def __get_title(self) -> None:
        try:
            self.title = self.page_soup.find('div', {'class':'seriestitlenu'}).text
        except:
            self.title = "No Title"
    
    def __get_cover_url(self):
        try:
            self.cover_url = self.page_soup.find('div', {'class':'seriesimg'}).img['src']
        except:
            self.cover_url = "No Cover Image"

    def __get_discription(self):
        try:
            self.discription = "\n".join(list(map(lambda x:x.text, 
                                self.page_soup.find('div', {'id':'editdescription'}).find_all('p'))))
        except:
            self.discription = "No Description"
                    

    def __get_genre(self):
        try:
            self.genre = list(map(lambda x:x.text, 
                        self.page_soup.find('div', {'id': 'seriesgenre'}).find_all('a')))
        except:
            self.genre = "No Genre"

    def __get_associated_names(self):
        try:
            self.associated_names = str(self.page_soup.find('div', {'id':'editassociated'})).split('<br/>')
            self.associated_names[0] = self.associated_names[0].split('>')[-1]
            self.associated_names[-1] = self.associated_names[-1].split('</')[0]
        except:
            self.associated_names = "No Associated Name Found"


    def __get_comments_on_all_pages(self):
        
        current_page_soup = self.page_soup
        while True:
            self.__get_comments_on_current_page(current_page_soup)

            if self.__is_last_page(current_page_soup):
                break
            else:
                current_page_link = current_page_soup.find('div', 
                        {'class':'w-comments-pagination'}).find('span', {'class':'current'})
                
                next_page_link = current_page_link.next_sibling.next_sibling['href']
                next_page_req = Request(next_page_link , headers={'User-Agent': 'Mozilla/5.0'})
                try:
                    next_page_res = urlopen(next_page_req)
                except:
                    self.status =-1
                    return

                next_webpage = next_page_res.read()
                current_page_soup = soup(next_webpage, "html.parser")

    def __is_last_page(self, page_soup):
        page_list = page_soup.find('div', {'class':'w-comments-pagination'})
        if not page_list.find('a', {'class':'next'}):
            return True
        else:
            return False


    def __get_comments_on_current_page(self, page_soup):
        
        try:
            for comment in page_soup.find_all('div',{'class':'w-comments-item-text'}):
                self.comments.append(self.__clean_comment(comment.text))
        except:
            self.comments.append("No Comments Found")

    def __clean_comment(self, comment):
        comment = re.sub(' +', ' ', comment).split('\n')
        temp_list = []
        for x in comment:
            x = x.strip()
            x = x.replace('<<less', '')
            x = x.replace('more>>', '')
            if len(x)==0 or x=='Spoiler' or  x=='[collapse]' or x=='<<less' or x=='more>>':
                continue
            temp_list.append(x)
        return '\n'.join(temp_list)