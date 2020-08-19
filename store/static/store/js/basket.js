// TODO: replace to JS framework
BASKET_API_URL = "/store/api/v1/basket/";
STATIC_URL = "/static/";

$.ajax({
    url: BASKET_API_URL,
    type: "get",
    success: function (response) {
        function get_product_card_html(link, image_link, name, product_id, basket_item_id, price, count) {
            static_url = window.location.protocol + "//" + window.location.host + STATIC_URL;
            return `<li>
                        <div class="product">
                            <a href="${link}"><img src="${static_url + image_link}"></a>
                            <a href="${link}">
                                <div class="info_product">
                                    <span class="name_product">${name}</span>
                                </div>
                            </a>
                            <div class="detail_product_area">
                                <span>${Math.trunc(price * count * 100) / 100} руб.</span>
                                <div class="change_count">
                                    <button id="btn_minus">-</button>
                                    <span>${count}</span>
                                    <button id="btn_plus">+</button>
                                </div>
                                <button id="btn_delete">Удалить</button>
                            </div>
                        </div>
	                </li>`;
        }
        if (response.length != 0) {
            let html = '<ul>';
            let total_price = 0;
            for (i in response) {
                 html += get_product_card_html(response[i]['link'], response[i]['link_to_image'], response[i]['name'],
                                               response[i]['product'], response[i]['id'], response[i]['price'],
                                               response[i]['count']);
                 total_price += response[i]['price'];
            }
            html += `</ul>
            		<div class="total">
					    <span>К оплате: ${Math.trunc(total_price * 100) / 100} руб.</span>
					    <button class="buy_btn">Оформить</button>
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
    },
    error: function(jqXHR, textStatus, errorThrown) {
       console.log(textStatus, errorThrown);
    }
});
