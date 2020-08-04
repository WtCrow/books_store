from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, DetailView
from django.db.models import F, Sum, FloatField
from django.shortcuts import redirect
from .models import *
from .utils import *


def custom_handler404(request, *args, **kwargs):
    return render(request, 'store/message.html', context={'message': '404 запрашиваемый ресурс не найден', 'code': 404})


def index(request):
    """Renderer main page

    Show 3 lists various products category and sections with last added products.

    """
    books_models = Book.objects \
                       .filter(product__count_in_stock__gt=0) \
                       .order_by('-product__date_pub')[:10]
    stationery_models = Stationery.objects \
                                  .filter(product__count_in_stock__gt=0) \
                                  .order_by('-product__date_pub')[:10]
    creations_models = Creation.objects \
                               .filter(product__count_in_stock__gt=0) \
                               .order_by('-product__date_pub')[:10]
    return render(request, 'store/main.html', context={'books': books_models,
                                                       'stationery': stationery_models,
                                                       'creations': creations_models})


class BookCategory(CategoryMixin, View):
    """Page with book category"""
    class_model = Book
    part_title = 'Книги'
    category = 'books'


class CreationCategory(CategoryMixin, View):
    """Page with creation category"""
    class_model = Creation
    part_title = 'Творчество'
    category = 'creations'


class StationeryCategory(CategoryMixin, View):
    """Page with stationery category"""
    class_model = Stationery
    part_title = 'Канецелярские товары'
    category = 'stationery'


class BookPage(DetailView):
    """Page with specific book category product"""
    model = Book
    template_name = 'store/product.html'


class CreationPage(DetailView):
    """Page with specific creation category product"""
    model = Creation
    template_name = 'store/product.html'


class StationeryPage(DetailView):
    """Page with specific stationery category product"""
    model = Stationery
    template_name = 'store/product.html'


class Find(PageNumbersList, View):
    """Find products by text in name or description"""
    template = 'store/category.html'
    count_items_at_page = 15

    def get(self, request):
        # validation page GET-param
        page = request.GET.get('page', None)
        page = self._get_valid_page(page)

        # get start-end interval for select from data base
        to, do = self._get_interval(page)

        # get search text
        search_text = request.GET.get('search', '')
        title = f'Поиск по запросу "{search_text}"'

        # class_product_models - variable from store/models.py, contain all subclass Product model
        # In self.template need pass specific product class, also Product.objects.filter no way
        products = []
        for class_product_model in classes_product_models:
            products += class_product_model.objects.all().filter(Q(product__name__icontains=search_text)
                                                                 | Q(product__description__icontains=search_text))\
                .order_by('-product__date_pub')
        products = products[to:do]

        # get total count
        count = Product.objects.filter(Q(name__icontains=search_text) | Q(description__icontains=search_text)).count()

        # get list numbers pages
        numbers_pages = self._get_numbers_pages(page, count)

        # generate url for switch between pages
        current_url = reverse('search') + f'?search={search_text}&page='

        return render(request, self.template,
                      context={'title': title,
                               'total_count': count,
                               'products': products,
                               'numbers_pages': numbers_pages,
                               'current_page': page,
                               'current_url': current_url,
                               }
                      )


@login_required
def basket(request):
    """Show all product from user basket"""

    # calculate total price in one SQL query
    sum_price = BasketItem.objects.filter(user=request.user)\
        .aggregate(sum_price=Sum(F('product__price') * F('count'), output_field=FloatField()))['sum_price']

    # get basket current user
    basket_items = BasketItem.objects.filter(user=request.user)
    # get all specific product classes (Book, Creation ...) from user basket
    products_and_links = []

    for basket_item in basket_items:
        product = basket_item.product

        specific_object = get_specific_object(product)
        link = specific_object.get_absolute_url()

        products_and_links.append({'instance': product,
                                   'link': link,
                                   'count': basket_item.count,
                                   })

    return render(request, 'store/basket.html', context={'products': products_and_links,
                                                         'sum_price': sum_price,
                                                         })


# TODO: change to POST, UPDATE, DELETE
@login_required
def add_in_basket(request, pk):
    """Add new product or inc count exist product in basket"""
    # validation pk
    if not pk.isdigit():
        raise Http404
    instance_product = get_object_or_404(Product, id=pk)
    # guard of bad request from url-panel
    if instance_product.count_in_stock <= 0:
        raise Http404

    # add new basket item or inc exist basket item
    basket_item = BasketItem.objects.filter(Q(user=request.user) & Q(product=instance_product))
    if basket_item:
        basket_item = basket_item[0]
        if instance_product.count_in_stock >= basket_item.count + 1:
            basket_item.count = F('count') + 1
            basket_item.save()
    else:
        BasketItem.objects.create(user=request.user, product=instance_product, count=1)

    return redirect('basket')


@login_required
def sub_from_basket(request, pk):
    """Decrement count or delete product in basket"""
    # validation pk
    if not pk.isdigit():
        raise Http404
    product = get_object_or_404(Product, id=pk)
    basket_item = BasketItem.objects.filter(Q(user=request.user) & Q(product=product))

    if basket_item:
        if basket_item[0].count <= 1:
            basket_item[0].delete()
        else:
            basket_item[0].count = F('count') - 1
            basket_item[0].save()

    return redirect('basket')


@login_required
def delete_from_basket(request, pk):
    """Delete product from basket"""
    # validation pk
    if not pk.isdigit():
        raise Http404
    instance_model = get_object_or_404(Product, id=pk)
    basket_item = BasketItem.objects.filter(Q(user=request.user) & Q(product=instance_model))
    if basket_item:
        basket_item[0].delete()

    return redirect('basket')


@login_required
def buy_product(request):
    """Handler for "buy" product.

    Clear basket, create Order and some ProductInOrder (M2M table).
    (In background work signal -> store/models.py change_count_in_stock)

    """
    basket_items = BasketItem.objects.filter(user=request.user)
    # guard of bad request from url-panel
    if not basket_items:
        return redirect('index')

    # create order
    order = Order.objects.create(user=request.user, date_pub=timezone.now())
    # add products in custom M2M table ProductInOrder
    for basket_item in basket_items:
        ProductInOrder.objects.create(product=basket_item.product, order=order,
                                      count=basket_item.count,
                                      price=basket_item.product.price
                                      )
        basket_item.delete()

    message = """Так как это только демонстрационный сайт, для того, чтобы показать мои навыки работы с Django, 
              работа с платежными API (и, наверное, API служб доставки) опущена. Вы можете увидеть, что история 
              ваших покупок обновилась, а товара стало меньше. Так же, если вы зарегистрировали 2 профиля и 
              добавили одинаковые товары в корзины, корзина другого профиля, могла измениться."""

    return render(request, 'store/message.html', context={'message': message})
# TODO: change to POST, UPDATE, DELETE


class StoryPurchase(LoginRequiredMixin, PageNumbersList, View):
    template = 'store/purchase_story.html'
    count_items_at_page = 15

    def get(self, request):
        """Handler for user purchase story

        Show list orders with total price and all products with link to product page

        """
        # validation GET-page param
        page = request.GET.get('page', None)
        page = self._get_valid_page(page)

        # get start-end interval for select from data base
        to, do = self._get_interval(page)

        # get orders and count orders this user
        orders = Order.objects.filter(user=request.user).order_by('-date_pub')[to:do]
        count = Order.objects.filter(user=request.user).count()

        # press data about order
        orders_info = list()
        for order in orders:
            # get information about each product in current order
            products_in_order = ProductInOrder.objects.filter(order=order)
            products = []
            for product_in_order in products_in_order:
                instance = product_in_order

                # get link to product page
                specific_object = get_specific_object(product_in_order.product)
                link = specific_object.get_absolute_url()

                # ProductInOrder() and url to page this product
                products.append({'instance': instance, 'link': link})

            # calculate total price this order in one SQL query
            total_price = ProductInOrder.objects\
                .filter(order=order)\
                .aggregate(total_price=Sum(F('price') * F('count'), output_field=FloatField()))['total_price']

            orders_info.append({'date': order.date_pub, 'id': order.id, 'products': products,
                                'total_price': total_price})

        # line for change current page
        numbers_pages = self._get_numbers_pages(page, count)

        # url for buttons that change current number page
        current_url = '%s?page=' % reverse('story')

        return render(request, self.template,
                      context={'orders': orders_info,
                               'numbers_pages': numbers_pages,
                               'current_page': page,
                               'current_url': current_url,
                               'count': count,
                               }
                      )
