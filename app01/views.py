from django.shortcuts import render, redirect
from rbac.models import User
# Create your views here.


def login(request):

    if request.method == "POST":
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        user_obj = User.objects.filter(user=user, pwd=pwd).first()

        if user_obj:
            # 存储登录状态
            request.session['user'] = user_obj.user

            # 查询当前登录用户的所有权限url
            # print("--->", user_obj.roles.all().values())
            # print("--->", user_obj.roles.all().values_list())
            # print(">>>", user_obj.roles.all().values("permissions__url"))
            permissions = user_obj.roles.all().values(
                "permissions__url",
                "permissions__code",
                "permissions__title"
            ).distinct()

            permission_list = []
            permission_menu_list = []

            for item in permissions:
                # 当前用户的权限url列表
                permission_list.append(item["permissions__url"])
                # 当前用户的菜单权限列表
                if item["permissions__code"] == "list":
                    permission_menu_list.append({
                        "url": item["permissions__url"],
                        "title": item["permissions__title"],
                    })

            # 将权限列表存储到session中
            request.session["permission_list"] = permission_list
            # 将菜单权限存储到session中
            request.session["permission_menu_list"] = permission_menu_list

            return redirect('/index/')

    return render(request, "login.html")


def index(request):
    return render(request, "index.html")
