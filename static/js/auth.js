// static/js/auth.js

const Auth = {
    // Variable to store the base API URL
    apiBase: '/api',

    // --- Actions ---

    login: async function(username, password) {
        try {
            const response = await fetch(`${this.apiBase}/login/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                // Save tokens to LocalStorage (The Browser's Safe)
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                
                // Get User Details immediately
                await this.fetchUser();
                
                window.location.href = '/'; // Redirect Home
            } else {
                App.showToast(data.detail || 'Login failed', 'error');
            }
        } catch (error) {
            console.error('Login Error:', error);
            App.showToast('Server connection failed', 'error');
        }
    },

    register: async function(formData) {
        try {
            const response = await fetch(`${this.apiBase}/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();

            if (response.ok) {
                App.showToast('Registration successful! Please login.', 'success');
                setTimeout(() => window.location.href = '/login', 2000);
            } else {
                // Show specific validation errors
                let errorMsg = 'Registration failed';
                if(data.username) errorMsg = data.username[0];
                if(data.email) errorMsg = data.email[0];
                if(data.password) errorMsg = data.password[0];
                
                App.showToast(errorMsg, 'error');
            }
        } catch (error) {
            App.showToast('Registration error', 'error');
        }
    },

    logout: function() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        window.location.href = '/login';
    },

    // --- Utilities ---

    isAuthenticated: function() {
        const token = localStorage.getItem('access_token');
        // In a real app, check expiration here
        return !!token;
    },

    fetchUser: async function() {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        const response = await fetch(`${this.apiBase}/me/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const userData = await response.json();
            localStorage.setItem('user_data', JSON.stringify(userData));
            this.updateUI();
        }
    },

    // Update Navbar based on login state
    updateUI: function() {
        const userJson = localStorage.getItem('user_data');
        const authLinks = document.getElementById('auth-links');
        
        if (this.isAuthenticated() && userJson) {
            const user = JSON.parse(userJson);
            authLinks.innerHTML = `
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                        Hello, ${user.username}
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#">Profile</a></li>
                        <li><a class="dropdown-item" href="#">Orders</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="#" onclick="Auth.logout()">Logout</a></li>
                    </ul>
                </li>
            `;
        } else {
            authLinks.innerHTML = `
                <li class="nav-item"><a class="nav-link" href="/login">Login</a></li>
                <li class="nav-item"><a class="btn btn-primary btn-sm ms-2" href="/register">Register</a></li>
            `;
        }
    }
};

// Run check on page load
document.addEventListener('DOMContentLoaded', () => {
    Auth.updateUI();
});