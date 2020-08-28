from .models import Subcategory, classes_product_models, BasketItem, Book
from django.shortcuts import render, reverse, get_object_or_404
from django.views.generic import DetailView
from django.http import Http404


# TODO: replaced on DRF pagination
class PageNumbersList:
    """Methods for generate correct list page numbers"""
    count_items_at_page = None

    def _get_numbers_pages(self, current_page, total_products_count):
        """Return list int numbers pages

        ['current_page_num', 'next_page_num'] |
        ['pre_page_num', 'current_page_num', 'next_page_num'] |
        ['pre_page_num', 'current_page_num']

        :param current_page: current page
        :param total_products_count: count all products in DB by this category

        """
        numbers_pages = []

        # pre
        if current_page > 1:
            numbers_pages.append(current_page - 1)
        # current
        numbers_pages.append(current_page)
        # next
        if total_products_count - current_page * self.count_items_at_page > 0:
            numbers_pages.append(current_page + 1)

        return numbers_pages

    @staticmethod
    def _get_valid_page(page):
        """validation GET-param page"""
        if page:
            if not page.isdigit() or int(page) == 0:
                raise Http404
            return int(page)
        return 1

    def _get_interval(self, page):
        """Return start and end indexes for models on this page (order by -date_pub)"""
        to = (self.count_items_at_page * (page - 1))
        do = (self.count_items_at_page * (page - 1)) + self.count_items_at_page
        return to, do


class CategoryMixin(PageNumbersList):
    """Show products specific category with line for switch pages"""

    class_model = None
    part_title = None
    category = None

    template = 'store/category.html'
    count_items_at_page = 15

    def get(self, request, subcategory=None):
        """Mixin renderer store/category.html template for specific class model

        In children class define class_model, which the get product field
        At html is displayed models with line for switch pages

        """
        # validation page
        page = request.GET.get('page', None)
        page = self._get_valid_page(page)

        # get interval start-end indexes for select data from data base
        to, do = self._get_interval(page)

        # generate title and define subcategory
        category_model = None
        if subcategory:
            category_model = get_object_or_404(Subcategory, name=subcategory)
        title = self.part_title if not subcategory else f'{self.part_title} ({category_model.normalize_name})'

        # get QuerySet models and total count this products
        filters_dict = {'product__count_in_stock__gt': 0}
        if subcategory:
            filters_dict['product__subcategory__name'] = subcategory
        if request.user.is_authenticated:
            sql_table_name = self.class_model._meta.db_table
            select = {'is_in_basket': f"""
                SELECT EXISTS (SELECT *
                FROM store_basketitem
                INNER JOIN auth_user
                    ON auth_user.id = store_basketitem.user_id
                WHERE
                    store_basketitem.product_id = {sql_table_name}.product_id
                    AND store_basketitem.user_id = %s)
                """}
            select_params = (request.user.id, )
        else:
            select = {'is_in_basket': 'SELECT FALSE'}
            select_params = ()
        products_models = self.class_model.objects.filter(**filters_dict).order_by('-product__date_pub')\
                              .extra(select=select, select_params=select_params)[to:do]
        count = self.class_model.objects.filter(**filters_dict).order_by('-product__date_pub').count()

        numbers_pages = self._get_numbers_pages(page, count)

        # generate url for switch between pages
        roots = dict()
        roots['category'] = self.category
        if subcategory:
            roots['subcategory'] = subcategory
        current_url = '%s?page=' % reverse('root_category', kwargs=roots)

        return render(request, self.template,
                      context={'title': title,
                               'total_count': count,
                               'products': products_models,
                               'numbers_pages': numbers_pages,
                               'current_page': page,
                               'current_url': current_url,
                               }
                      )


class ProductPageMixin(DetailView):

    def get_context_data(self, **kwargs):
        context = super(ProductPageMixin, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_in_basket'] = BasketItem.objects.filter(product=self.get_object().product.id,
                                                                user=self.request.user).exists()
        return context


def get_specific_object(product):
    """Get specific Product class and return this object"""
    specific_model = classes_product_models[product.specific_product]
    return specific_model.objects.get(product=product)
