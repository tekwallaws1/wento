from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static
# from .views import GeneratePdf


urlpatterns = [
    path('<proj>/proposalsdashboard/', views.Prop_Dashboard, name='propdb'),
    path('<proj>/proposalform/', views.Proposal_Form, name='pform'),
    path('proposalform/', views.Proposal_Form1, name='pform1'),
    path('<proj>/proposalslist/', views.Proposals, name='prop'),
    path('<proj>/quote/<fnc>/<var>/', views.Gen_Quote, name='quote'),
    path('myquote/<var>/<var1>/', views.Gen_Quote1, name='quote1'), 
    path('<proj>/quoteedit/<var>/', views.Quote_Edit, name='qtedit'),
    path('<proj>/proposaledit/<var>/', views.Prop_Edit, name='propedit'),
    path('<proj>/proposalcopy/<var>/', views.Prop_Copy, name='propcopy'),
    path('<proj>/fillforms/<fnc>/<var>/<rid>/', views.Forms, name='form'),
    path('<proj>/masterdatas/<var>/', views.Master_Data, name='mdata'), 
    path('<proj>/proposaltoorder/<var>/', views.Proposal_To_Order, name='proposaltoorder'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


 