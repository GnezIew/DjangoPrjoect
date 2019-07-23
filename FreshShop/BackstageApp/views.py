import hashlib

from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from BackstageApp.models import *
# Create your views here.

#判断该用户啊是否存在店铺
def is_store(request):
    user_id = request.COOKIES.get('user_id')
    if user_id:
        user_id = int(user_id)
    else:
        user_id = 0
    # 通过用户查询店铺是否存在(店铺和用户通过用户的id进行关联)
    store = Store.objects.filter(user_id=user_id).first()
    if store:
        is_store = 1
    else:
        is_store = 0
    return is_store
#登录装饰器
def loginValid(func):
    """
    进行登录校验
    如果cookie当中username和session当中的username不一致认为用户不合法
    """
    def inner(request,*args,**kwargs):
        username = request.COOKIES.get('username')
        session_user = request.session.get('username')
        if username and session_user:
            user = Seller.objects.filter(username=username).first()
            if user and session_user == username:
                return func(request,*args,**kwargs)
        return HttpResponseRedirect('/backstage/login/')
    return inner

#密码加密
def set_password(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    return md5.hexdigest()

#注册
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            seller = Seller()
            seller.username = username
            seller.password = set_password(password)
            seller.nickname = username
            seller.save()
            return HttpResponseRedirect('/backstage/login/')
    return render(request,'BackstageApp/register.html')


#登录
def login(request):
    """
    登录功能，如果登录成功，跳转到首页
    如果失败，跳转到登录页
    """
    response = render(request,'BackstageApp/login.html')
    response.set_cookie('login_from','login_page')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = Seller.objects.filter(username=username).first()
            if user:
                web_password = set_password(password)
                cookies = request.COOKIES.get('login_from')
                if user.password == web_password and cookies == 'login_page':
                    response = HttpResponseRedirect('/backstage/index')
                    response.set_cookie('username',username)
                    response.set_cookie('user_id',user.id)
                    request.session['username'] = username
                    return response
    return response

#后台管理的首页
@loginValid
def index(request):
    """
    添加检查账号是否存在店铺的逻辑
    """
    #查询当前用户是谁是否注册过店铺
    # user_id = request.COOKIES.get('user_id')
    # if user_id:
    #     user_id = int(user_id)
    # else:
    #     user_id = 0
    # #通过用户查询店铺是否存在(店铺和用户通过用户的id进行关联)
    # store = Store.objects.filter(user_id=user_id).first()
    # if store:
    #     is_store = 1
    # else:
    #     is_store = 0
    Is_store = is_store(request)
    return render(request,'BackstageApp/index.html',{'Is_store': Is_store})

#注册店铺
def register_store(request):
    type_list = StoreType.objects.all()
    if request.method == 'POST':
        post_data = request.POST #接受post数据
        store_name = post_data.get('store_name')
        store_description = post_data.get('store_description')
        store_phone = post_data.get('store_phone')
        store_money = post_data.get('store_money')
        store_address = post_data.get('store_address')

        user_id = int(request.COOKIES.get('user_id'))#通过cookies来得到user_id
        type_lists = post_data.getlist('type')#通过request.post得到类型，得到的是一个列表

        store_logo = request.FILES.get('store_logo')#通过request.FILES得到
        #保存非多对多数据
        store = Store()
        store.store_name = store_name
        store.store_description = store_description
        store.store_phone = store_phone
        store.store_money = store_money
        store.store_address = store_address
        store.user_id = user_id
        store.store_logo = store_logo
        store.save() #保存，生成了数据库当中的一条数据
        #在生成的数据当中添加多对多字段
        for i in type_lists: #
            store_type = StoreType.objects.get(id = i)
            store.type.add(store_type)#添加到类型字段，多对多得映射表
        store.save()
    return render(request,'BackstageApp/register_store.html',locals())

#添加商品
def add_goods(request):
    """
    负责添加商品
    """
    Is_store = is_store(request)

    if request.method == 'POST':
        goods_name = request.POST.get('goods_name')
        goods_price = request.POST.get('goods_price')
        goods_number = request.POST.get('goods_number')
        goods_description = request.POST.get('goods_description')
        goods_date = request.POST.get('goods_date')
        goods_safeDate = request.POST.get('goods_safeDate')
        goods_store = request.POST.get('goods_store')
        goods_image = request.FILES.get('goods_image')
        #开始保存数据
        goods = Goods()
        goods.goods_name = goods_name
        goods.goods_price = goods_price
        goods.goods_number = goods_number
        goods.goods_description = goods_description
        goods.goods_date = goods_date
        goods.goods_safeDate = goods_safeDate
        goods.goods_image = goods_image
        goods.save()
        #保存多对多数据
        goods.store_id.add(
            Store.objects.get(id = int(goods_store))
        )
    return render(request,'BackstageApp/add_goods.html',locals())

#后端数据库查询
def list_goods(request):

    Is_store = is_store(request)
    keywords = request.GET.get('keywords','')
    page_num = request.GET.get('page_num',1)
    if keywords:
        goods_list = Goods.objects.filter(goods_name__contains=keywords)
    else:
        goods_list =Goods.objects.all()
    paginator = Paginator(goods_list,3)
    page = paginator.page(int(page_num)) #获取每一页的所有商品对象
    page_range = paginator.page_range
    for p in page:
        print(p)
    return render(request,'BackstageApp/goods_list.html',locals())

def base(request):
    return render(request,'BackstageApp/base.html',locals())