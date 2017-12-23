from django.urls import path

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^home$', views.index, name='index'),
    url(r'^index$', views.newIndex, name = 'newIndex'),
    url(r'^station$', views.station, name = 'station'),
    url(r'^reserve$', views.reserve, name = 'reserve'),
 	url(r'^trains$', views.trains, name = 'trains'),
 	url(r'^errorpage$',views.errorPage, name = 'errorpage'),
 	url(r'^station/(?P<id>\d+)/$',views.stationTimes, name = 'stationTimes`'),
	url(r'^reservation/(?P<id>\d+)/$',views.myReserv, name = 'myReserv`')
 	
 	
       
]