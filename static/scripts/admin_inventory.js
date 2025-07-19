// static/script.js
document.addEventListener('DOMContentLoaded', function() {
    // Load initial data
    loadSuppliers();
    loadLocations();
    loadCategories();
    loadProducts();

    // Form submission handler for adding product
    document.getElementById('addProductForm').addEventListener('submit', function(e) {
        e.preventDefault();
        addProduct();
    });

    // Search functionality
    document.getElementById('searchInput').addEventListener('input', function() {
        searchProducts(this.value);
    });

    // Update product modal form submission
    document.getElementById('updateProductForm').addEventListener('submit', function(e) {
        e.preventDefault();
        updateProduct();
    });
});

function loadSuppliers() {
    fetch('/get_suppliers')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('supplier');
            data.forEach(supplier => {
                const option = document.createElement('option');
                option.value = supplier.id;
                option.textContent = `${supplier.name} (${supplier.company})`;
                select.appendChild(option);
            });
        });
}

function loadLocations() {
    fetch('/get_locations')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('location');
            data.forEach(location => {
                const option = document.createElement('option');
                option.value = location.id;
                option.textContent = location.name;
                select.appendChild(option);
            });
        });
}

function loadCategories() {
    fetch('/get_categories')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('category');
            data.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                select.appendChild(option);
            });
        });
}

function loadProducts() {
    fetch('/get_products')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('productsList');
            tbody.innerHTML = '';
            data.forEach(product => {
                const tr = document.createElement('tr');
                if (product.quantity <= product.min_threshold) {
                    tr.classList.add('low-stock');
                }
                tr.innerHTML = `
                    <td>${product.name}</td>
                    <td>${product.category}</td>
                    <td>${product.supplier}</td>
                    <td>${product.location}</td>
                    <td>${product.purchased_at}</td>
                    <td>${product.quantity}</td>
                    <td>${product.min_threshold}</td>
                    <td>${product.expiry_date}</td>
                    <td>${product.price}</td>
                    <td>
                        <button class="btn btn-sm btn-warning" onclick="openUpdateModal(${product.id}, '${product.name}', ${product.quantity}, ${product.min_threshold}, ${product.price})">
                            Update
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})">
                            Delete
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        });
}

function addProduct() {
    const data = {
        product_name: document.getElementById('productName').value,
        category_id: document.getElementById('category').value,
        supplier_id: document.getElementById('supplier').value,
        location_id: document.getElementById('location').value,
        quantity: document.getElementById('quantity').value,
        min_threshold: document.getElementById('minThreshold').value,
        manufacture_date: document.getElementById('manufactureDate').value,
        expiry_date: document.getElementById('expiryDate').value,
        description: document.getElementById('description').value,
        purchased_at: document.getElementById('purchasedAt').value
    };

    fetch('/add_product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('addProductForm').reset();
            loadProducts();
        } else {
            alert('Error adding product: ' + data.error);
        }
    });
}

function searchProducts(searchTerm) {
    const tbody = document.getElementById('productsList');
    const rows = tbody.getElementsByTagName('tr');
    
    for (let row of rows) {
        let show = false;
        const cells = row.getElementsByTagName('td');
        
        // Search across multiple columns
        for (let cell of cells) {
            if (cell.textContent.toLowerCase().includes(searchTerm.toLowerCase())) {
                show = true;
                break;
            }
        }
        
        row.style.display = show ? '' : 'none';
    }
}

function openUpdateModal(productId, productName, currentQuantity, currentThreshold, currentPrice) {
    // Populate modal with current product details
    document.getElementById('updateProductId').value = productId;
    document.getElementById('updateProductName').textContent = productName;
    document.getElementById('updateQuantity').value = currentQuantity;
    document.getElementById('updateMinThreshold').value = currentThreshold;
    document.getElementById('updatePrice').value = currentPrice;
    
    // Show the modal
    const updateModal = new bootstrap.Modal(document.getElementById('updateProductModal'));
    updateModal.show();
}

function updateProduct() {
    const productId = document.getElementById('updateProductId').value;
    const data = {
        quantity: document.getElementById('updateQuantity').value,
        min_threshold: document.getElementById('updateMinThreshold').value,
        price: document.getElementById('updatePrice').value
    };

    fetch(`/update_product/${productId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close the modal
            const updateModal = bootstrap.Modal.getInstance(document.getElementById('updateProductModal'));
            updateModal.hide();
            
            // Refresh the product list
            loadProducts();
            
            // Show success message
            alert('Product updated successfully!');
        } else {
            alert('Error updating product: ' + data.error);
        }
    });
}

function deleteProduct(productId) {
    if (confirm('Are you sure you want to delete this product?')) {
        fetch(`/delete_product/${productId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadProducts();
            } else {
                alert('Error deleting product: ' + data.error);
            }
        });
    }
}