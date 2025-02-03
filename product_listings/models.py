from django.db import models
from django.core.validators import MinValueValidator


# Product Model
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)  # Make slug unique
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(1)]
    )
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    last_update = models.DateTimeField(auto_now=True)
   

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']

# Product Image Model
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.URLField(max_length=500)  # Assuming URL is used for images

    def __str__(self):
        return f"Image for {self.product.title}"
