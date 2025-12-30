// static/js/app.js

const App = {
    // Show a specific alert message (UX Rule: Clear Feedback)
    showToast: function(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
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
        
        // Append and initialize
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const toastEl = tempDiv.firstElementChild;
        toastContainer.appendChild(toastEl);
        
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        
        // Remove from DOM after hidden
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    },

    // UX Rule: No blocking UI - use Skeleton loaders
    renderSkeleton: function(containerId, count=4) {
        const container = document.getElementById(containerId);
        if(!container) return;
        
        let html = '';
        for(let i=0; i<count; i++) {
            html += `
            <div class="col-md-3 mb-4">
                <div class="card h-100" aria-hidden="true">
                    <div class="skeleton skeleton-img card-img-top"></div>
                    <div class="card-body">
                        <h5 class="card-title skeleton skeleton-text" style="width: 70%;"></h5>
                        <p class="card-text skeleton skeleton-text"></p>
                        <p class="card-text skeleton skeleton-text" style="width: 40%;"></p>
                        <a href="#" class="skeleton skeleton-btn"></a>
                    </div>
                </div>
            </div>`;
        }
        container.innerHTML = html;
    }
};

// Initialize Skeletons on load (Demonstration)
document.addEventListener('DOMContentLoaded', () => {
    // If we are on the homepage, show product skeletons immediately
    if(document.getElementById('product-list')) {
        App.renderSkeleton('product-list', 8);
    }
});