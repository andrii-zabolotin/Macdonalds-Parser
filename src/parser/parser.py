import asyncio
import json
import logging
from bs4 import BeautifulSoup as BS
from playwright.async_api import async_playwright, Page


logging.basicConfig(filename='parser.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s - line: %(lineno)d')

url = 'https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html'


async def fetch_product_links(page: Page):
    logging.info("Parsing product links.")
    await page.goto(url=url)
    await page.wait_for_load_state()

    response = await page.content()
    html = BS(response, 'html.parser')

    product_links = html.find_all('a', class_='cmp-category__item-link')
    links = ['https://www.mcdonalds.com' + link.get('href') + '#accordion-29309a7a60-item-9ea8a10642' for link in product_links]

    logging.info(f"Found {len(links)} product links.")
    return links


async def get_info_about_product(html: BS):
    try:
        name = html.select('.cmp-product-details-main__heading-title')[0].text
        description = html.select('.cmp-product-details-main__description')[0].text
        nutrition = html.select('.cmp-nutrition-summary__heading-primary-item')
        calories = nutrition[0].select('.value span')[2].text
        fats = nutrition[1].select('.value span')[2].text
        carbs = nutrition[2].select('.value span')[2].text
        proteins = nutrition[3].select('.value span')[2].text
        additional_nutrition = html.select('.cmp-nutrition-summary__details-column-view-mobile .label-item')
        unsaturated_fats = additional_nutrition[0].select('.value span')[0].text.split('/')[0]
        sugar = additional_nutrition[1].select('.value span')[0].text.split('/')[0]
        salt = additional_nutrition[2].select('.value span')[0].text.split('/')[0]
        portion = additional_nutrition[3].select('.value span')[0].text.split('/')[0]
    except Exception as e:
        logging.error(f"Error extracting data: {e}")
        return None

    return {
        'name': name.strip().replace('\xa0', ' '),
        'description': description.strip().replace('\xa0', ' '),
        'calories': calories.strip(),
        'fats': fats.strip(),
        'carbs': carbs.strip(),
        'proteins': proteins.strip(),
        'unsaturated_fats': unsaturated_fats.strip(),
        'sugar': sugar.strip(),
        'salt': salt.strip(),
        'portion': portion.strip(),
    }


async def main():
    data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        links = await fetch_product_links(page=page)

        for link in links:
            await page.goto(link)
            await page.wait_for_selector('.cmp-nutrition-summary__heading-primary-item', timeout=5000)
            response = await page.content()
            html = BS(response, 'html.parser')

            while html.select('.cmp-nutrition-summary__heading-primary-item')[0].select('.value span')[2].text == '0':
                logging.warning(f"{link}: data isn't loaded, reloading.")
                response = await page.content()
                html = BS(response, 'html.parser')

            logging.info(f"{link}: Extracting product information")
            data.append(await get_info_about_product(html=html))

        await browser.close()

    logging.info(f"Writing data for {len(data)} products to data.json.")
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

asyncio.run(main())
