document.addEventListener('DOMContentLoaded', () => {
    const loginForm    = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const toggleAuth   = document.getElementById('toggle-auth');
    const authSubtitle = document.getElementById('auth-subtitle');
    const footerText   = document.getElementById('footer-text');
    const errorBox     = document.getElementById('error-box');

    let mode = 'login'; // 'login' or 'register'

    toggleAuth.addEventListener('click', (e) => {
        e.preventDefault();
        if (mode === 'login') {
            mode = 'register';
            loginForm.classList.add('hidden');
            registerForm.classList.remove('hidden');
            authSubtitle.textContent = 'Create your account to get started.';
            footerText.textContent = 'Already have an account?';
            toggleAuth.textContent = 'Sign In';
        } else {
            mode = 'login';
            loginForm.classList.remove('hidden');
            registerForm.classList.add('hidden');
            authSubtitle.textContent = 'Welcome back! Please login.';
            footerText.textContent = "Don't have an account?";
            toggleAuth.textContent = 'Sign Up';
        }
        errorBox.style.display = 'none';
    });

    const showError = (msg) => {
        errorBox.textContent = msg;
        errorBox.style.display = 'block';
    };

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            if (res.ok) {
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user));
                window.location.href = '/';
            } else {
                showError(data.error || 'Login failed');
            }
        } catch (err) {
            showError('Network error. Please try again.');
        }
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;

        try {
            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const data = await res.json();
            if (res.ok) {
                // After registration, auto-login
                const loginRes = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const loginData = await loginRes.json();
                if (loginRes.ok) {
                    localStorage.setItem('token', loginData.access_token);
                    localStorage.setItem('user', JSON.stringify(loginData.user));
                    window.location.href = '/';
                }
            } else {
                showError(data.error || 'Registration failed');
            }
        } catch (err) {
            showError('Network error. Please try again.');
        }
    });
});
