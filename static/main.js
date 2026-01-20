// Asosiy JavaScript fayli

$(document).ready(function() {
    // Cart funksiyalari
    $('.add-to-cart-btn').on('click', function(e) {
        e.preventDefault();
        const productId = $(this).data('product-id');
        const quantity = $(this).data('quantity') || 1;
        
        $.ajax({
            url: '/cart/add/',
            type: 'POST',
            data: {
                'product_id': productId,
                'quantity': quantity,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function(response) {
                if (response.success) {
                    // Cart count yangilash
                    $('.cart-count').text(response.cart_count);
                    
                    // Animation
                    $('.cart-icon').addClass('cart-animation');
                    setTimeout(() => {
                        $('.cart-icon').removeClass('cart-animation');
                    }, 500);
                    
                    // Notification
                    showToast('Mahsulot savatga qo\'shildi!', 'success');
                }
            }
        });
    });
    
    // Quantity o'zgartirish
    $('.quantity-btn').on('click', function() {
        const input = $(this).siblings('.quantity-input');
        let value = parseInt(input.val());
        
        if ($(this).hasClass('plus')) {
            value++;
        } else if ($(this).hasClass('minus') && value > 1) {
            value--;
        }
        
        input.val(value);
    });
    
    // Form validation
    $('form').on('submit', function() {
        const submitBtn = $(this).find('button[type="submit"]');
        if (submitBtn.length) {
            submitBtn.prop('disabled', true);
            submitBtn.html('<span class="spinner-border spinner-border-sm"></span> Kutish...');
        }
    });
    
    // Toast notification funksiyasi
    function showToast(message, type = 'info') {
        const toast = $(`
            <div class="toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `);
        
        $('body').append(toast);
        const bsToast = new bootstrap.Toast(toast[0]);
        bsToast.show();
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
    
    // Auto-hide alerts
    setTimeout(() => {
        $('.alert').alert('close');
    }, 5000);
    
    // Smooth scroll
    $('a[href^="#"]').on('click', function(e) {
        if (this.hash !== "") {
            e.preventDefault();
            const hash = this.hash;
            $('html, body').animate({
                scrollTop: $(hash).offset().top - 70
            }, 800);
        }
    });
});

// Cart classi
class Cart {
    constructor() {
        this.loadCart();
    }
    
    loadCart() {
        this.items = JSON.parse(localStorage.getItem('cart')) || [];
    }
    
    saveCart() {
        localStorage.setItem('cart', JSON.stringify(this.items));
    }
    
    addItem(product, quantity = 1) {
        const existingItem = this.items.find(item => item.id === product.id);
        
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            this.items.push({
                id: product.id,
                name: product.name,
                price: product.price,
                quantity: quantity,
                image: product.image
            });
        }
        
        this.saveCart();
        this.updateCartUI();
    }
    
    updateCartUI() {
        const count = this.items.reduce((sum, item) => sum + item.quantity, 0);
        $('.cart-count').text(count);
    }
}