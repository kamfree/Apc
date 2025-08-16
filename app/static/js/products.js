document.addEventListener('DOMContentLoaded', function() {
    const productList = document.getElementById('product-list');

    async function fetchProducts() {
        try {
            const response = await fetch('/api/products');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            renderProducts(data.products);
        } catch (error) {
            productList.innerHTML = '<p class="text-red-500">Failed to load products. Please try again later.</p>';
            console.error('Error fetching products:', error);
        }
    }

    function renderProducts(products) {
        if (products.length === 0) {
            productList.innerHTML = '<p>No products found.</p>';
            return;
        }

        productList.innerHTML = ''; // Clear loading message
        products.forEach(product => {
            const productCard = `
                <div class="bg-white rounded-lg shadow-md overflow-hidden transform hover:scale-105 transition-transform duration-300">
                    <img src="${product.images.length > 0 ? product.images[0].url : 'https://via.placeholder.com/300'}" alt="${product.name}" class="w-full h-48 object-cover">
                    <div class="p-4">
                        <h3 class="text-lg font-semibold">${product.name}</h3>
                        <p class="text-gray-600 mt-1">${product.vendor}</p>
                        <p class="text-xl font-bold mt-2">$${product.skus.length > 0 ? product.skus[0].price.toFixed(2) : 'N/A'}</p>
                        <a href="/product/${product.id}" class="mt-4 inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">View Details</a>
                    </div>
                </div>
            `;
            productList.innerHTML += productCard;
        });
    }

    fetchProducts();
});
