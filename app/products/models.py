from django.db import models

class Product(models.Model):

    name = models.CharField(max_length=200)
    name_2 = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    stock_quantity = models.IntegerField()
    expiration_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)