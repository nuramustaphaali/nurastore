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
                // Save tokens to LocalStorage
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                
                // Get User Details immediately
                await this.fetchUser();
                
                // Redirect to intended page or home
                window.location.href = '/'; 
            } else {
                if (typeof App !== 'undefined') {
                    App.showToast(data.detail || 'Login failed', 'error');
                } else {
                    alert('Login failed');
                }
            }
        } catch (error) {
            console.error('Login Error:', error);
            if (typeof App !== 'undefined') App.showToast('Server connection failed', 'error');
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
                if (typeof App !== 'undefined') App.showToast('Registration successful! Please login.', 'success');
                setTimeout(() => window.location.href = '/login', 2000);
            } else {
                // Show specific validation errors
                let errorMsg = 'Registration failed';
                if(data.username) errorMsg = data.username[0];
                if(data.email) errorMsg = data.email[0];
                if(data.password) errorMsg = data.password[0];
                
                if (typeof App !== 'undefined') App.showToast(errorMsg, 'error');
            }
        } catch (error) {
            if (typeof App !== 'undefined') App.showToast('Registration error', 'error');
        }
    },

    logout: function() {
        // Clear all local storage items
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        
        // Redirect to login
        window.location.href = '/login';
    },

    // --- Utilities ---

    isAuthenticated: function() {
        const token = localStorage.getItem('access_token');
        // Basic check (Real apps should check expiration)
        return !!token;
    },

    fetchUser: async function() {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        try {
            const response = await fetch(`${this.apiBase}/me/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const userData = await response.json();
                localStorage.setItem('user_data', JSON.stringify(userData));
                this.updateUI(); // Refresh UI with new name
            } else {
                // Token invalid? Logout
                this.logout();
            }
        } catch(e) {
            console.error("Failed to fetch user", e);
        }
    },

    // --- THIS IS THE PART THAT UPDATES THE NAVBAR ---
    updateUI: function() {
        const userJson = localStorage.getItem('user_data');
        const authLinks = document.getElementById('auth-links');
        
        if (!authLinks) return; // Safety check

        if (this.isAuthenticated() && userJson) {
            const user = JSON.parse(userJson);
            
            // RENDER LOGGED IN LINKS (Profile, Orders, Logout)
            authLinks.innerHTML = `
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle active fw-bold" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="fas fa-user-circle me-1"></i> Hello, ${user.username}
                    </a>
                    <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0 animate slideIn">
                        <li>
                            <a class="dropdown-item" href="/profile">
                                <i class="fas fa-id-card me-2 text-primary"></i> My Profile
                            </a>
                        </li>
                        <li>
                            <a class="dropdown-item" href="/orders">
                                <i class="fas fa-box-open me-2 text-success"></i> My Orders
                            </a>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                            <a class="dropdown-item text-danger" href="#" onclick="Auth.logout()">
                                <i class="fas fa-sign-out-alt me-2"></i> Logout
                            </a>
                        </li>
                    </ul>
                </li>
            `;
        } else {
            // RENDER LOGGED OUT LINKS
            authLinks.innerHTML = `
                <li class="nav-item">
                    <a class="nav-link" href="/login">Login</a>
                </li>
                <li class="nav-item">
                    <a class="btn btn-primary btn-sm ms-2 px-3 rounded-pill" href="/register">Register</a>
                </li>
            `;
        }
    }
};

// Run check on page load
document.addEventListener('DOMContentLoaded', () => {
    Auth.updateUI();
});