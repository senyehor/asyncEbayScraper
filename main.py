import asyncio

from aiohttp import ClientSession

from product_urls_scraper import ProductLinksScraper


async def get_urls():
    async with ClientSession() as session:
        scraper = ProductLinksScraper(session)
        return await scraper.get_urls()


async def main():
    urls = await get_urls()


if __name__ == '__main__':
    asyncio.run(main())
