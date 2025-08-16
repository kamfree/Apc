document.addEventListener('DOMContentLoaded', function() {
    const authLinks = document.getElementById('auth-links');
    const userInfo = document.getElementById('user-info');
    const userEmailSpan = document.getElementById('user-email');
    const logoutBtn = document.getElementById('logout-btn');

    const token = localStorage.getItem('access_token');

    if (token) {
        // User is logged in
        authLinks.classList.add('hidden');
        userInfo.classList.remove('hidden');

        // Decode the token to get the 'sub' (subject) claim, which is the user's email
        const payload = JSON.parse(atob(token.split('.')[1]));
        userEmailSpan.textContent = payload.sub;

        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('cart_session_id');
            window.location.href = '/login';
        });
    } else {
        // User is logged out
        authLinks.classList.remove('hidden');
        userInfo.classList.add('hidden');
    }

    updateCartCount();
});

async function updateCartCount() {
    const cartCountSpan = document.getElementById('cart-count');
    const headers = { 'Content-Type': 'application/json' };
    const cartSessionId = localStorage.getItem('cart_session_id');
    if (cartSessionId) {
        headers['X-Cart-Session-ID'] = cartSessionId;
    }
    const token = localStorage.getItem('access_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch('/api/cart', { headers });
        if (response.ok) {
            const cart = await response.json();
            cartCountSpan.textContent = cart.items.length;
        } else {
            cartCountSpan.textContent = '0';
        }
    } catch (error) {
        console.error('Error fetching cart:', error);
        cartCountSpan.textContent = '0';
    }
}
