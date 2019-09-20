from django.contrib.auth.decorators import login_required
from django.views.generic import View, DetailView
from django.shortcuts import redirect
from django.db.models import F, aggregates, Sum, FloatField
from .models import *
from .utils import *


def index(request):
    """Renderer main page

    Show 3 scroll list various category products.
    Sections contains last added objects in category

    """
    books_models = Book.objects \
                       .select_related('product') \
                       .filter(product__count_in_stock__gt=0) \
                       .order_by('-product__date_pub')[:10]
    stationery_models = Stationery.objects \
                                  .select_related('product') \
                                  .filter(product__count_in_stock__gt=0) \
                                  .order_by('-product__date_pub')[:10]
    creations_models = Creation.objects \
                               .select_related('product') \
                               .filter(product__count_in_stock__gt=0) \
                               .order_by('-product__date_pub')[:10]
    return render(request, 'store/main.html', context={'books': books_models,
                                                       'stationery': stationery_models,
                                                       'creations': creations_models})


class BookCategory(View, CategoryMixin):
    """Page with products from book category"""

    class_model = Book
    title_part = 'Книги'
    category = 'books'


class CreationCategory(View, CategoryMixin):
    """Page with products from creation category"""

    class_model = Creation
    title_part = 'Творчество'
    category = 'creations'


class StationeryCategory(View, CategoryMixin):
    """Page with products from stationery category"""

    class_model = Stationery
    title_part = 'Канецелярские товары'
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


class Find(View, CategoryMixin):
    """Find in all products in fields name and description"""

    def get(self, request, category=None):
        # validation page param
        page = request.GET.get('page', None)
        page = self._get_valid_page(page)

        # get search text
        search_text = request.GET.get('search', '')

        title = f'Поиск по запросу "{search_text}"'

        # get start-end interval for select from data base
        to, do = self._get_interval(page)

        # get specific products
        # class_product_models - variable from store/util.py
        products = []
        for class_product_model in classes_product_models:
            products += class_product_model.objects.all().select_related('product')\
                                          .filter(Q(product__name__icontains=search_text)
                                                  | Q(product__description__icontains=search_text))\
                                          .order_by('product__date_pub')
        products = products[to:do]

        # get total count
        count = Product.objects\
                       .filter(Q(name__icontains=search_text)
                               | Q(description__icontains=search_text)).count()

        # get list numbers pages
        numbers_pages = self._get_numbers_pages(page, count) if len(products) > 0 else []

        # generate url for switch between pages
        current_url = reverse('search') + f'?search={search_text}'

        return render(request, self.template,
                      context={'title': title,
                               'total_count': count,
                               'products': products,
                               'numbers_pages': numbers_pages,
                               'current_page': page,
                               'current_url': current_url,
                               }
                      )


def custom_handler404(request, *args, **kwargs):
    code = '404'
    message = '404 запрашиваемый ресурс не найден'
    return render(request, 'store/message.html', context={'message': message, 'code': code})


@login_required
def add_in_basket(request, pk):
    """Add new product or inc count exist product in basket"""
    # validation pk
    if not pk.isdigit():
        raise Http404
    instance_product = get_object_or_404(Product, id=pk)
    # guard of request from url-panel
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
    """Decrement count product in basket"""
    instance_model = get_object_or_404(Product, id=pk)
    basket_item = BasketItem.objects.filter(Q(user=request.user) & Q(product=instance_model))
    # change count if count > 1
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
    instance_model = get_object_or_404(Product, id=pk)
    basket_item = BasketItem.objects.filter(Q(user=request.user) & Q(product=instance_model))
    if basket_item:
        basket_item[0].delete()

    return redirect('basket')


@login_required
def basket(request):
    """Show all product from user basket"""
    # get basket current user
    basket_items = BasketItem.objects.filter(user=request.user)

    # calculate total price
    sum_price = sum([basket_item.product.price * basket_item.count for basket_item in basket_items])

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


@login_required
def buy_product(request):
    """Handler for "buy" product.

    Clear basket, add order and row in M2M table.
    In background work signal.

    """
    # guard of request from url-panel
    basket_items = BasketItem.objects.filter(user=request.user)
    if not basket_items:
        redirect('index')

    # create order
    order = Order.objects.create(user=request.user, date_pub=datetime.now())
    # "add" products in custom M2M table ProductInOrder and set price and count values
    for basket_item in basket_items:
        ProductInOrder.objects.create(product=basket_item.product, order=order,
                                      count=basket_item.count,
                                      price=basket_item.product.price
                                      )
        basket_item.delete()

    return redirect('index')


@login_required
def story(request):
    """Handler for purchase story user

    Show list orders with total price
    and all products with link to product page

    In context send list in format:
    (('date': str, 'id': int, 'products': [...], 'total_price':float), ... )
    'products' get format:
    ({instance: ProductInOrder(), 'link': url}, ...)

    """

    orders = Order.objects.filter(user=request.user).order_by('-date_pub')

    orders_info = list()
    for order in orders:
        products_in_order = ProductInOrder.objects.filter(order=order)
        products = []
        for product_in_order in products_in_order:
            instance = product_in_order

            specific_object = get_specific_object(product_in_order.product)
            link = specific_object.get_absolute_url()

            products.append({'instance': instance, 'link': link})

        total_price = ProductInOrder.objects\
            .filter(order=order)\
            .aggregate(total_price=Sum(F('price') * F('count'), output_field=FloatField()))['total_price']
        # if NoneType.
        # In real work, order with 0 count product must not be, but if will appear (bug) then total_price = 0
        if not total_price:
            total_price = 0

        orders_info.append({'date': order.date_pub, 'id': order.id, 'products': products, 'total_price': total_price})

    return render(request, 'store/purchase_story.html', context={'orders': orders_info})
