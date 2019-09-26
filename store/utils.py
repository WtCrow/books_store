from django.shortcuts import render, reverse, get_object_or_404
from .models import Subcategory, classes_product_models
from django.http import Http404


class BaseNumbersPage:
    count_product_at_page = None

    def _get_numbers_pages(self, current_page, total_products_count):
        """return list int with numbers pages

        ['current', 'next'] | ['pre', 'current', 'next'] | ['pre', 'current'],

        :param current_page: current page
        :param total_products_count: count all products in DB for this category

        """
        numbers_pages = []

        # pre
        if current_page > 1:
            numbers_pages.append(current_page - 1)
        # current
        numbers_pages.append(current_page)
        # next
        if total_products_count - current_page * self.count_product_at_page > 0:
            numbers_pages.append(current_page + 1)

        return numbers_pages

    @staticmethod
    def _get_valid_page(page):
        """validation GET-param page"""
        if page:
            if not page.isdigit():
                raise Http404
            return int(page)
        return 1

    def _get_interval(self, page):
        """Return start and end indexes for models depending on the page"""
        to = (self.count_product_at_page * (page - 1))
        do = (self.count_product_at_page * (page - 1)) + self.count_product_at_page
        return to, do


class CategoryMixin(BaseNumbersPage):
    """Show count_product_at_page products at page"""

    class_model = None
    title_part = None
    category = None

    template = 'store/category.html'
    count_product_at_page = 15

    def _get_products(self, to, do, subcategory=None):
        """Return QuerySet with products

        Return products to - do, which the order by date_pub
        with taking into subcategory if != None

        :param to: start index
        :param do: end index
        :param subcategory: subcategory field
        :return: QuerySet
        """
        if subcategory:
            products_models = self.class_model.objects \
                               .select_related('product') \
                               .filter(product__count_in_stock__gt=0) \
                               .select_related('product__subcategory') \
                               .filter(product__subcategory__name=subcategory) \
                               .order_by('-product__date_pub')[to:do]
        else:
            products_models = self.class_model.objects \
                               .select_related('product') \
                               .filter(product__count_in_stock__gt=0) \
                               .order_by('-product__date_pub')[to:do]

        return products_models

    def _get_count_products(self, subcategory=None):
        """Return QuerySet with products

        Return total count products in data base, with taking into subcategory if != None

        :param subcategory: subcategory field
        :return: int
        """
        if subcategory:
            count = self.class_model.objects \
                .select_related('product') \
                .filter(product__count_in_stock__gt=0) \
                .select_related('-product__subcategory') \
                .filter(product__subcategory__name=subcategory) \
                .count()
        else:
            count = self.class_model.objects \
                .select_related('product') \
                .filter(product__count_in_stock__gt=0) \
                .count()

        return count

    def get(self, request, subcategory=None):
        """Mixin renderer store/category.html template for specific class model

        In children class define class_model, which the get product field (class Product)
        At html is displayed models

        """
        # validation page
        page = request.GET.get('page', None)
        page = self._get_valid_page(page)

        # generate title and define subcategory
        category_model = None
        if subcategory:
            category_model = get_object_or_404(Subcategory, name=subcategory)
        title = self.title_part if not subcategory else f'{self.title_part} ({category_model.normalize_name})'

        # get interval start-end indexes for select data from data base
        to, do = self._get_interval(page)

        # get objects models
        products_models = self._get_products(to, do, subcategory)
        count = self._get_count_products(subcategory)

        # get list with numbers pages
        numbers_pages = self._get_numbers_pages(page, count) if len(products_models) > 0 else []

        # generate url for switch between pages
        roots = dict()
        roots['category'] = self.category
        if subcategory:
            roots['subcategory'] = subcategory
        current_url = reverse('root_category', kwargs=roots) + '?'

        return render(request, self.template,
                      context={'title': title,
                               'total_count': count,
                               'products': products_models,
                               'numbers_pages': numbers_pages,
                               'current_page': page,
                               'current_url': current_url,
                               }
                      )


def get_specific_object(product):
    """Get specific Product class and return specific object"""

    for class_product_model in classes_product_models:
        obj_model = class_product_model.objects.filter(product=product)
        if obj_model:
            return obj_model[0]
