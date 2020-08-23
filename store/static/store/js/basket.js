// TODO: replace to JS framework
BASKET_API_URL = "/store/api/v1/basket/";
BUY_URL = "/basket/buy/"
PATH_TO_STATIC = "/static/";


function recalculateTotalPrice() {
    let total_price = 0;
    $('.price').each(function(i, obj) {
        total_price += parseInt($(this).text());
    });
    $('div.total span#total_price').html(Math.trunc(total_price * 100) / 100);
    if (total_price == 0) {
        html = `
            <div class="total">
                <span>Ваша корзина пуста :( <a href="/">Начать покупки!</a></span>
            </div>
        `;
        $('#basket_content').html(html);
    }
}

function deleteRequest(id) {
    $.ajax({
        url: BASKET_API_URL + id + '/',
        type: "delete",
        headers: {"X-CSRFToken": getCookie('csrftoken')}
    })
    .done(function(response) {
        $('li#' + id).remove();
        recalculateTotalPrice();
    });
}

function changeCount(id, count) {
    $.ajax({
        url: BASKET_API_URL + id + '/',
        type: "patch",
        data: {count: parseInt($('li#' + id + ' span.count').html()) + parseInt(count)},
        headers: {"X-CSRFToken": getCookie('csrftoken')}
    })
    .done(function(response) {
        if (response.id) {
            $('li#' + id + ' span.price').html(`${Math.trunc(response.price * response.count * 100) / 100} руб.`);
            $('li#' + id + ' span.count').html(response.count);
        } else {
            $('li#' + id).remove();
        }
        recalculateTotalPrice();
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        for (i in jqXHR.responseJSON) {
            alert(jqXHR.responseJSON[i][0]);
            break;
        }
    });
}

$(document).ready(function() {
    $.ajax({
        url: BASKET_API_URL,
        type: "get",
    })
    .done(function(response) {
        function getProductCardHtml(link, image_link, name, product_id, basket_item_id, price, count) {
            static_url = window.location.protocol + "//" + window.location.host + PATH_TO_STATIC;
            return `<li id=${basket_item_id}>
                        <div class="product">
                            <a href="${link}"><img src="${static_url + image_link}"></a>
                            <a href="${link}">
                                <div class="info_product">
                                    <span class="name_product">${name}</span>
                                </div>
                            </a>
                            <div class="detail_product_area">
                                <span class="price">${Math.trunc(price * count * 100) / 100} руб.</span>
                                <div class="change_count">
                                    <button id="btn_minus" onclick="changeCount(${basket_item_id}, -1)">-</button>
                                    <span class="count">${count}</span>
                                    <button id="btn_plus" onclick="changeCount(${basket_item_id}, 1)">+</button>
                                </div>
                                <button id="btn_delete" onclick="deleteRequest(${basket_item_id})">Удалить</button>
                            </div>
                        </div>
                    </li>`;
        }
        if (response.length != 0) {
            let html = '<ul>';
            let total_price = 0;
            for (i in response) {
                 html += getProductCardHtml(response[i]['link'], response[i]['link_to_image'], response[i]['name'],
                                               response[i]['product'], response[i]['id'], response[i]['price'],
                                               response[i]['count']);
                 total_price += response[i]['price'];
            }
            html += `</ul>
                    <div class="total">
                        <span>К оплате: <span id="total_price">${Math.trunc(total_price * 100) / 100}</span> руб.</span>
                        <form method="post" action="${BUY_URL}">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                            <button type="submit" class="buy_btn">Оформить</button>
                        </form>
                    </div>`;
            $('#basket_content').html(html);
        } else {
            html = `
                <div class="total">
                    <span>Ваша корзина пуста :( <a href="/">Начать покупки!</a></span>
                </div>
            `;
            $('#basket_content').html(html);
        }
    });
});
