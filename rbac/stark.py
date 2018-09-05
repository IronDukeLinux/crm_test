# '2018/9/5 8:59'
# coding=utf-8


from .models import User, Role, Permission
from stark.service.sites import site, ModelStark


class PermissionConfig(ModelStark):
    list_display = ["title", "url", "code"]


site.register(User)
site.register(Role)
site.register(Permission, PermissionConfig)
