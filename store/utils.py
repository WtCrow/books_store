from django.shortcuts import render, reverse, get_object_or_404
from django.http import Http404
from .models import Subcategory


class CategoryMixin:
    class_model = None
    title_part = None
    category = None

    template = 'store/category.html'
    count_product_at_page = 12

    def _get_numbers_pages(self, current_page, total_products_count):
        """return list int with numbers pages

        ['current', 'next'] | ['pre', 'current', 'next'] | ['pre', 'current'],

        :param current_page: current page
        :param total_products_count: count all products in DB for this category

        """
        numbers_pages = []

        if current_page > 1:
            numbers_pages.append(current_page - 1)
        numbers_pages.append(current_page)
        if total_products_count - current_page * self.count_product_at_page > 0:
            numbers_pages.append(current_page + 1)

        return numbers_pages

    @staticmethod
    def _get_valid_page(page):
        if page:
            if not page.isdigit():
                raise Http404
            else:
                page = int(page)
        else:
            page = 1

        return page

    def _get_products(self, to, do, subcategory=None):
        if subcategory:
            products_models = self.class_model.objects.all() \
                               .select_related('product') \
                               .filter(product__count_in_stock__gt=0) \
                               .select_related('product__subcategory') \
                               .filter(product__subcategory__name=subcategory) \
                               .order_by('-product__date_pub')[to:do]
        else:
            products_models = self.class_model.objects.all() \
                               .select_related('product') \
                               .filter(product__count_in_stock__gt=0) \
                               .order_by('-product__date_pub')[to:do]

        return products_models

    def _get_count_products(self, subcategory=None):
        if subcategory:
            count = self.class_model.objects.all() \
                .select_related('product') \
                .filter(product__count_in_stock__gt=0) \
                .select_related('-product__subcategory') \
                .filter(product__subcategory__name=subcategory) \
                .count()
        else:
            count = self.class_model.objects.all() \
                .select_related('product') \
                .filter(product__count_in_stock__gt=0) \
                .count()

        return count

    def _get_interval(self, page):
        to = (self.count_product_at_page * (page - 1))
        do = (self.count_product_at_page * (page - 1)) + self.count_product_at_page
        return to, do

    def get(self, request, subcategory=None):
        page = request.GET.get('page', None)
        page = self._get_valid_page(page)

        category_model = None
        if subcategory:
            category_model = get_object_or_404(Subcategory, name=subcategory)
        title = self.title_part if not subcategory else f'{self.title_part} ({category_model.normalize_name})'

        to, do = self._get_interval(page)
        products_models = self._get_products(to, do, subcategory)
        count = self._get_count_products(subcategory)

        numbers_pages = self._get_numbers_pages(page, count) if len(products_models) > 0 else []

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
