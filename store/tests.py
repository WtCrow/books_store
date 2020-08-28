from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.options import Options
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from django.test.testcases import TestCase
from books_store.settings import BASE_DIR
from selenium import webdriver
from functools import partial
from store.models import *
from random import randint
from unittest import skip
import json

User = get_user_model()
INDEX_URL = 'index'
LOGIN_URL = 'login'
BASKET_URL = 'basket'
API_BASKET_URL = 'base_basket_api-list'


class TestShading:
    """Class for stop testing base-classes"""

    class BaseTest(StaticLiveServerTestCase):
        headless = True

        @classmethod
        def setUpClass(cls):
            super(TestShading.BaseTest, cls).setUpClass()
            options = Options()
            options.headless = cls.headless
            cls.selenium = webdriver.Firefox(options=options, executable_path=f'{BASE_DIR}/geckodriver')
            cls.selenium.implicitly_wait(1)

        @classmethod
        def setUp(cls):
            # test user
            cls.username = 'tester'
            cls.email = 'test@test.com'
            cls.password = 'test'
            cls.user = User.objects.create_user(username=cls.username, email=cls.email, password=cls.password)

            # test products
            test_subcategory = Subcategory.objects.create(name='test_subcategory',
                                                          normalize_name='norm_test_subcategory')

            test_author = Author.objects.create(name='test_author')

            for class_model in classes_product_models.values():
                count_products_in_category = 40
                name_class = class_model.__name__
                for i in range(0, count_products_in_category):
                    if class_model == Book:
                        specific_product = 'bk'
                    elif class_model == Stationery:
                        specific_product = 'st'
                    else:
                        specific_product = 'cr'
                    product = Product.objects.create(
                        subcategory=test_subcategory,
                        description='-',
                        price=100,
                        name=f'{name_class}_{i}',
                        count_in_stock=5,
                        picture_name='/test.jpg',
                        specific_product=specific_product,
                    )

                    specific_product = class_model.objects.create(
                        product=product
                    )
                    if class_model == Book:
                        specific_product.authors.add(test_author)

        @classmethod
        def tearDownClass(cls):
            cls.selenium.quit()
            super(TestShading.BaseTest, cls).tearDownClass()

        def login_by_selenium(self):
            """Find auth form and login"""
            username_field = self.selenium.find_element_by_id('id_username')
            username_field.send_keys(self.username)

            password_field = self.selenium.find_element_by_id('id_password')
            password_field.send_keys(self.password)

            self.selenium.find_element_by_id('id_login_button').click()

        def go_to_page(self, name_url, **kwargs):
            """Selenium go to page by name"""
            url = reverse(name_url, kwargs=kwargs)
            self.selenium.get('%s%s' % (self.live_server_url, url))

    class TestCategoryMixin(BaseTest):
        """Base class for test various products categories"""
        category_name_url = None
        title = None
        class_specific_product = None

        template = 'store/category.html'

        def _get_names_products(self, to, do):
            """Sorted by date publisher all specific products and return names products in range to-do"""
            names_products = self.class_specific_product.objects.filter(product__count_in_stock__gt=0) \
                                 .values_list('product__name', flat=True).order_by('-product__date_pub')[to:do]
            return names_products

        def test_template(self):
            """Test: use template store/category.html"""
            response = self.get_request(self.category_name_url)
            self.assertTemplateUsed(response, self.template)

        def test_content(self):
            """Test: page category contain first 15 product, that order by date publisher"""
            response = self.get_request(self.category_name_url)

            self.assertContains(response, self.title)

            names_products = self._get_names_products(0, 15)
            map(self.assertContains, names_products)

        def test_click_to_product(self):
            """Test: move to product page from page category"""
            self.go_to_page(self.category_name_url)

            link_to_product_page = self.selenium.find_elements_by_class_name('name_product')[0]
            name_product = link_to_product_page.text
            link_to_product_page.click()

            product_info = Product.objects.filter(name=name_product)\
                .values('name', 'description', 'price', 'count_in_stock')
            self.assertTrue(product_info, msg='Product from link not found in data base')

            assert_part = partial(self.assertIn, container=self.selenium.page_source)
            map(assert_part, product_info.values())

        def test_buy(self):
            """Click to buy button from page category before and after authorization"""
            basket_url = f'{self.live_server_url}{reverse(BASKET_URL)}'
            count_before_buy = BasketItem.objects.filter(user=self.user).count()

            # after auth
            self.go_to_page(self.category_name_url)
            buy_btn = self.selenium.find_elements_by_class_name('buy_btn')[0]
            buy_btn.click()
            self.assertNotEqual(self.selenium.current_url, basket_url, 'User move to basket page without auth')

            self.login_by_selenium()

            # before auth
            self.go_to_page(self.category_name_url)
            buy_btn = self.selenium.find_elements_by_class_name('buy_btn')[0]
            text_before_click = buy_btn.text
            buy_btn.click()
            text_after_click = buy_btn.text
            self.assertNotEqual(text_before_click, text_after_click, 'Text on button not changed')
            self.assertEqual(text_after_click, 'В корзине', 'Text on button not changed')

            # Basket not empty
            count_after_buy = BasketItem.objects.filter(user=self.user).count()
            self.assertNotEqual(count_after_buy, count_before_buy, 'Count basket item not changed after click '
                                                                   'by buy_btn')

        def get_request(self, name_url):
            return self.client.get(reverse(self.category_name_url))


class TestIndexView(TestShading.BaseTest):

    def test_template(self):
        """Test: use store/main.html"""
        response = self.client.get(reverse(INDEX_URL))
        self.assertTemplateUsed(response, 'store/main.html')

    def test_content(self):
        """index page contain 10 products each category, also books contains authors

        Products this is last 10 product (order by date publisher)

        """
        self.go_to_page(INDEX_URL)

        for cls in classes_product_models.values():
            # get names products
            product_names = cls.objects \
                       .filter(product__count_in_stock__gt=0) \
                       .order_by('-product__date_pub')\
                       .values('product__name')[:10].values_list('product__name', flat=True)
            self.assertTrue(product_names, 'Data base not contain data')

            items = self.selenium.find_elements_by_class_name('item')
            items = [item.get_attribute('innerHTML') for item in items]  # FireFoxWebElement -> html (str)

            for name in product_names:
                # find card, that contain name
                list_with_one_item = list(filter(lambda itm: name in itm, items))
                self.assertTrue(list_with_one_item, msg=f'Page not contains product {name}')

                if cls == Book:
                    # check authors for books names
                    item = list_with_one_item[0]
                    authors = Book.objects.get(product__name=name).authors.all()
                    self.assertTrue(authors, msg=f'Authors book: {name}, not found')
                    authors_names = [author.name for author in authors]
                    # check all authors
                    map(partial(self.assertIn, container=item), authors_names)

    def test_buy(self):
        """Click to buy button from main page before and after authorization"""
        part_basket_url = reverse(BASKET_URL)
        basket_url = f'{self.live_server_url}{part_basket_url}'
        part_login_url = reverse(LOGIN_URL)
        login_url = f'{self.live_server_url}{part_login_url}'
        count_before_buy = BasketItem.objects.filter(user=self.user).count()

        # before auth
        self.go_to_page(INDEX_URL)
        buy_buttons = self.selenium.find_elements_by_class_name('buy_btn')
        self.assertTrue(buy_buttons, 'Buy buttons not found')
        buy_button = buy_buttons[0]
        buy_button.click()

        self.assertNotEqual(self.selenium.current_url, basket_url, 'User move to basket page without auth')
        self.assertEqual(self.selenium.current_url, login_url, 'User not redirected to login page')
        self.login_by_selenium()

        # after auth
        self.go_to_page(INDEX_URL)
        buy_buttons = self.selenium.find_elements_by_class_name('buy_btn')
        self.assertTrue(buy_buttons, 'Buy buttons not found')
        buy_button = buy_buttons[0]
        text_before_click = buy_button.text
        buy_button.click()
        text_after_click = buy_button.text
        self.assertNotEqual(text_before_click, text_after_click, 'Text on button not changed')
        self.assertEqual(text_after_click, 'В корзине', 'Text on button not changed')

        # check empty basket
        self.go_to_page(BASKET_URL)
        count_after_buy = BasketItem.objects.filter(user=self.user).count()
        self.assertNotEqual(count_after_buy, count_before_buy, 'Count basket item not changed after click '
                                                               'by buy_btn')


class TestBooksCategory(TestShading.TestCategoryMixin):
    """Books category"""
    category_name_url = 'root_books'
    title = 'Книги'
    class_specific_product = Book


class TestStationeryCategory(TestShading.TestCategoryMixin):
    """Stationery category"""
    category_name_url = 'root_stationery'
    title = 'Канецелярские товары'
    class_specific_product = Stationery


class TestCreationsCategory(TestShading.TestCategoryMixin):
    """Creations category"""
    category_name_url = 'root_creations'
    title = 'Творчество'
    class_specific_product = Creation


class TestFind(TestShading.TestCategoryMixin):
    """Test find function."""
    category_name_url = 'search'
    search_text = 'book'
    title = 'Поиск по запросу &quot;book&quot;'

    def _get_names_products(self, to, do):
        """Get last names from all class products"""
        products = []

        for class_product_model in classes_product_models.values():
            products += class_product_model.objects.all()\
                .values('product__name') \
                .filter(Q(product__name__icontains=self.search_text)
                        | Q(product__description__icontains=self.search_text)) \
                .order_by('product__date_pub')
        products = products[to:do]

        names_products = [name['product__name'] for name in products]

        return names_products

    def go_to_page(self, _, **kwargs):
        part_url = reverse('search', kwargs=kwargs)
        url = f'{self.live_server_url}{part_url}?search={self.search_text}'
        self.selenium.get(url)

    def get_request(self, name_url):
        url = reverse(self.category_name_url)
        return self.client.get(f'{url}?search={self.search_text}')


class TestBasketAPI(TestCase):
    """Test basket REST API"""

    @classmethod
    def setUp(cls):
        # test user
        cls.username = 'tester'
        cls.email = 'test@test.com'
        cls.password = 'test'
        cls.user = User.objects.create_user(username=cls.username, email=cls.email, password=cls.password)

        # test products
        test_subcategory = Subcategory.objects.create(name='test_subcategory',
                                                      normalize_name='norm_test_subcategory')

        test_author = Author.objects.create(name='test_author')

        for class_model in classes_product_models.values():
            count_products_in_category = 40
            name_class = class_model.__name__
            for i in range(0, count_products_in_category):
                if class_model == Book:
                    specific_product = 'bk'
                elif class_model == Stationery:
                    specific_product = 'st'
                else:
                    specific_product = 'cr'
                product = Product.objects.create(
                    subcategory=test_subcategory,
                    description='-',
                    price=100,
                    name=f'{name_class}_{i}',
                    count_in_stock=5,
                    picture_name='/test.jpg',
                    specific_product=specific_product,
                )

                specific_product = class_model.objects.create(
                    product=product
                )
                if class_model == Book:
                    specific_product.authors.add(test_author)

    def test_post_request(self):
        """Test POST request basket url"""
        url = reverse(API_BASKET_URL)
        product = Product.objects.all()[0]

        response = self.client.post(url, data={'product': product.id, 'count': 1})
        self.assertEqual(response.status_code, 403, f'Not auth user use basket API. '
                                                    f'Status != 403, ({response.status_code})')

        self.client.login(username=self.username, password=self.password)
        count_products_test_user = BasketItem.objects.filter(user__username=self.username).count()
        self.assertEqual(count_products_test_user, 0, f'Basket not empty')

        response = self.client.post(url, data={'product': product.id, 'count': 1})
        self.assertEqual(response.status_code, 201, f'Auth user not use API. Status != 201, ({response.status_code})')
        count_products_test_user = BasketItem.objects.filter(user__username=self.username).count()
        self.assertEqual(count_products_test_user, 1, f'Basket is empty')

    def test_post_overflow_product_count(self):
        """Test POST request with large count"""
        url = reverse(API_BASKET_URL)
        product = Product.objects.all()[0]
        self.client.login(username=self.username, password=self.password)
        count_products_test_user = BasketItem.objects.filter(user__username=self.username).count()
        self.assertEqual(count_products_test_user, 0, f'Basket not empty')

        response = self.client.post(url, data={'product': product.id, 'count': 500})
        self.assertEqual(response.status_code, 400, f'Status bad request != 400, ({response.status_code})')
        count_products_test_user = BasketItem.objects.filter(user__username=self.username).count()
        self.assertEqual(count_products_test_user, 0, f'Basket is not empty')

    def test_get_request(self):
        """Test GET request basket url"""
        self.client.login(username=self.username, password=self.password)

        user = User.objects.get(username=self.username)
        self.assertEqual(BasketItem.objects.filter(user=user).count(), 0, 'Basket not empty')

        # create BasketItems for 3 products, set and save random count for check count next
        count_product_in_basket = dict()
        basket_items = list()
        for i in range(0, 3):
            product = Product.objects.all()[i]
            count_product_in_basket[product.id] = randint(0, 5)
            basket_items.append(BasketItem(user=user, count=count_product_in_basket[product.id], product=product))
        BasketItem.objects.bulk_create(basket_items)

        url = reverse(API_BASKET_URL)
        response = self.client.get(url)
        data = json.loads(response.content)
        for basket_item in data:
            response_product = basket_item['product']
            response_count = basket_item['count']
            self.assertIn(response_product, count_product_in_basket, f'Unknown product in basket '
                                                                     f'{response_product}')
            self.assertEqual(count_product_in_basket[response_product], response_count,
                             f'Count in basket not equal count from response '
                             f'({count_product_in_basket[response_product]} != {response_count}')

    def test_patch_request(self):
        """Test PATCH request basket url"""
        self.client.login(username=self.username, password=self.password)

        user = User.objects.get(username=self.username)
        self.assertEqual(BasketItem.objects.filter(user=user).count(), 0, 'Basket is not empty')
        old_count, new_count = 3, 5
        item = BasketItem.objects.create(user=user, count=old_count, product=Product.objects.all()[0])
        url = f'{reverse(API_BASKET_URL)}{item.id}/'
        self.client.patch(url, data={'count': new_count}, content_type='application/json')
        item = BasketItem.objects.get(pk=item.id)
        self.assertEqual(new_count, item.count)

    def test_patch_overflow_product_count(self):
        """Test PATCH request with large count"""
        self.client.login(username=self.username, password=self.password)
        user = User.objects.get(username=self.username)
        item = BasketItem.objects.create(user=user, count=1, product=Product.objects.all()[0])
        old_count = item.count

        url = f'{reverse(API_BASKET_URL)}{item.id}/'
        response = self.client.patch(url, data={'count': 500}, content_type='application/json')
        self.assertEqual(response.status_code, 400, f'Status bad request != 400, ({response.status_code})')
        new_count = BasketItem.objects.get(pk=item.id).count
        self.assertEqual(new_count, old_count, f'Count changed')

    def test_patch_if_count_zero_then_delete(self):
        """Test: if send PATCH request with count == 0, then delete basket item"""
        self.client.login(username=self.username, password=self.password)
        user = User.objects.get(username=self.username)
        item = BasketItem.objects.create(user=user, count=1, product=Product.objects.all()[0])

        url = f'{reverse(API_BASKET_URL)}{item.id}/'
        response = self.client.patch(url, data={'count': 0}, content_type='application/json')
        self.assertEqual(response.status_code, 200, f'Status bad request != 400, ({response.status_code})')
        item_after_patch = BasketItem.objects.filter(id=item.id)
        self.assertFalse(item_after_patch, f'Object not deleted')

    def test_delete_request(self):
        """Test DELETE request basket url"""
        self.client.login(username=self.username, password=self.password)

        user = User.objects.get(username=self.username)
        self.assertEqual(BasketItem.objects.filter(user=user).count(), 0, 'Basket not empty')
        item = BasketItem.objects.create(user=user, count=1, product=Product.objects.all()[0])
        url = f'{reverse(API_BASKET_URL)}{item.id}/'
        self.client.delete(url, content_type='application/json')
        count_items = BasketItem.objects.filter(pk=item.id).count()
        self.assertEqual(count_items, 0)
