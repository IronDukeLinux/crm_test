# '2018/9/5 11:10'
# coding=utf-8


from django.shortcuts import HttpResponse, redirect, render
from django.utils.deprecation import MiddlewareMixin
import re


class PermissionMiddleware(MiddlewareMixin):

    def process_request(self, request):

        current_path = request.path

        # 白名单，用来存放一些不需要用户登录就可以访问的页面
        white_url = ["/login/", "/index/", "/admin/"]
        for reg in white_url:
            ret = re.search(reg, current_path)
            if ret:
                return

        # 验证用户是否登录
        user = request.session.get('user')
        if not user:
            return redirect('/login/')

        # 权限认证
        permission_list = request.session.get('permission_list')
        for reg in permission_list:
            reg = "^%s$" % reg
            ret = re.search(reg, current_path)
            if ret:
                return
        return HttpResponse("无权限访问！")
