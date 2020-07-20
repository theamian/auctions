from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listings(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True)
    category = models.CharField(max_length=5, blank=True)
    creator = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f"""
            active: {self.active}
            title: {self.title}
            description: {self.description}
            image url: {self.image}
            category: {self.category}"""

    class Meta:
        verbose_name_plural = "listings"

class Bids(models.Model):
    amount = models.IntegerField(blank=False)
    bidder = models.CharField(max_length=64)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="bid_listing")

    class Meta:
        verbose_name_plural = "bids"

class Comments(models.Model):
    commenter = models.CharField(max_length=64)
    stamp = (models.DateTimeField(auto_now_add=True))
    text = models.TextField(blank=True)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, related_name="listing")

    class Meta:
        verbose_name_plural = "comments"


