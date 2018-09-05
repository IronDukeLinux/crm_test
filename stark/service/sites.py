# '2018/8/28 17:28'
# coding=utf-8
from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import forms
from stark.page import MyPage
from django.db.models import Q
import copy


class ShowList(object):
    """
    数据展示类
    """
    def __init__(self, config_obj, data_list, request, ):
        self.config_obj = config_obj
        self.data_list = data_list
        self.request = request
        # 分页
        self.pagination = MyPage(
            request.GET.get('page', 1),
            data_list.count(),
            request,
            per_page_data=10
        )
        self.page_queryset = data_list[self.pagination.start:self.pagination.end]

    def get_headers(self):
        # 定义表头
        header_list = []
        for field_or_func in self.config_obj.new_list_display():
            if callable(field_or_func):
                val = field_or_func(self.config_obj, is_header=True)
            else:
                if field_or_func == '__str__':
                    val = self.config_obj.model_name.upper()
                else:
                    obj = self.config_obj.model._meta.get_field(field_or_func)
                    val = obj.verbose_name
                    print(val)
            header_list.append(val)
        return header_list

    def get_body(self):
        # 定义查询展示的数据表
        new_data_list = []
        for obj in self.page_queryset:  # 当前页面的数据
            temp = []
            for field_or_func in self.config_obj.new_list_display():
                if callable(field_or_func):
                    val = field_or_func(self.config_obj, obj=obj)
                else:
                    try:
                        from django.db.models.fields.related import ManyToManyField
                        field_obj = self.config_obj.model._meta.get_field(field_or_func)
                        if isinstance(field_obj, ManyToManyField):
                            rel_data_list = getattr(obj, field_or_func).all()
                            queryset_list = [str(item) for item in rel_data_list]
                            val = ','.join(queryset_list)
                        else:
                            val = getattr(obj, field_or_func)
                            if field_or_func in self.config_obj.list_display_links:
                                _url = self.config_obj.get_edit_url(obj)
                                val = mark_safe("<a href='%s'>%s</a>" % (_url, val))
                    except Exception as e:
                        val = getattr(obj, field_or_func)
                temp.append(val)
            new_data_list.append(temp)
        return new_data_list

    def get_new_actions(self):
        temp = []
        temp.extend(self.config_obj.action_fields)
        temp.append(self.config_obj.patch_delete)
        new_action_fields = []
        for func in temp:
            new_action_fields.append({
                "text": func.desc,
                "name": func.__name__,
            })
        return new_action_fields

    def get_list_filter_links(self):
        # 因为有多级过滤的需求，所以用字典而不是列表
        list_filter_links = {}

        for filed in self.config_obj.list_filter:
            # 获取带有搜索历史的get
            params = copy.deepcopy(self.request.GET)
            # 获取当前字段的pk值
            current_field_pk = params.get(filed, 0)
            # 获取字段对象
            field_obj = self.config_obj.model._meta.get_field(filed)
            # 获取关联字段关联的表
            rel_model = field_obj.rel.to
            # 获取关联表的所有数据
            rel_model_queryset = rel_model.objects.all()
            # 每一条数据生成一个a标签
            temp = []
            if current_field_pk == 0:
                # params.pop(filed, None)
                link = "<a href='?%s' class='list-group-item active'>%s</a>" % (params.urlencode(), "ALL")
            else:
                params.pop(filed)
                link = "<a href='?%s' class='list-group-item'>%s</a>" % (params.urlencode(), "ALL")
            temp.append(link)
            for obj in rel_model_queryset:
                params[filed] = obj.pk
                if obj.pk == int(current_field_pk):
                    link = "<a href='?%s' class='list-group-item active'>%s</a>" % (params.urlencode(), str(obj))
                    temp.append(link)
                else:
                    link = "<a href='?%s' class='list-group-item'>%s</a>" % (params.urlencode(), str(obj))
                    temp.append(link)
            list_filter_links[filed] = temp
        return list_filter_links


class ModelStark(object):
    """
    默认的配置类
    self
    self.model
    self.list_display
    """
    list_display = ["__str__"]
    model_form_class = []
    list_display_links = []
    search_fields = []
    list_filter = []
    action_fields = []

    def __init__(self, model):
        self.model = model
        self.app_label = self.model._meta.app_label
        self.model_name = self.model._meta.model_name

    # action批量删除
    def patch_delete(self, queryset):
        queryset.delete()
    patch_delete.desc = "批量删除"

    # 反射解析当前查看表的增删改查url, 获取当前url
    def get_list_url(self):
        url_name = '%s_%s_query_list' % (self.app_label, self.model_name)
        _url = reverse(url_name)
        return _url

    def get_add_url(self):
        url_name = '%s_%s_add_data' % (self.app_label, self.model_name)
        _url = reverse(url_name)
        return _url

    def get_edit_url(self, obj):
        url_name = '%s_%s_edit_data' % (self.app_label, self.model_name)
        _url = reverse(url_name, args=(obj.pk, ))
        return _url

    def get_del_url(self, obj):
        url_name = '%s_%s_delete_data' % (self.app_label, self.model_name)
        _url = reverse(url_name, args=(obj.pk, ))
        return _url

    # 默认操作函数
    def edit(self, obj=None, is_header=False):
        if is_header:
            return '编辑'
        else:
            return mark_safe("<a href='%s'>编辑</a>" % self.get_edit_url(obj))

    def delete(self, obj=None, is_header=False):
        if is_header:
            return '删除'
        else:
            return mark_safe("<a href='%s'>删除</a>" % self.get_del_url(obj))

    def checkbox(self, obj=None, is_header=False):
        if is_header:
            return "选择"
        return mark_safe("<input type='checkbox' name='pk_list' value=%s>" % obj.pk)

    # 给表数据体加上第一列和最后两列
    def new_list_display(self):
        temp = []
        temp.extend(self.list_display)
        temp.insert(0, ModelStark.checkbox)
        if not self.list_display_links:
            temp.append(ModelStark.edit)
        temp.append(ModelStark.delete)
        return temp

    # search查询条件
    def get_search_condition(self, request):
        keyword = request.GET.get('keyword')
        search_condition = Q()
        if keyword:
            search_condition.connector = "or"
            for field in self.search_fields:
                search_condition.children.append((field + "__icontains", keyword), )
        return search_condition

    # filter过滤条件
    @staticmethod
    def get_filter_condition(request):
        filter_condition = Q()
        for key, val in request.GET.items():
            if key in ["page", "keyword"]:
                continue
            filter_condition.children.append((key, val), )
        return filter_condition

    # 视图函数
    def list_view(self, request):
        if request.method == "POST":
            action = request.POST.get("action")
            pk_list = request.POST.getlist("pk_list")
            if action:
                func = getattr(self, action)
                queryset = self.model.objects.filter(pk__in=pk_list)
                func(queryset)

        add_url = self.get_add_url()
        data_list = self.model.objects.all()

        # 获取搜索条件对象
        search_condition = self.get_search_condition(request)
        # 获取filter的condition
        filter_condition = self.get_filter_condition(request)
        # 数据过滤
        data_list = data_list.filter(search_condition).filter(filter_condition)
        # 分页展示
        show_list = ShowList(self, data_list, request, )

        filter_list = show_list.get_list_filter_links()
        header_list = show_list.get_headers()
        new_data_list = show_list.get_body()

        return render(request, "stark/list_view.html", locals())

    def get_new_form(self, form):
        from django.forms.boundfield import BoundField
        from django.forms.models import ModelChoiceField
        from django.forms.models import ModelMultipleChoiceField
        for bfield in form:
            # 可以看下bfield的内容  boundfield
            # print(type(bfield.field))

            # 先确认哪些标签可以加+号
            # ModelMultipleChoiceField是ModelChoiceField的子类，子类对象isinstance也能返回True
            if isinstance(bfield.field, ModelChoiceField):
                # 标志位判断是否需要渲染+号
                bfield.is_pop = True
                rel_model = self.model._meta.get_field(bfield.name).rel.to
                model_name = rel_model._meta.model_name
                app_label = rel_model._meta.app_label
                # 比如当前查看表是Book，但是要添加的却是Publish表，所以不能用get_add_url，需要自己反向解析
                _url = reverse("%s_%s_add_data" % (app_label, model_name))
                bfield.url = _url
                # 用于pop页面添加完后让添加页面选中添加项
                bfield.pop_back_id = "id_" + bfield.name  # 用于定位是给哪个字段标签添加的
        return form

    def get_model_form(self):
        if self.model_form_class:
            ModelFormClass = self.model_form_class
        else:
            class ModelFormClass(forms.ModelForm):
                class Meta:
                    model = self.model
                    fields = "__all__"
        return ModelFormClass

    def add_view(self, request):
        ModelFormClass = self.get_model_form()
        if request.method == "POST":
            form = ModelFormClass(request.POST)
            form = self.get_new_form(form)  # 如果验证失败+号需要保留
            if form.is_valid():
                obj = form.save()
                is_pop = request.GET.get("pop")
                if is_pop:
                    # pop页面存储完数据后需要将当前存储数据返回给父页面
                    text = str(obj)
                    pk = obj.pk
                    return render(request, "stark/pop.html", locals())
                return redirect(self.get_list_url())
            return render(request, "stark/add_view.html", locals())
        form = ModelFormClass()
        form = self.get_new_form(form)
        return render(request, "stark/add_view.html", locals())

    def chg_view(self, request, nid):
        ModelFormClass = self.get_model_form()
        edit_obj = self.model.objects.get(pk=nid)
        if request.method == "POST":
            form = ModelFormClass(request.POST, instance=edit_obj)  # 把要修改的编辑对象传进去，否则就成添加了
            form = self.get_new_form(form)
            if form.is_valid():
                form.save()  # update
                return redirect(self.get_list_url())
            return render(request, "stark/chg_view.html", locals())
        form = ModelFormClass(instance=edit_obj)  # 编辑对象里存放着要展示的编辑数据
        form = self.get_new_form(form)
        return render(request, "stark/chg_view.html", locals())

    def del_view(self, request, nid):
        list_url = self.get_list_url()
        if request.method == "POST":
            self.model.objects.get(pk=nid).delete()
            return redirect(list_url)
        return render(request, "stark/del_view.html", locals())

    # 设计url
    def get_urls(self):
        return [
            url(r'^$', self.list_view, name='%s_%s_query_list' % (self.app_label, self.model_name)),
            url(r'^add/$', self.add_view, name='%s_%s_add_data' % (self.app_label, self.model_name)),
            url(r'^(\d+)/change/$', self.chg_view, name='%s_%s_edit_data' % (self.app_label, self.model_name)),
            url(r'^(\d+)/delete/$', self.del_view, name='%s_%s_delete_data' % (self.app_label, self.model_name)),
        ]

    @property
    def urls(self):
        return self.get_urls(), None, None


class StarkSite(object):
    """
    stark组件的全局类
    """
    def __init__(self):
        self._registry = {}

    def register(self, model, stark_class=None):
        # 设置配置类
        if not stark_class:
            stark_class = ModelStark
        self._registry[model] = stark_class(model)

    def get_urls(self):
        temp = []
        for model, model_stark in self._registry.items():
            model_name = model._meta.model_name
            app_label = model._meta.app_label
            temp.append(url(r"^%s/%s/" % (app_label, model_name), model_stark.urls, name='app_model'))
        return temp

    @property
    def urls(self):
        return self.get_urls(), None, None


site = StarkSite()
