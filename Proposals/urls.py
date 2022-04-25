from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static
# from .views import GeneratePdf


urlpatterns = [
    path('proposalsdashboard', views.Prop_Dashboard, name='propdb'),
    path('proposalform/', views.Proposal_Form, name='pform'),
    path('proposalslist/', views.Proposals, name='prop'),
    path('quote/<fnc>/<var>/', views.Gen_Quote, name='quote'),
    path('myquote/<var>/<var1>/', views.Gen_Quote1, name='quote1'), 
    path('quoteedit/<var>/', views.Quote_Edit, name='qtedit'),
    path('proposaledit/<var>/', views.Prop_Edit, name='propedit'),
    path('proposalcopy/<var>/', views.Prop_Copy, name='propcopy'),
    path('fillforms/<fnc>/<var>/<rid>/', views.Forms, name='form'),
    path('masterdatas/<var>/', views.Master_Data, name='mdata'), 

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


 