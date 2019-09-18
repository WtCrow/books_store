from django.contrib.auth.decorators import login_required
from django.views.generic import View, DetailView
from django.shortcuts import redirect
from django.db.models import Q, F
from .models import *
from .utils import *


def index(request):
    books_models = Book.objects \
                       .select_related('product') \
                       .all() \
                       .order_by('-product__date_pub')[:10]
    stationery_models = Stationery.objects \
                                  .select_related('product') \
                                  .all() \
                                  .order_by('-product__date_pub')[:10]
    creations_models = Creation.objects \
                               .select_related('product') \
                               .all() \
                               .order_by('-product__date_pub')[:10]
    return render(request, 'store/main.html', context={'books': books_models,
                                                       'stationery': stationery_models,
                                                       'creations': creations_models})


class BookCategory(View, CategoryMixin):
    class_model = Book
    title_part = 'Книги'
    category = 'books'


class CreationCategory(View, CategoryMixin):
    class_model = Creation
    title_part = 'Творчество'
    category = 'creations'


class StationeryCategory(View, CategoryMixin):
    class_model = Stationery
    title_part = 'Канецелярские товары'
    category = 'stationery'


class BookPage(DetailView):
    model = Book
    template_name = 'store/product.html'


class CreationPage(DetailView):
    model = Creation
    template_name = 'store/product.html'


class StationeryPage(DetailView):
    model = Stationery
    template_name = 'store/product.html'


class Find(View, CategoryMixin):
    models_for_search = [Book, Stationery, Creation]

    @staticmethod
    def _search_in_models(class_model, text):
        finded_models = class_model.objects \
                                   .select_related('product') \
                                   .filter(Q(product__name__icontains=text)
                                           | Q(product__description__icontains=text)
                                           ).order_by('product__date_pub')
        return finded_models

    @staticmethod
    def _get_count_finded_models(class_model, text):
        count_finded_models = class_model.objects \
                                         .select_related('product') \
                                         .filter(Q(product__name__icontains=text)
                                                 | Q(product__description__icontains=text)
                                                 ).count()
        return count_finded_models

    def get(self, request, category=None):
        page = request.GET.get('page', None)
        page = self._get_valid_page(page)

        search_text = request.GET.get('search', '')

        title = f'Поиск по запросу "{search_text}"'

        to, do = self._get_interval(page)
        products_models = []
        count = 0

        for model_for_search in self.models_for_search:
            products_models += self._search_in_models(model_for_search, search_text)
            count += self._get_count_finded_models(model_for_search, search_text)

        products_models = products_models[to:do]

        numbers_pages = self._get_numbers_pages(page, count) if len(products_models) > 0 else []

        current_url = reverse('search') + f'?search={search_text}'

        return render(request, self.template,
                      context={'title': title,
                               'total_count': count,
                               'products': products_models,
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
    instance_model = get_object_or_404(Product, id=pk)
    basket_item = BasketItem.objects.filter(Q(user=request.user) & Q(product=instance_model))
    if basket_item:
        basket_item[0].count = F('count') + 1
        basket_item[0].save()
    else:
        BasketItem.objects.create(user=request.user, product=instance_model, count=1)

    return redirect('basket')


@login_required
def sub_from_basket(request, pk):
    instance_model = get_object_or_404(Product, id=pk)
    basket_item = BasketItem.objects.filter(Q(user=request.user) & Q(product=instance_model))
    if basket_item:
        if basket_item[0].count == 1:
            basket_item[0].delete()
        else:
            basket_item[0].count = F('count') - 1
            basket_item[0].save()

    return redirect('basket')


@login_required
def delete_from_basket(request, pk):
    instance_model = get_object_or_404(Product, id=pk)
    basket_item = BasketItem.objects.filter(Q(user=request.user) & Q(product=instance_model))
    if basket_item:
        basket_item[0].delete()

    return redirect('basket')


@login_required
def basket(request):
    basket_items = BasketItem.objects.filter(user=request.user)

    sum_price = sum([basket_item.product.price * basket_item.count for basket_item in basket_items])

    # TODO find best way :|
    concreting_models = [Book, Stationery, Creation]

    products_and_links = []

    for basket_item in basket_items:
        for concreting_model in concreting_models:
            concreting_model_instance = concreting_model.objects.filter(product=basket_item.product)
            if concreting_model_instance:
                products_and_links.append({'instance': basket_item.product,
                                           'link': concreting_model_instance[0].get_absolute_url(),
                                           'count': basket_item.count,
                                           })
                break

    return render(request, 'store/basket.html', context={'products': products_and_links,
                                                         'sum_price': sum_price,
                                                         })


@login_required
def buy_product(request):
    message = 'TODO'
    return render(request, 'store/message.html', context={'message': message})
