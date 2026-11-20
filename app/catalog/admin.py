from django.contrib import admin

from .models import Service, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active", "is_featured", "estimated_days", "created_at")
    list_filter = ("is_active", "is_featured", "tags")
    search_fields = ("name", "description", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "is_featured", "price")
    filter_horizontal = ("tags",)
