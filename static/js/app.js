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
    fetchProducts: async function() {
        const container = document.getElementById('product-list');
        if (!container) return;

        // Show Loading State
        this.renderSkeleton('product-list', 8);

        try {
            const response = await fetch('/api/products/');
            
            if (!response.ok) {
                throw new Error('Server returned ' + response.status);
            }

            const products = await response.json();

            // Clear Skeletons
            container.innerHTML = '';

            // Handle Empty State
            if (products.length === 0) {
                container.innerHTML = `
                    <div class="col-12 text-center py-5">
                        <i class="fas fa-box-open fa-3x text-muted mb-3"></i>
                        <p class="text-muted">No products found yet.</p>
                    </div>`;
                return;
            }

            // Render Products
            products.forEach(product => {
                const imgUrl = product.image ? product.image : 'https://via.placeholder.com/300x300?text=No+Image';
                
                // Calculate Discount Badge
                let badge = '';
                if (product.old_price && parseFloat(product.old_price) > parseFloat(product.price)) {
                    const diff = Math.round(((product.old_price - product.price) / product.old_price) * 100);
                    badge = `<span class="position-absolute top-0 start-0 badge bg-danger m-2 shadow-sm">-${diff}%</span>`;
                }

                // Format Price
                const priceFormatted = parseFloat(product.price).toLocaleString();
                const oldPriceFormatted = product.old_price ? parseFloat(product.old_price).toLocaleString() : null;

                const html = `
                <div class="col">
                    <div class="card h-100 shadow-sm border-0">
                        <div class="position-relative">
                            ${badge}
                            <img src="${imgUrl}" class="card-img-top" alt="${product.name}" style="height: 220px; object-fit: cover;">
                        </div>
                        <div class="card-body d-flex flex-column">
                            <small class="text-muted mb-1 text-uppercase" style="font-size: 0.75rem; letter-spacing: 0.5px;">${product.category_name || 'General'}</small>
                            <h5 class="card-title text-truncate" title="${product.name}">${product.name}</h5>
                            
                            <div class="mt-auto pt-3">
                                <div class="d-flex align-items-center justify-content-between mb-3">
                                    <span class="fs-5 fw-bold text-dark">₦${priceFormatted}</span>
                                    ${oldPriceFormatted ? `<small class="text-muted text-decoration-line-through">₦${oldPriceFormatted}</small>` : ''}
                                </div>
                                <button class="btn btn-outline-primary w-100" onclick="App.addToCart(${product.id})">
                                    <i class="fas fa-cart-plus me-1"></i> Add to Cart
                                </button>
                            </div>
                        </div>
                    </div>
                </div>`;
                container.insertAdjacentHTML('beforeend', html);
            });

        } catch (error) {
            console.error("Fetch error:", error);
            container.innerHTML = `
                <div class="col-12 text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <p>Failed to load products. ${error.message}</p>
                </div>`;
        }
    },

    // 4. API Action: Add to Cart (Placeholder for Phase 7)
    addToCart: function(id) {
        this.showToast('Product added to cart (Cart System coming in Phase 7)', 'success');
    }
};

// Initialize Skeletons on load (Demonstration)
document.addEventListener('DOMContentLoaded', () => {
    // If we are on the homepage, show product skeletons immediately
    if(document.getElementById('product-list')) {
        App.renderSkeleton('product-list', 8);
    }
});