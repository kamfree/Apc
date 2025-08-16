document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = this.email.value;
            const password = this.password.value;
            const errorDiv = document.getElementById('login-error');

            const headers = {
                'Content-Type': 'application/json',
            };
            const cartSessionId = localStorage.getItem('cart_session_id');
            if (cartSessionId) {
                headers['X-Cart-Session-ID'] = cartSessionId;
            }

            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('refresh_token', data.refresh_token);
                    // After logging in, the guest cart is merged, so we can remove the session ID
                    localStorage.removeItem('cart_session_id');
                    window.location.href = '/';
                } else {
                    errorDiv.textContent = data.message || 'Login failed.';
                }
            } catch (error) {
                errorDiv.textContent = 'An error occurred. Please try again.';
                console.error('Login error:', error);
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = this.email.value;
            const password = this.password.value;
            const messageDiv = document.getElementById('register-message');

            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();
                if (response.ok) {
                    messageDiv.textContent = 'Registration successful! You can now log in.';
                    messageDiv.className = 'mt-4 text-green-500 text-center';
                    registerForm.reset();
                } else {
                    messageDiv.textContent = data.message || 'Registration failed.';
                    messageDiv.className = 'mt-4 text-red-500 text-center';
                }
            } catch (error) {
                messageDiv.textContent = 'An error occurred. Please try again.';
                messageDiv.className = 'mt-4 text-red-500 text-center';
                console.error('Registration error:', error);
            }
        });
    }
});
