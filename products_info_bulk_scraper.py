import asyncio
from asyncio import Semaphore
from typing import TypedDict

from aiohttp import ClientSession
from bs4 import BeautifulSoup


class ProductInfo(TypedDict):
    product_name: str
    product_link: str
    image_link: str
    seller_name: str
    price_dollars: float
    shipping_cost_dollars: float | None


class ProductsInfoBulkScraper:
    def __init__(self, session: ClientSession, product_links: list[str]):
        self.__PRODUCT_LINKS = product_links
        self.__session = session

    async def fetch_products(self) -> list[ProductInfo]:
        semaphore = asyncio.Semaphore(10)
        products = []
        fetch_products_tasks =[
            asyncio.create_task(
                self.__fetch_specific_product_info(link, products, semaphore),
            ) for link in
            self.__PRODUCT_LINKS
        ]
        await asyncio.gather(*fetch_products_tasks)
        return products

    async def __fetch_specific_product_info(
            self, link: str, products_info_list: list[ProductInfo], semaphore: Semaphore
    ):
        async with semaphore:
            async with self.__session.get(link) as result:
                result.raise_for_status()
                html = await result.text()
        soup = BeautifulSoup(html, 'lxml')
        product_info = await self.__parse_product_info(soup, link)
        products_info_list.append(product_info)

    async def __parse_product_info(
            self, soup: BeautifulSoup, url: str
    ) -> dict[str, str | float]:
        product_name = self.__parse_product_name(soup)
        seller_name = self.__parse_seller_name(soup)
        image_link = self.__parse_image_link(soup)
        # allows to "pause" parsing to start fetching some more pages
        await asyncio.sleep(0)
        price_dollars = self.__parse_price(soup)
        shipping_cost_dollars = self.__parse_shipping_cost(soup)
        return {
            'product_name':          product_name,
            'seller_name':           seller_name,
            'image_link':            image_link,
            'price_dollars':         price_dollars,
            'shipping_cost_dollars': shipping_cost_dollars,
            'product_link':          url
        }

    def __parse_product_name(self, soup: BeautifulSoup) -> str:
        _product_name_wrapper = soup.find(class_='x-item-title__mainTitle')
        return _product_name_wrapper \
            .find('span', class_='ux-textspans ux-textspans--BOLD') \
            .string

    def __parse_seller_name(self, soup: BeautifulSoup) -> str:
        _seller_name_div = soup.find('div', class_='x-sellercard-atf__info__about-seller')
        return _seller_name_div.find('span', class_='ux-textspans ux-textspans--BOLD').string

    def __parse_image_link(self, soup: BeautifulSoup) -> str:
        _image_div = soup.find('div', class_='ux-image-carousel-item image-treatment active image')
        return _image_div.find('img')['data-zoom-src']

    def __parse_price(self, soup: BeautifulSoup) -> float:
        price_wrapper_div = soup.find('div', attrs={'data-testid': 'x-price-section'})
        # check for converted price first, as it means main price is not in dollars
        if price_converted_to_dollars := price_wrapper_div.find('div', class_='x-price-approx'):
            _price_span = price_converted_to_dollars \
                .find('span', class_='x-price-approx__price') \
                .find('span')
            return float(_price_span.string.split('$')[-1])
        if price_in_dollars_span := price_wrapper_div \
                .find('div', class_='x-price-primary') \
                .find('span'):
            return float(price_in_dollars_span.string.split('$')[-1])
        raise Exception('did not find approximate price nor primary')

    def __parse_shipping_cost(self, soup: BeautifulSoup) -> float | None:
        shipping_wrapper_div = soup \
            .find('div', class_='ux-layout-section ux-layout-section--shipping') \
            .find('div', class_='ux-labels-values__values-content')
        # case with primary shipping cost not in dollars
        if shipping_cost_approximate_span := shipping_wrapper_div.find(
                'span', class_='ux-textspans ux-textspans--SECONDARY ux-textspans--BOLD'
        ):
            return float(shipping_cost_approximate_span.string.split('$')[-1].rstrip(')'))
        # case with no shipping
        if shipping_wrapper_div.find(
                'span', class_='ux-textspans ux-textspans--BOLD ux-textspans--NEGATIVE'
        ):
            return None
        if shipping_cost_in_dollars_span := shipping_wrapper_div.find(
                'span', class_='ux-textspans ux-textspans--BOLD'
        ):
            return float(shipping_cost_in_dollars_span.string.split('$')[-1])
        raise Exception('failed to parse shipping cost')
