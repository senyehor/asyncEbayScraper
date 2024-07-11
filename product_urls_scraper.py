from aiohttp import ClientSession
from bs4 import BeautifulSoup


class ProductLinksScraper:

    def __init__(self, session: ClientSession, search_link: str):
        self.__session = session
        self.__search_link = search_link

    async def get_urls(self) -> list[str]:
        soup = await self.__get_soup_from_page()
        return self.__extract_product_urls_from_soup(soup)

    def __extract_product_urls_from_soup(self, soup: BeautifulSoup) -> list[str]:
        products_container = soup.find(id='srp-river-results')
        products_a_tags_with_product_link = products_container.find_all('a', class_='s-item__link')
        # could be done prettier, without inline splitting and leaving just the first part
        # but left like that for speed and test task simplicity
        return [a_tag['href'].split('?')[0] for a_tag in products_a_tags_with_product_link]

    async def __get_soup_from_page(self) -> BeautifulSoup:
        async with self.__session.get(self.__search_link) as result:
            html = await result.text()
            soup = BeautifulSoup(html, 'html.parser')
            self.__check_request_is_not_blocked(soup)
            return soup

    def __check_request_is_not_blocked(self, soup: BeautifulSoup):
        if soup.title.string.lower() == 'access denied':
            raise Exception('ebay blocked request')
