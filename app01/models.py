from django.db import models

# Create your models here.


class School(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title


class Order(models.Model):
    title = models.CharField(max_length=32, verbose_name='')
    num = models.IntegerField()

    def __str__(self):
        return self.title
