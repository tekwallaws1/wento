from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('<proj>/expensesform/<fnc>/<expid>/', views.Expenses_Form, name='expensesform'),
    path('<proj>/expensesitemsform/<fnc>/<expid>/<itemid>/', views.Expenses_Items_Form, name='expensesitemsform'),
    path('<proj>/expenseslist/<apr>/<expid>/', views.Expenses_List, name='expenseslist'),
    path('<proj>/expensesclaimreceipt/<apr>/<fnc>/<expid>/<itemid>/', views.Expenses_Receipt, name='expensesclaimreceipt'),
    path('<proj>/expensesapprovalrequests/<apr>/<expid>/', views.Exp_Approval_Req, name='expensesapprovalrequests'),

    path('<proj>/debitlist/', views.Debit_List, name='debitlist'),
    path('<proj>/debitform/<fnc>/<did>/', views.Debit_Form, name='debitform'),
    path('<proj>/debitreceipt/<did>/', views.Debit_Receipt, name='debitreceipt'),
    
    path('<proj>/attendanceform/<fnc>/<eid>/<returnpage>/', views.Attendance_Form, name='attendanceform'),
    path('<proj>/daywiseattendancelist/<day>/', views.DayWise_Attendance, name='daywiseattendancelist'),
    path('<proj>/autoattendance/<month>/', views.Gen_Auto_Attendance, name='autoattendance'),
    path('<proj>/monthwiseattendancelist/<month>/', views.MonthWise_Attendance, name='monthwiseattendancelist'),
    path('<proj>/employwiseattendance/<month>/<empl>/', views.Employ_Wise_Attendance, name='employwiseattendance'),
    path('<proj>/holidaysform/<fnc>/<hid>/', views.Holidays_Form, name='holidaysform'),
    path('<proj>/holidayslist/<year>/', views.Holidays_List, name='holidayslist'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 