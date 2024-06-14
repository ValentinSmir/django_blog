from django.contrib import admin

from blog.models import Category, Location, Post, Comment


class PostAdmin(admin.ModelAdmin):
    search_fields = ('title', 'location__name', 'category__title',
                     'author__username', 'pub_date', 'text',)


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('title',)


class LocationAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class CommentAdmin(admin.ModelAdmin):
    search_fields = ('text', 'author__username', 'created_at', 'post__title',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
