from .models import CartItem,Cart

def cart_item_count(request):
    items_count = 0 
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        user_cart = cart.items.all()
        items_count = user_cart.count()
    else:
        item_counts = 0
    return {'cart_item_count': items_count}
