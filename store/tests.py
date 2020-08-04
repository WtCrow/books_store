from selenium.webdriver.firefox.options import Options
from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from books_store.settings import BASE_DIR
from selenium import webdriver
from functools import partial
from store.models import *
from unittest import skip
import time

User = get_user_model()
BASKET_EMPTY_MESSAGE = 'Ваша корзина пуста'


class TestShading:
    """Class for stop testing base-classes"""

    class BaseTest(LiveServerTestCase):
        url_login = 'login'
        is_start_selenium = True

        @classmethod
        def setUpClass(cls):
            super(TestShading.BaseTest, cls).setUpClass()
            if cls.is_start_selenium:
                options = Options()
                options.headless = True

                cls.selenium = webdriver.Firefox(options=options, executable_path=f'{BASE_DIR}/geckodriver')
                cls.selenium.implicitly_wait(1)

        @classmethod
        def tearDownClass(cls):
            if cls.is_start_selenium:
                cls.selenium.quit()
            super(TestShading.BaseTest, cls).tearDownClass()

        def setUp(self):
            # test user
            self.username = 'tester'
            self.email = 'test@tst.tst'
            self.password = '123456'
            self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)

            # test products
            test_subcategory = Subcategory.objects.create(name='test_sc', normalize_name='norm_test_sc')

            test_author = Author.objects.create(name='test_author')

            for class_model in classes_product_models:
                count_products_in_category = 40
                name_class = class_model.__name__
                for i in range(0, count_products_in_category):
                    product = Product.objects.create(
                        subcategory=test_subcategory,
                        description='-',
                        price=100,
                        name=f'{name_class}_{i}',
                        count_in_stock=5,
                        picture_name='/test.jpg'
                    )

                    specific_product = class_model.objects.create(
                        product=product
                    )
                    if class_model == Book:
                        specific_product.authors.add(test_author)

        def login(self):
            """Find login form at current page and login test user"""
            username_field = self.selenium.find_element_by_id('id_username')
            username_field.send_keys(self.username)

            password_field = self.selenium.find_element_by_id('id_password')
            password_field.send_keys(self.password)

            self.selenium.find_element_by_id('id_login_button').click()

        def get_page(self, name_url, **kwargs):
            """Go to page with name_url in selenium"""
            url = reverse(name_url, kwargs=kwargs)
            self.selenium.get('%s%s' % (self.live_server_url, url))

        def get_response(self, name_url, **kwargs):
            """Get response to name url from django client"""
            url_path = reverse(name_url, kwargs=kwargs)
            response = self.client.get(url_path)
            return response

    class TestCategoryMixin(BaseTest):
        category_name_url = None
        title = None
        class_specific_product = None

        template = 'store/category.html'

        def _get_names_products(self, to, do):
            """Sorted by date publisher all specific products and return names products in range to-do"""
            products = self.class_specific_product.objects.filter(product__count_in_stock__gt=0) \
                           .values('product__name').order_by('-product__date_pub')[to:do]
            names_products = [name['product__name'] for name in products]
            return names_products

        def test_template(self):
            """Test: use template store/category.html"""
            response = self.get_response(self.category_name_url)
            self.assertTemplateUsed(response, self.template)

        def test_content(self):
            """Test: page category contain first 15 product, that order by date publisher"""
            response = self.get_response(self.category_name_url)

            self.assertContains(response, self.title)

            names_products = self._get_names_products(0, 15)
            map(self.assertContains, names_products)

        def test_click_to_product(self):
            """Test: move to product page from page category"""
            self.get_page(self.category_name_url)

            link_to_product_page = self.selenium.find_elements_by_class_name('name_product')[0]
            name_product = link_to_product_page.text
            link_to_product_page.click()

            product_info = Product.objects.filter(name=name_product)\
                .values('name', 'description', 'price', 'count_in_stock')
            self.assertTrue(product_info, msg='Product from link not found in data base')

            assert_part = partial(self.assertIn, container=self.selenium.page_source)
            map(assert_part, product_info.values())

        def test_buy(self):
            """Click to buy button from page category after and before authorization"""
            par_basket_url = reverse('basket')
            basket_url = f'{self.live_server_url}{par_basket_url}'

            # after auth
            self.get_page(self.category_name_url)
            link_to_product_page = self.selenium.find_elements_by_class_name('buy_btn')[0]
            link_to_product_page.click()
            self.assertNotEqual(self.selenium.current_url, basket_url, 'User move to basket page without auth')

            self.login()

            # before auth
            self.get_page(self.category_name_url)
            link_to_product_page = self.selenium.find_elements_by_class_name('buy_btn')[0]
            link_to_product_page.click()
            self.assertEqual(self.selenium.current_url, basket_url, "Auth user don't buy product")

            # Basket not empty
            self.assertNotIn(self.selenium.page_source, BASKET_EMPTY_MESSAGE, 'Корзина пуста')


class TestIndexView(TestShading.BaseTest):

    def _buy_product_from_main_page(self):
        """Find and click button for buy product"""
        self.get_page('index')
        buy_buttons = self.selenium.find_elements_by_class_name('buy_btn')
        self.assertTrue(buy_buttons, 'Buy buttons not found')
        buy_button = buy_buttons[0]
        buy_button.click()

    def test_template(self):
        """Test: use store/main.html"""
        response = self.get_response('index')
        self.assertTemplateUsed(response, 'store/main.html')

    def test_content(self):
        """index page contain 10 products each category book contains authors

        Product this is last 10 product (order by date publisher)

        """
        self.get_page('index')

        for cls in classes_product_models:
            # get names products
            products_names = cls.objects \
                       .filter(product__count_in_stock__gt=0) \
                       .order_by('-product__date_pub')\
                       .values('product__name')[:10]
            products_names = [name['product__name'] for name in products_names]
            self.assertTrue(products_names, 'Data base not contain data')

            items = self.selenium.find_elements_by_class_name('item')
            items = [item.get_attribute('innerHTML') for item in items]  # FireFoxWebElement -> html (str)

            for name in products_names:
                list_with_one_item = list(filter(lambda itm: name in itm, items))
                self.assertTrue(list_with_one_item, msg=f'Page not contains product {name}')

                if cls == Book:
                    # check authors for books names
                    item = list_with_one_item[0]
                    authors = Book.objects.get(product__name=name).authors.all()
                    self.assertTrue(authors)
                    authors_names = [author.name for author in authors]
                    # check all authors for book
                    assert_part = partial(self.assertIn, container=item)
                    map(assert_part, authors_names)

    def test_buy(self):
        """Click to buy button from main page before and after authorization"""
        part_basket_url = reverse('basket')
        basket_url = f'{self.live_server_url}{part_basket_url}'

        # before auth
        self._buy_product_from_main_page()
        self.assertNotEqual(self.selenium.current_url, basket_url, 'User move to basket page without auth')

        self.login()

        # after auth
        self._buy_product_from_main_page()
        self.assertEqual(self.selenium.current_url, basket_url, "Auth user don't buy product")

        # check empty basket
        self.assertNotIn(self.selenium.page_source, BASKET_EMPTY_MESSAGE, 'Корзина пуста')


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

        for class_product_model in classes_product_models:
            products += class_product_model.objects.all()\
                .values('product__name') \
                .filter(Q(product__name__icontains=self.search_text)
                        | Q(product__description__icontains=self.search_text)) \
                .order_by('product__date_pub')
        products = products[to:do]

        names_products = [name['product__name'] for name in products]

        return names_products

    def get_page(self, _, **kwargs):
        part_url = reverse('search', kwargs=kwargs)
        url = '%s%s?search=%s' % (self.live_server_url, part_url, self.search_text)
        self.selenium.get(url)

    def get_response(self, name_url, **kwargs):
        """Get response to name url from django client"""
        part_url = reverse(name_url, kwargs=kwargs)
        response = self.client.get(part_url, {'search': self.search_text})
        return response


class TestBasket(TestShading.BaseTest):
    """Test add and sub from basket"""

    is_start_selenium = False

    url_basket = 'basket'
    url_add = 'add_in_basket'
    url_sub = 'sub_from_basket'

    def test_add(self):
        """Check function add one product in basket"""
        BasketItem.objects.filter(user=self.user).all().delete()

        # auth
        self.client.login(username=self.username, password=self.password)

        # check empty basket
        response = self.get_response(self.url_basket)
        self.assertContains(response, BASKET_EMPTY_MESSAGE)

        # add product with id=1
        product = Product.objects.all()[0]
        self.get_response(self.url_add, pk=product.id)

        # check not empty basket
        response = self.get_response(self.url_basket)
        self.assertNotContains(response, BASKET_EMPTY_MESSAGE)

    def test_overflow_add(self):
        """Check function add product in basket if call add function more than product in stock"""
        BasketItem.objects.filter(user=self.user).all().delete()

        # auth
        self.client.login(username=self.username, password=self.password)

        # check empty basket
        response = self.get_response(self.url_basket)
        self.assertContains(response, BASKET_EMPTY_MESSAGE)

        # add count_in_stock + 3 products
        product = Product.objects.all()[0]
        count_in_stock = product.count_in_stock

        for _ in range(0, count_in_stock + 3):
            self.get_response(self.url_add, pk=product.id)

        # check not empty basket
        response = self.get_response(self.url_basket)
        self.assertNotContains(response, BASKET_EMPTY_MESSAGE)

        # check count product in data base model
        count_product_in_basket = BasketItem.objects.get(Q(user=self.user) & Q(product=product)).count
        self.assertTrue(count_product_in_basket == count_in_stock, f'{count_product_in_basket} != {count_in_stock}')

    def test_sub(self):
        """Sub product from basket"""
        BasketItem.objects.filter(user=self.user).all().delete()
        product = Product.objects.all()[0]
        basket_item = BasketItem.objects.create(user=self.user, product=product, count=2)

        # auth
        self.client.login(username=self.username, password=self.password)

        # first sub
        self.get_response(self.url_sub, pk=product.id)
        self.assertEqual(basket_item.count, 2,
                         f'Count product in basket test user before sub_request {basket_item.count}')

        # second sub
        self.get_response(self.url_sub, pk=product.id)
        self.assertTrue(basket_item.count, f'Basket item not deleted. Count basket item == {basket_item.count}')

    def test_sub_from_empty_basket(self):
        """Sub product from empty basket"""
        BasketItem.objects.filter(user=self.user).all().delete()
        product = Product.objects.all()[0]

        # auth
        self.client.login(username=self.username, password=self.password)

        # check empty basket models
        basket_item_test_user = BasketItem.objects.filter(user=self.user)
        self.assertFalse(basket_item_test_user,
                         f'Basket test user contain products. Count = {basket_item_test_user.count()}')

        # sub
        response = self.get_response(self.url_sub, pk=product.id)

        full_url_basket = '%s%s' % (self.live_server_url, reverse(self.url_basket))
        # check user not redirect to basket
        self.assertNotEqual(response.url, full_url_basket, 'User redirect in basket')
        # check empty basket models
        self.assertFalse(basket_item_test_user,
                         f'Basket test user contain products. Count = {basket_item_test_user.count()}')
