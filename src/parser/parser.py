import asyncio
import json
import logging
import aiohttp

from bs4 import BeautifulSoup as BS


logging.basicConfig(filename='parser.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s - line: %(lineno)d')

url = 'https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html'


async def fetch_product_links(session: aiohttp.ClientSession):
    async with session.get(url=url) as response:
        response.raise_for_status()
        html = BS(await response.text(), 'html.parser')

    product_links = html.select('.cmp-category__item')
    links = ['https://www.mcdonalds.com/dnaapp/itemDetails?country=UA&language=uk&showLiveData=true&item=' + link.get('data-product-id') for link in product_links]

    logging.info(f"Found {len(links)} product links.")
    return links


async def get_info_about_product(link: str, session: aiohttp.ClientSession):
    async with session.get(url=link) as response:
        response.raise_for_status()
        result = await response.json()

    name = result['item']['item_name']
    if result['item']['description'] != {}:
        description = result['item']['description']
    else:
        description = ''
    calories = result['item']['nutrient_facts']['nutrient'][2]['value'] + ' ' + result['item']['nutrient_facts']['nutrient'][2]['uom_description']
    fats = result['item']['nutrient_facts']['nutrient'][3]['value'] + ' ' + result['item']['nutrient_facts']['nutrient'][3]['uom_description']
    carbs = result['item']['nutrient_facts']['nutrient'][4]['value'] + ' ' + result['item']['nutrient_facts']['nutrient'][4]['uom_description']
    proteins = result['item']['nutrient_facts']['nutrient'][5]['value'] + ' ' + result['item']['nutrient_facts']['nutrient'][5]['uom_description']
    unsaturated_fats = result['item']['nutrient_facts']['nutrient'][8]['value'] + ' ' + result['item']['nutrient_facts']['nutrient'][8]['uom_description']
    sugar = result['item']['nutrient_facts']['nutrient'][7]['value'] + ' ' + result['item']['nutrient_facts']['nutrient'][7]['uom_description']
    salt = result['item']['nutrient_facts']['nutrient'][6]['value'] + ' ' + result['item']['nutrient_facts']['nutrient'][6]['uom_description']
    portion = result['item']['nutrient_facts']['nutrient'][0]['value'] + ' ' + result['item']['nutrient_facts']['nutrient'][0]['uom_description']

    return {
            name: {
                'description': description,
                'calories': calories,
                'fats': fats,
                'carbs': carbs,
                'proteins': proteins,
                'unsaturated_fats': unsaturated_fats,
                'sugar': sugar,
                'salt': salt,
                'portion': portion,
            }
        }


async def main():
    async with aiohttp.ClientSession() as session:
        links = await fetch_product_links(session=session)

        tasks = [get_info_about_product(link=link, session=session) for link in links]
        results = await asyncio.gather(*tasks)

    data = {}
    for result in results:
        data.update(result)

    logging.info(f"Writing data for {len(data)} products to data.json.")
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

asyncio.run(main())
