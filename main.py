import asyncio

from aiohttp import ClientSession

from product_urls_scraper import ProductLinksScraper

NIKE_AIR_FORCE_1_SEARCH_LINK = 'https://www.ebay.com/sch/i.html?_nkw=nike+air+force+1'


async def get_urls():
    async with ClientSession() as session:
        scraper = ProductLinksScraper(session, NIKE_AIR_FORCE_1_SEARCH_LINK)
        return await scraper.get_urls()


async def main():
    urls = await get_urls()


if __name__ == '__main__':
    asyncio.run(main())
