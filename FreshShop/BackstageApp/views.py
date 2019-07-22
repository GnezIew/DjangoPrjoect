import hashlib

from django.shortcuts import render
from django.http import HttpResponseRedirect
from BackstageApp.models import Seller
# Create your views here.

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
                    request.session['username'] = username
                    return response
    return response

@loginValid
def index(request):
    username = request.COOKIES.get('username')
    print(username)
    return render(request,'BackstageApp/index.html',locals())