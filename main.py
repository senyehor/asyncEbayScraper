import asyncio
import json

from aiohttp import ClientSession

from product_urls_scraper import ProductLinksScraper
from products_info_bulk_scraper import (
    ProductInfo, ProductsInfoBulkScraper,
)

NIKE_AIR_FORCE_1_SEARCH_LINK = 'https://www.ebay.com/sch/i.html?_nkw=nike+air+force+1'


async def get_urls():
    async with ClientSession() as session:
        scraper = ProductLinksScraper(session, NIKE_AIR_FORCE_1_SEARCH_LINK)
        return await scraper.get_urls()


async def scrape_ebay_urls(urls: list[str]):
    async with ClientSession() as session:
        scraper = ProductsInfoBulkScraper(session, urls)
        return await scraper.fetch_products()


def write_products_info_to_file(products: list[ProductInfo], file_name: str):
    with open(file_name, 'w') as f:
        # begin json array
        f.write('[')
        for product in products[:-1]:
            product_info_as_json_str = json.dumps(product)
            product_info_with_separator = f'{product_info_as_json_str},\n'
            f.write(product_info_with_separator)
        last_product = json.dumps(products[-1])
        f.write(last_product)
        # close json array
        f.write(']')


async def main():
    urls = await get_urls()
    products = await scrape_ebay_urls(urls)
    write_products_info_to_file(products, 'products.json')

if __name__ == '__main__':
    asyncio.run(main())
