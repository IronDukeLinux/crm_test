# '2018/9/4 21:17'
# coding=utf-8


from .models import *
from stark.service.sites import site

site.register(School)
site.register(Order)
