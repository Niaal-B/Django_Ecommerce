from django.contrib import admin
from .models import Wishlist, WishlistItem

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'items_count', 'created_at', 'updated_at']
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items Count'

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['wishlist', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__name', 'wishlist__user__username']

