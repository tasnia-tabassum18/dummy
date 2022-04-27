from django.urls import path
from . import views

app_name = 'revenue'
urlpatterns = [

  path ('', views.Revenue, name='Revenue'),

 
#path ('', views.chart_stats, name='chart_stats'),

]