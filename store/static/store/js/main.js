function buyRequest(id) {
    $.ajax({
        url: "/store/api/v1/basket/",
        type: "post",
        data: {count: 1, product: id} ,
        headers: {
            "X-CSRFToken": getCookie('csrftoken')
        },
        success: function(response) {
            console.log(response)
        },
        error: function(jqXHR, textStatus, errorThrown) {
           console.log(textStatus, errorThrown);
        }
    });
}
