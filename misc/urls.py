from django.urls import path

from . import views

app_name='misc'

urlpatterns = [
    path('search/', views.search, name='search'),
    path('terms/', views.terms, name='terms'),
    path('auth/', views.authenticated, name='auth'),
    path('time/', views.time, name='time'),
    path('ad/', views.ad, name='ad'),
    path('sw.js', views.swjs, name='swjs'),
    path('ads.txt', views.adstxt, name='adstxt'),
    path('robots.txt', views.robotstxt, name='robotstxt'),
    path('idscan/', views.idscan, name='idscan'),
    path('sitemap.xml', views.sitemap, name='sitemap'),
    path('news.xml', views.news, name='news'),
]
