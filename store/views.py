from django.shortcuts import render, HttpResponse


def index(request):
    return render(request, 'store/main.html', context={})


def products(request):
    return render(request, 'store/products.html', context={})


def product(request):
    return render(request, 'store/product.html', context={})


def basket(request):
    return render(request, 'store/basket.html', context={})


def profile(request):
    return render(request, 'store/profile.html', context={})


def auth(request):
    return render(request, 'store/auth.html', context={})


def logout(request):
    return HttpResponse()


def handler404(request, *args, **argv):
    message = 'Запрошенный ресурс не найден.'
    return render(request, 'store/message.html', context={message: message}, status=404)
