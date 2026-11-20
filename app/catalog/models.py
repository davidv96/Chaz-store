from django.db import models
from django.urls import reverse

from store.uploads import service_image_path


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:service_list") + f"?tag={self.slug}"


class Service(models.Model):
    tags = models.ManyToManyField(Tag, related_name="services", blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_price_variable = models.BooleanField(default=False, help_text="Price is quoted by the owner after the order is placed")
    image = models.ImageField(upload_to=service_image_path, blank=True)
    focal_x = models.FloatField(default=0.5, help_text="Horizontal crop focus, 0 (left) to 1 (right)")
    focal_y = models.FloatField(default=0.5, help_text="Vertical crop focus, 0 (top) to 1 (bottom)")
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False)
    estimated_days = models.PositiveIntegerField(help_text="Estimated business days to complete")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "name"]
        indexes = [
            models.Index(fields=["is_active", "is_featured"]),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:service_detail", kwargs={"slug": self.slug})
