// static/js/app.js

const App = {
    // 1. UX Utility: Show Toast Notifications
    showToast: function(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const bgClass = type === 'error' ? 'text-bg-danger' : 
                        type === 'success' ? 'text-bg-success' : 'text-bg-primary';
        
        const html = `
            <div class="toast align-items-center ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const toastEl = tempDiv.firstElementChild;
        toastContainer.appendChild(toastEl);
        
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    },

    // 2. UX Utility: Render Skeleton Loaders
    renderSkeleton: function(containerId, count=4) {
        const container = document.getElementById(containerId);
        if(!container) return;
        
        let html = '';
        for(let i=0; i<count; i++) {
            html += `
            <div class="col-md-3 mb-4">
                <div class="card h-100" aria-hidden="true">
                    <div class="skeleton skeleton-img card-img-top" style="height: 200px;"></div>
                    <div class="card-body">
                        <h5 class="card-title skeleton skeleton-text" style="width: 70%;"></h5>
                        <p class="card-text skeleton skeleton-text"></p>
                        <div class="skeleton skeleton-btn mt-3" style="width: 100%;"></div>
                    </div>
                </div>
            </div>`;
        }
        container.innerHTML = html;
    },

    // 3. API Action: Fetch and Display Products
    filterState: {
        search: '',
        category: '',
        ordering: '',
        price_min: '',
        price_max: ''
    },

    // 3. API Action: Fetch and Display Products (Updated for Phase 6)
    fetchProducts: async function() {
        const container = document.getElementById('product-list');
        if (!container) return;

        // Show Loading State
        this.renderSkeleton('product-list', 8);

        // Build Query String from Filter State
        const params = new URLSearchParams();
        if (this.filterState.search) params.append('search', this.filterState.search);
        if (this.filterState.category) params.append('category', this.filterState.category);
        if (this.filterState.ordering) params.append('ordering', this.filterState.ordering);
        
        // Construct URL
        const url = `/api/products/?${params.toString()}`;

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error('Server returned ' + response.status);

            const products = await response.json();

            // Clear Skeletons
            container.innerHTML = '';

            // Handle Empty State
            if (products.length === 0) {
                container.innerHTML = `
                    <div class="col-12 text-center py-5">
                        <i class="fas fa-search fa-3x text-muted mb-3"></i>
                        <p class="text-muted">No products found matching your criteria.</p>
                        <button class="btn btn-outline-primary" onclick="App.resetFilters()">Clear Filters</button>
                    </div>`;
                return;
            }

            // Render Products (Same rendering logic as before)
            products.forEach(product => {
                const imgUrl = product.image ? product.image : 'https://via.placeholder.com/300x300?text=No+Image';
                
                // UX: Discount Badge
                let badge = '';
                if (product.old_price && parseFloat(product.old_price) > parseFloat(product.price)) {
                    const diff = Math.round(((product.old_price - product.price) / product.old_price) * 100);
                    badge = `<span class="position-absolute top-0 start-0 badge bg-danger m-2 shadow-sm">-${diff}%</span>`;
                }

                const priceFormatted = parseFloat(product.price).toLocaleString();
                const oldPriceFormatted = product.old_price ? parseFloat(product.old_price).toLocaleString() : null;

                // ... inside fetchProducts, inside products.forEach(product => { ...

                const html = `
                <div class="col">
                    <div class="card h-100 shadow-sm border-0 product-card">
                        <div class="position-relative">
                            ${badge}
                            <a href="/product/${product.slug}/">
                                <img src="${imgUrl}" class="card-img-top" alt="${product.name}" style="height: 220px; object-fit: cover;">
                            </a>
                        </div>
                        <div class="card-body d-flex flex-column">
                            <small class="text-muted mb-1 text-uppercase" style="font-size: 0.75rem;">${product.category_name}</small>
                            
                            <a href="/product/${product.slug}/" class="text-decoration-none text-dark">
                                <h5 class="card-title text-truncate">${product.name}</h5>
                            </a>
                            
                            <div class="mt-auto pt-3">
                                <div class="d-flex align-items-center justify-content-between mb-3">
                                    <span class="fs-5 fw-bold text-dark">₦${priceFormatted}</span>
                                    ${oldPriceFormatted ? `<small class="text-muted text-decoration-line-through">₦${oldPriceFormatted}</small>` : ''}
                                </div>
                                
                                <div class="d-flex gap-2">
                                    <a href="/product/${product.slug}/" class="btn btn-outline-secondary flex-grow-1">
                                        View
                                    </a>
                                    <button class="btn btn-primary flex-grow-1" onclick="App.addToCart(${product.id})">
                                        <i class="fas fa-cart-plus"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`;
                container.insertAdjacentHTML('beforeend', html);
            
            // ... end of loop
            });

        } catch (error) {
            console.error("Fetch error:", error);
            container.innerHTML = `<div class="col-12 text-center text-danger">Failed to load products.</div>`;
        }
    },

    // UX: Apply Filters when user types or selects
    applyFilters: function() {
        // Read values from DOM
        const searchInput = document.getElementById('search-input');
        const catSelect = document.getElementById('category-select');
        const sortSelect = document.getElementById('sort-select');

        if(searchInput) this.filterState.search = searchInput.value;
        if(catSelect) this.filterState.category = catSelect.value;
        if(sortSelect) this.filterState.ordering = sortSelect.value;

        this.fetchProducts();
    },

    resetFilters: function() {
        this.filterState = { search: '', category: '', ordering: '', price_min: '', price_max: '' };
        
        // Reset DOM elements
        document.getElementById('search-input').value = '';
        document.getElementById('category-select').value = '';
        document.getElementById('sort-select').value = '';
        
        this.fetchProducts();
    },

    // Helper: Load Categories into Dropdown
    loadCategories: async function() {
        const select = document.getElementById('category-select');
        if(!select) return;

        try {
            const response = await fetch('/api/categories/');
            const categories = await response.json();
            
            let html = '<option value="">All Categories</option>';
            categories.forEach(cat => {
                html += `<option value="${cat.id}">${cat.name}</option>`;
            });
            select.innerHTML = html;
        } catch(e) { console.error("Failed to load categories"); }
    },

    // 4. API Action: Add to Cart (REAL IMPLEMENTATION)
    addToCart: async function(productId) {
        if (!Auth.isAuthenticated()) {
            this.showToast('Please login to add items to cart', 'error');
            setTimeout(() => window.location.href = '/login', 1500);
            return;
        }

        try {
            const response = await fetch('/api/cart/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify({ product_id: productId, quantity: 1 })
            });

            if (response.ok) {
                this.showToast('Item added to cart!', 'success');
                this.fetchCart(); // Update UI
            } else {
                this.showToast('Failed to add item', 'error');
            }
        } catch (e) { console.error(e); }
    },

    // 5. API Action: Fetch Cart Data
    fetchCart: async function() {
        if (!Auth.isAuthenticated()) return;

        try {
            const response = await fetch('/api/cart/', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
            });
            const cart = await response.json();
            
            this.renderCart(cart);
        } catch (e) { console.error("Cart error", e); }
    },

    // 6. UI: Render Cart Items in Sidebar
    renderCart: function(cart) {
        const container = document.getElementById('cart-items-container');
        const totalEl = document.getElementById('cart-total');
        const countEl = document.getElementById('cart-count');
        const checkoutBtn = document.getElementById('btn-checkout');

        if (!container) return;

        // Update Count Badge
        const itemCount = cart.items.length;
        if(countEl) countEl.innerText = itemCount;

        // Handle Empty Cart
        if (itemCount === 0) {
            container.innerHTML = `
                <div class="text-center mt-5">
                    <i class="fas fa-shopping-basket fa-3x text-muted mb-3"></i>
                    <p class="text-muted">Your cart is empty.</p>
                </div>`;
            totalEl.innerText = '₦0.00';
            checkoutBtn.classList.add('disabled');
            return;
        }

        checkoutBtn.classList.remove('disabled');
        totalEl.innerText = `₦${parseFloat(cart.total_price).toLocaleString()}`;

        // Render Items
        let html = '';
        cart.items.forEach(item => {
            const img = item.product_image ? item.product_image : 'https://via.placeholder.com/80';
            html += `
            <div class="d-flex mb-3 pb-3 border-bottom">
                <img src="${img}" class="rounded" style="width: 60px; height: 60px; object-fit: cover;">
                <div class="ms-3 flex-grow-1">
                    <h6 class="mb-0 text-truncate" style="max-width: 150px;">${item.product_name}</h6>
                    <small class="text-muted">₦${parseFloat(item.product_price).toLocaleString()}</small>
                    
                    <div class="d-flex justify-content-between align-items-center mt-2">
                        <div class="input-group input-group-sm" style="width: 80px;">
                            <button class="btn btn-outline-secondary" onclick="App.updateCartItem(${item.id}, ${item.quantity - 1})">-</button>
                            <span class="input-group-text bg-white">${item.quantity}</span>
                            <button class="btn btn-outline-secondary" onclick="App.updateCartItem(${item.id}, ${item.quantity + 1})">+</button>
                        </div>
                        <button class="btn btn-sm text-danger" onclick="App.removeCartItem(${item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>`;
        });
        container.innerHTML = html;
    },

    // 7. API Action: Update Quantity
    updateCartItem: async function(itemId, newQuantity) {
        try {
            const response = await fetch(`/api/cart/items/${itemId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify({ quantity: newQuantity })
            });
            if(response.ok) {
                const cart = await response.json();
                this.renderCart(cart);
            }
        } catch(e) { console.error(e); }
    },

    // 8. API Action: Remove Item
    removeCartItem: async function(itemId) {
        try {
            const response = await fetch(`/api/cart/items/${itemId}/`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
            });
            if(response.ok) {
                const cart = await response.json();
                this.renderCart(cart);
            }
        } catch(e) { console.error(e); }
    },
    // ... inside App object ...

    // 9. Load Summary on Checkout Page
    loadCheckoutSummary: async function() {
        const list = document.getElementById('summary-list');
        if(!list) return;

        try {
            const response = await fetch('/api/cart/', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
            });
            const cart = await response.json();
        this.cartSubtotal = parseFloat(cart.total_price); // Save for math later

        // Update UI (Subtotal only initially)
        document.getElementById('summary-total').innerText = `₦${this.cartSubtotal.toLocaleString()}`;
            document.getElementById('summary-count').innerText = cart.items.length;

            // Update List
            let html = '';
            cart.items.forEach(item => {
                html += `
                <li class="list-group-item d-flex justify-content-between lh-sm">
                    <div>
                        <h6 class="my-0 small">${item.product_name}</h6>
                        <small class="text-muted">Qty: ${item.quantity}</small>
                    </div>
                    <span class="text-muted">₦${parseFloat(item.subtotal).toLocaleString()}</span>
                </li>`;
            });
            list.innerHTML = html;

        } catch(e) { console.error(e); }
    },

    // 10. API Action: Place Order
    placeOrder: async function(formData, btn, originalText) {
        
        // 1. Get Selected Payment Method
        const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;
        formData.payment_method = paymentMethod;

        try {
            const response = await fetch('/api/checkout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                // CASE A: Paystack Redirect
                if (data.type === 'paystack' && data.payment_url) {
                    this.showToast('Redirecting to secure payment...', 'success');
                    window.location.href = data.payment_url; 
                } 
                // CASE B: Payment on Delivery / Offline
                else {
                    this.showToast('Order placed successfully!', 'success');
                    setTimeout(() => window.location.href = '/order-success', 2000); // We will build this page next
                }
            } else {
                this.showToast(data.error || 'Checkout failed', 'error');
                btn.innerText = originalText;
                btn.disabled = false;
            }
        } catch (e) {
            console.error(e);
            this.showToast('Connection failed', 'error');
            btn.innerText = originalText;
            btn.disabled = false;
        }
    },

    // ... inside App object ...

    // Store zones locally to avoid repeated API calls
    deliveryZones: [],
    cartSubtotal: 0,

    // 11. Load Delivery Zones (Call this on Checkout Page Load)
    loadDeliveryZones: async function() {
        const select = document.getElementById('state');
        if(!select) return;

        try {
            const response = await fetch('/api/delivery-zones/');
            this.deliveryZones = await response.json();

            let html = '<option value="">Select State...</option>';
            this.deliveryZones.forEach(zone => {
                html += `<option value="${zone.state}" data-fee="${zone.fee}" data-time="${zone.estimated_time}">${zone.state}</option>`;
            });
            select.innerHTML = html;
        } catch(e) { console.error("Failed to load zones"); }
    },

    // 12. Update Checkout Summary (Math Logic)
    calculateTotal: function() {
        const select = document.getElementById('state');
        const deliveryEl = document.getElementById('summary-delivery');
        const totalEl = document.getElementById('summary-total');
        const infoEl = document.getElementById('delivery-info');
        
        if(!select) return;

        // Get selected option data
        const selectedOption = select.options[select.selectedIndex];
        const fee = parseFloat(selectedOption.getAttribute('data-fee') || 0);
        const time = selectedOption.getAttribute('data-time') || '';

        // Update UI Text
        deliveryEl.innerText = `₦${fee.toLocaleString()}`;
        if(time) infoEl.innerText = `Estimated Delivery: ${time}`;
        else infoEl.innerText = '';

        // Calculate Grand Total (Subtotal + Fee)
        // Note: We need to ensure we have the subtotal. 
        // We will update loadCheckoutSummary to save it.
        const grandTotal = this.cartSubtotal + fee;
        totalEl.innerText = `₦${grandTotal.toLocaleString()}`;
    },
};

// Initialize Skeletons on load (Demonstration)
document.addEventListener('DOMContentLoaded', () => {
    // If we are on the homepage, show product skeletons immediately
    if(document.getElementById('product-list')) {
        App.renderSkeleton('product-list', 8);
    }
});