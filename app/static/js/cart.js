document.addEventListener('DOMContentLoaded', function() {
    const cartContainer = document.getElementById('cart-container');
    const cartSummary = document.getElementById('cart-summary');
    const checkoutBtn = document.getElementById('checkout-btn');

    async function fetchCart() {
        const headers = { 'Content-Type': 'application/json' };
        const token = localStorage.getItem('access_token');
        const cartSessionId = localStorage.getItem('cart_session_id');

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        } else if (cartSessionId) {
            headers['X-Cart-Session-ID'] = cartSessionId;
        } else {
            renderEmptyCart();
            return;
        }

        try {
            const response = await fetch('/api/cart', { headers });
            if (response.ok) {
                const cart = await response.json();
                renderCart(cart);
            } else {
                renderEmptyCart();
            }
        } catch (error) {
            cartContainer.innerHTML = '<p class="text-red-500">Error loading cart.</p>';
            console.error('Error fetching cart:', error);
        }
    }

    function renderCart(cart) {
        if (!cart || cart.items.length === 0) {
            renderEmptyCart();
            return;
        }

        let itemsHtml = `
            <div class="border-b pb-4 mb-4">
                ${cart.items.map(item => `
                    <div class="flex items-center justify-between py-4">
                        <div class="flex items-center">
                            <div>
                                <p class="font-semibold">${item.name}</p>
                                <p class="text-sm text-gray-600">${Object.entries(item.attributes).map(([k,v])=>`${k}: ${v}`).join(', ')}</p>
                            </div>
                        </div>
                        <div class="flex items-center">
                            <input type="number" value="${item.quantity}" min="1" class="w-16 p-1 border rounded-md text-center quantity-input" data-item-id="${item.id}">
                            <p class="w-24 text-center font-semibold">$${item.item_total.toFixed(2)}</p>
                            <button class="ml-4 text-red-500 hover:text-red-700 remove-btn" data-item-id="${item.id}">&times;</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        cartContainer.innerHTML = itemsHtml;

        cartSummary.innerHTML = `<p class="text-2xl font-bold">Total: $${cart.total_price.toFixed(2)}</p>`;
        checkoutBtn.classList.remove('hidden');

        addEventListeners();
    }

    function renderEmptyCart() {
        cartContainer.innerHTML = '<p>Your cart is empty.</p>';
        cartSummary.innerHTML = '';
        checkoutBtn.classList.add('hidden');
    }

    function addEventListeners() {
        document.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', (e) => updateQuantity(e.target.dataset.itemId, e.target.value));
        });
        document.querySelectorAll('.remove-btn').forEach(button => {
            button.addEventListener('click', (e) => removeItem(e.target.dataset.itemId));
        });
    }

    async function updateQuantity(itemId, quantity) {
        await updateCartItem(`/api/cart/items/${itemId}`, 'PUT', { quantity: parseInt(quantity) });
    }

    async function removeItem(itemId) {
        await updateCartItem(`/api/cart/items/${itemId}`, 'DELETE');
    }

    async function updateCartItem(url, method, body = null) {
        const headers = { 'Content-Type': 'application/json' };
        const token = localStorage.getItem('access_token');
        const cartSessionId = localStorage.getItem('cart_session_id');
        if (token) headers['Authorization'] = `Bearer ${token}`;
        else if (cartSessionId) headers['X-Cart-Session-ID'] = cartSessionId;

        try {
            const response = await fetch(url, {
                method: method,
                headers: headers,
                body: body ? JSON.stringify(body) : null
            });
            if (response.ok) {
                fetchCart(); // Re-fetch and re-render the whole cart
                updateCartCount(); // Update header count
            } else {
                const data = await response.json();
                alert(data.message || 'Failed to update cart.');
            }
        } catch (error) {
            console.error('Error updating cart:', error);
            alert('An error occurred.');
        }
    }

    fetchCart();
});
