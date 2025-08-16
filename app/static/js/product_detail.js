document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('product-detail-container');

    async function fetchProductDetails() {
        try {
            const response = await fetch(`/api/products/${productId}`);
            if (!response.ok) {
                throw new Error('Product not found');
            }
            const product = await response.json();
            renderProduct(product);
        } catch (error) {
            container.innerHTML = `<p class="text-red-500">${error.message}</p>`;
            console.error('Error fetching product details:', error);
        }
    }

    function renderProduct(product) {
        let skusHtml = '<p>No variants available.</p>';
        if (product.skus.length > 0) {
            skusHtml = product.skus.map((sku, index) => `
                <div class="flex items-center">
                    <input type="radio" id="sku-${sku.id}" name="sku" value="${sku.id}" data-price="${sku.price}" class="mr-2" ${index === 0 ? 'checked' : ''}>
                    <label for="sku-${sku.id}">
                        ${Object.entries(sku.attributes).map(([key, val]) => `${key}: ${val}`).join(', ')} -
                        <span class="font-semibold">$${sku.price.toFixed(2)}</span>
                        <span class="text-sm text-gray-500 ml-2">(${sku.quantity} in stock)</span>
                    </label>
                </div>
            `).join('');
        }

        container.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <img src="${product.images.length > 0 ? product.images[0].url : 'https://via.placeholder.com/500'}" alt="${product.name}" class="w-full rounded-lg shadow-md">
                </div>
                <div>
                    <h1 class="text-4xl font-bold">${product.name}</h1>
                    <p class="text-gray-500 text-lg mt-2">Sold by ${product.vendor}</p>
                    <p class="mt-4 text-gray-700">${product.description}</p>

                    <div class="mt-6">
                        <h3 class="text-xl font-semibold mb-2">Select Variant</h3>
                        <div id="sku-options" class="space-y-2">${skusHtml}</div>
                    </div>

                    <div class="mt-6 flex items-center">
                        <label for="quantity" class="mr-4">Quantity:</label>
                        <input type="number" id="quantity" name="quantity" value="1" min="1" class="w-20 px-3 py-2 border rounded-lg">
                    </div>

                    <button id="add-to-cart-btn" class="mt-6 w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition-colors text-lg font-bold">Add to Cart</button>
                    <div id="add-to-cart-message" class="mt-4 text-center"></div>
                </div>
            </div>
        `;

        const addToCartBtn = document.getElementById('add-to-cart-btn');
        addToCartBtn.addEventListener('click', addToCart);
    }

    async function addToCart() {
        const selectedSku = document.querySelector('input[name="sku"]:checked');
        if (!selectedSku) {
            alert('Please select a variant.');
            return;
        }

        const skuId = selectedSku.value;
        const quantity = document.getElementById('quantity').value;
        const messageDiv = document.getElementById('add-to-cart-message');

        const headers = { 'Content-Type': 'application/json' };
        const token = localStorage.getItem('access_token');
        const cartSessionId = localStorage.getItem('cart_session_id');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        } else if (cartSessionId) {
            headers['X-Cart-Session-ID'] = cartSessionId;
        }

        try {
            const response = await fetch('/api/cart/items', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ sku_id: parseInt(skuId), quantity: parseInt(quantity) })
            });

            const data = await response.json();
            if (response.ok) {
                messageDiv.textContent = 'Item added to cart!';
                messageDiv.className = 'mt-4 text-green-500 text-center';

                // If the server created a new guest cart, it will send back the session ID
                const newCartSessionId = response.headers.get('X-Cart-Session-ID');
                if (newCartSessionId) {
                    localStorage.setItem('cart_session_id', newCartSessionId);
                }

                updateCartCount(); // This function is in main.js
            } else {
                throw new Error(data.message || 'Failed to add item.');
            }
        } catch (error) {
            messageDiv.textContent = error.message;
            messageDiv.className = 'mt-4 text-red-500 text-center';
            console.error('Add to cart error:', error);
        }
    }

    fetchProductDetails();
});
