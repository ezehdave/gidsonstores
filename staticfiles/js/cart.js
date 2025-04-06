function updateCart(productId, action) {
    fetch('/update_cart/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ productId: productId, action: action }),
    })
    .then((res) => res.json())
    .then((data) => {
        console.log(data);
        location.reload(); // or update the DOM dynamically
    });
}

function clearCart() {
    fetch('/clear_cart/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        }
    })
    .then((res) => res.json())
    .then((data) => {
        console.log(data);
        location.reload();
    });
}

function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        if (cookie.trim().startsWith('csrftoken=')) {
            return cookie.trim().split('=')[1];
        }
    }
    return '';
}
