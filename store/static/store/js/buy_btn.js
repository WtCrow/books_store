function toBasket() {
    window.location.href = '/basket';
}

function buyRequest(e, id) {
    if (!is_auth_user) {
        window.location.href = '/accounts/login';
        return;
    }
    $.ajax({
        url: "/store/api/v1/basket/",
        type: "post",
        data: {count: 1, product: id} ,
        headers: {"X-CSRFToken": getCookie('csrftoken')}
    })
    .always(function(jqXHR, textStatus) {
        if (textStatus == 'success' ||
            (jqXHR.responseJSON.error && jqXHR.responseJSON.error.filter(error => error.includes('already in basket')))) {
            e.textContent = 'В корзине';
            e.style.background='#aaea99';
            e.onclick = toBasket;
        }
    });
}
