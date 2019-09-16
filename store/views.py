from django.views.generic import View, DetailView
from .utils import *
from .models import *


def index(request):
    books_models = Book.objects.all()[:10]
    stationery_models = Stationery.objects.all()[:10]
    creations_models = Creation.objects.all()[:10]
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


def custom_handler404(request, *args, **kwargs):
    code = '404'
    message = '404 запрашиваемый ресурс не найден'
    return render(request, 'store/message.html', context={'message': message, 'code': code})


class FindBook(View, FindInCategoryMixin):
    class_model = Book
    title_part = 'Канецелярские товары'
    category = 'books'


class FindCreation(View, FindInCategoryMixin):
    class_model = Creation
    title_part = 'Канецелярские товары'
    category = 'creation'


class FindStationery(View, FindInCategoryMixin):
    class_model = Stationery
    title_part = 'Канецелярские товары'
    category = 'stationery'
