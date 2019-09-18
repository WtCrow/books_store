import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "books_store.settings")
django.setup()

from multiprocessing import Pool
from bs4 import BeautifulSoup
from store.models import *
from pathlib import Path
import requests
import random
import shutil


class ProductsParser:

    def __init__(self, part_url, subcategory_name, normalize_name, class_model):
        self.base_url = 'https://www.chitai-gorod.ru'
        self.part_url = part_url
        self.class_model = class_model

        if not Subcategory.objects.filter(name=subcategory_name):
            self.subcategory = Subcategory.objects.create(name=subcategory_name, normalize_name=normalize_name)
        else:
            self.subcategory = Subcategory.objects.get(name=subcategory_name)

    @staticmethod
    def _get_products_links(url):
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')

        tags_a = soup.find_all("a", attrs={"class": "product-card__img js-analytic-productlink"})
        hrefs = [tag_a.get('href') for tag_a in tags_a]

        return hrefs

    def _get_base_product(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        # get name product
        name = soup.find("h1", attrs={"class": "product__title js-analytic-product-title"}).contents[0]
        name = str(name).strip()

        if Product.objects.filter(name=name):
            return None

        # get image ref
        image_url = soup.find_all("img", attrs={"itemprop": "image"})[0].get('src')

        # save image
        # get last item url and init path variable
        image_name = image_url.split('/')[-1]
        full_image_name = f'store/image/products/{image_name}'
        path_to_file = Path(__file__).parents[0] / 'static' / full_image_name

        # download and save image to path_to_file
        response = requests.get(image_url, stream=True)
        with open(path_to_file, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

        descriptions = soup.find("div", attrs={"itemprop": "description"}).contents
        descriptions = [str(item).strip() for item in descriptions]
        descriptions = ''.join(descriptions)
        descriptions.replace('<br>', '')
        descriptions.replace('<br/>', '')
        descriptions.replace('</br>', '')

        price = soup.find("div", attrs={"class": "price"}).contents[0]
        price = float(price.split(' ')[0])  # '300 Р' -> 300

        product = Product(
            subcategory=self.subcategory,
            description=descriptions,
            price=price,
            name=name,
            count_in_stock=random.randint(1, 10),
            picture_name=full_image_name,
        )

        return product

    def parse(self, url):
        html = requests.get(url).text

        new_product = self._get_base_product(html)
        if not new_product:
            return
        new_product.save()

        obj = self.class_model.objects.create(product=new_product)

        return obj

    def parse_category(self):
        for i in range(1, 5):
            result_url = self.base_url + self.part_url + str(i)

            refs = self._get_products_links(result_url)
            refs = [self.base_url + ref for ref in refs]

            with Pool(24) as p:
                p.map(self.parse, refs)


class BooksParser(ProductsParser):

    def __init__(self, part_url, subcategory_name, normalize_name):
        super().__init__(part_url, subcategory_name, normalize_name, Book)

    def parse(self, url):
        book = super().parse(url)
        if not book:
            return
        html = requests.get(url).text

        soup = BeautifulSoup(html, 'html.parser')
        authors = soup.find("a", attrs={"class": "link product__author"}).contents
        authors = [str(author).strip() for author in authors]

        for author in authors:
            if not Author.objects.filter(name=author):
                book.authors.add(Author.objects.create(name=author))
            else:
                book.authors.add(Author.objects.get(name=author))

        return book


if __name__ == '__main__':
    # Books
    BooksParser(part_url='/catalog/books/programmirovaniye-9185/?page=',
                subcategory_name='programming', normalize_name='Программирование').parse_category()
    BooksParser(part_url='/catalog/books/klassicheskaya_i_sovremennaya_proza-9665/?page=',
                subcategory_name='fiction', normalize_name='Художественная литература').parse_category()
    BooksParser(part_url='/catalog/books/delovaya_literatura-8979/?page=',
                subcategory_name='business', normalize_name='Деловая литература').parse_category()

    # Creation
    ProductsParser(part_url='/catalog/hobbies/dekorirovaniye-18242/?page=',
                   subcategory_name='decoration', normalize_name='Декорирование',
                   class_model=Creation).parse_category()
    ProductsParser(part_url='/catalog/hobbies/instrumenty_i_prisposobleniya-18218/?page=',
                   subcategory_name='tool', normalize_name='Инструменты и приспособления',
                   class_model=Creation).parse_category()
    ProductsParser(part_url='/catalog/hobbies/raskhodnyye_materialy-18219/?page=',
                   subcategory_name='consumables', normalize_name='Расходные материалы',
                   class_model=Creation).parse_category()

    # Stationery
    ProductsParser(part_url='/catalog/kanctovars/bumazhnyye_izdeliya-2856/?page=',
                   subcategory_name='paper', normalize_name='Бумажные изделия',
                   class_model=Stationery).parse_category()
    ProductsParser(part_url='/catalog/kanctovars/pismennyye_prinadlezhnosti-2963/?page=',
                   subcategory_name='writing', normalize_name='Письменные приналежности',
                   class_model=Stationery).parse_category()

"""
-- DELETE FROM store_book_authors;
-- DELETE FROM store_author;
-- DELETE FROM store_book;
-- DELETE FROM store_product;
-- DELETE FROM store_subcategory;

SELECT *
FROM store_product INNER JOIN store_subcategory
ON store_product.subcategory_id = store_subcategory.id
WHERE store_subcategory.name = 
-- 'programming'
-- 'fiction'
-- 'business'

-- 'decoration'
-- 'tool'
-- 'consumables'

-- 'paper'
-- 'writing'

"""
