from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django import forms
from django.contrib import messages
from django.urls import reverse
from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json
from . import urls
from django.http import HttpResponseRedirect
from .forms import SignUpForm, EditProfileForm
import numpy as np
from joblib import load
# from .ap import apyori
# /home/wasim/users/WasimSayyed/dev/ecommerce/ecommmerce/shop/apyori.py
from ap import apyori

# Create your views here.
from django.http import HttpResponse
from ecommmerce.settings import algo


def index(request):
    #algo = load(r'/home/wasim/users/WasimSayyed/dev/ecommerce/ecommmerce/shop/items.pkl')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
    return render(request, 'shop/contact.html')


# def tracker(request):
#     if request.method=="POST":
#         orderId = request.POST.get('orderId', '')
#         email = request.POST.get('email', '')
#         try:
#             order = Orders.objects.filter(order_id=orderId, email=email)
#             if len(order)>0:
#                 update = OrderUpdate.objects.filter(order_id=orderId)
#                 updates = []
#                 for item in update:
#                     updates.append({'text': item.update_desc, 'time': item.timestamp})
#                     response = json.dumps([updates, order[0].items_json], default=str)
#                 return HttpResponse(response)
#             else:
#                 return HttpResponse('{}')
#         except Exception as e:
#             return HttpResponse('{}')

#     return render(request, 'shop/tracker.html')

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<3:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)



# def login_user(request):
#     if request.method=='POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('ShopHome')
#             # return HttpResponseRedirect(reverse('index', kwargs={}))
#         else:
#             return redirect('login')
#
#     else:
#         return render(request, 'shop/login_user.html', {})

# def productView(request, t_name):
#     # u = User.objects.get(username=username)
#     product = Product.objects.filter(name=t_name)
#     return render(request,'shop/prodView.html', {'product':product})

def productView(request, myid):

    #Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request,'shop/prodView.html', {'product':product[0]})


def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
    return render(request, 'shop/checkout.html')


def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        try:
            if user is not None:
                login(request, user)
                messages.success(request, ('You have successfully logged In!'))
                # return HttpResponseRedirect(reverse('/shop/', kwargs={'pk': pk}))

                return redirect('ShopHome')
                # return render(request, '/shop/')

            else:
                messages.success(request, ('Error - logging in - Please try again'))
                return redirect('login')

        except Exception as e:
            # return HttpResponseRedirect(reverse('/shop/', kwargs={'pk': pk}))

            return redirect('ShopHome')


    else:
            return render(request, 'shop/login_user.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ('Logged out successfully'))
    return redirect('ShopHome')

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # user = authenticate(username=username, password=password)
            # login(request, user)
            messages.success(request, ('you have registered sucessfully ...'))
            return redirect('ShopHome')
    else:
        form = SignUpForm()
    context = {'form' : form}
    return render(request, 'shop/register_user.html', context)

def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
           
            messages.success(request, ('You have Edited Your Profile ...'))
            return redirect('ShopHome')
    else:
        form = EditProfileForm(instance=request.user)
    context = {'form' : form}
    return render(request, 'shop/edit_profile.html', context)

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, ('You have Changed Your Password ...'))
            return redirect('ShopHome')
    else:
        form = PasswordChangeForm(user=request.user)
    context = {'form' : form}
    return render(request, 'shop/change_password.html', context)



# def img_scrapper(request):
#     #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# # Created on Sun Mar 31 13:29:01 2019

# # @author: wasim

#     import os
#     import sys
#     import webbrowser
#     import requests
#     import re
#     import csv

#     from bs4 import BeautifulSoup
#     from contextlib import closing
#     from selenium.webdriver import Firefox # pip install selenium
#     from selenium.webdriver.support.ui import WebDriverWait


#     #f = open('desc_extra.csv', 'w')
#     #header = 'Description,img_url\n'
#     #f.write(header)
#     import http.client
#     http.client.HTTPConnection._http_vsn = 10
#     http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'


#     desc=[]
#     f=open('desc.csv', 'r')
#     for row in f:
#         desc.append(row.strip())

#     fo = open('desc_img.csv', 'a')
#     header = 'Description, img-url\n'   
#     fo.write(header)

        
#     for data in desc:
#     ##    url = ("https://www.google.com/search?q=nfl+%s&biw=1920&bih=1009&source=lnms&tbm=isch&sa=X&ved=0ahUKEwi338XG0-3KAhVGvYMKHaqRCUEQ_AUIBigB" %(data))
#         fo = open('desc_img.csv', 'a')
#         url = "https://www.google.com/search?q=%20"+data+"&source=lnms&tbm=isch"

#         # use firefox to get page with javascript generated content
#         with closing(Firefox()) as browser:
#             browser.get(url)
#         ##     button = browser.find_element_by_name('.pdf')
#         ##     button.click()
#         # wait for the page to load
#             #WebDriverWait(browser, timeout=10)##.until(
#         ##         lambda x: x.find_element_by_id('.pdf'))
#         # store it to string variable
#             page_source = browser.page_source
#             page_source = page_source[page_source.find("Search Results"):]
#     ##        browser.get("http://www.uchicago.edu")

#         soup = BeautifulSoup(page_source, "html.parser")


#         ##print(soup.get_text())

#     ##    pdflist= []
#     ##
#     ##    docnamelist = []

#         images = [a['src'] for a in soup.find_all("img", {"src": re.compile("com")})]
        
#         #images = images[0]
#         fo.write(',' + images[2] + '\n')
#         fo.close()



# def recommend_products(request):
#     x=input("Enter a product name :\n")
#     m=[]
#     for i in range(0,len(results)): 
#         search=list(results[i][0])
#         for j in range(0,len(search)):
#             if(x==search[j]):
#                 m.append(search)
#     recommended_products=[]
#     for a in m:
#         for y in a:
#             recommended_products.append(y)
#     recommended_products=set(recommended_products)-{x}
#     print('\nrecommended products =\n')
#     print(recommended_products)


def recommend(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
        product = Product.objects.filter(name)
        pr = algo.recommend('pr')
    params = {'allProds':allProds, 'pr':pr}
    return render(request, 'shop/prodView.html' , params)

def ty(request):
    return render(request,"shop/ty.html", {})