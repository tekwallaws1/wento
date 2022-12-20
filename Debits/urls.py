from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('<firm>/<proj>/expensesform/<fnc>/<expid>/', views.Expenses_Form, name='expensesform'),
    path('<firm>/<proj>/expensesitemsform/<fnc>/<expid>/<itemid>/', views.Expenses_Items_Form, name='expensesitemsform'),
    path('<firm>/<proj>/expenseslist/<apr>/<expid>/', views.Expenses_List, name='expenseslist'),
    path('<firm>/<proj>/expensesclaimreceipt/<apr>/<fnc>/<expid>/<itemid>/', views.Expenses_Receipt, name='expensesclaimreceipt'),
    path('<firm>/<proj>/expensesapprovalrequests/<apr>/<expid>/', views.Exp_Approval_Req, name='expensesapprovalrequests'),

    path('<firm>/<proj>/debitlist/', views.Debit_List, name='debitlist'),
    path('<firm>/<proj>/debitform/<fnc>/<did>/', views.Debit_Form, name='debitform'),
    path('<firm>/<proj>/debitreceipt/<did>/', views.Debit_Receipt, name='debitreceipt'),
    path('<firm>/<proj>/employwiseclaims/', views.Employ_Claims, name='employwiseclaims'),
    
    path('<firm>/<proj>/attendanceform/<fnc>/<eid>/<returnpage>/', views.Attendance_Form, name='attendanceform'),
    path('<firm>/<proj>/daywiseattendancelist/<day>/', views.DayWise_Attendance, name='daywiseattendancelist'),
    path('<firm>/<proj>/autoattendance/<month>/', views.Gen_Auto_Attendance, name='autoattendance'),
    path('<firm>/<proj>/monthwiseattendancelist/<month>/', views.MonthWise_Attendance, name='monthwiseattendancelist'),
    path('<firm>/<proj>/monthlyattendanceedit/<empl>/<dt>/<fnc>/', views.Month_Attendance_Edit, name='monthlyattendanceedit'),
    path('<firm>/<proj>/employwiseattendance/<month>/<empl>/', views.Employ_Wise_Attendance, name='employwiseattendance'),
    path('<firm>/<proj>/holidaysform/<fnc>/<hid>/', views.Holidays_Form, name='holidaysform'),
    path('<firm>/<proj>/holidayslist/<year>/', views.Holidays_List, name='holidayslist'),

    path('<firm>/<proj>/monthlysalariesedit/<month>/<eid>/<mode>/', views.Monthly_Salaries_Edit, name='monthlysalariesedit'),
    path('<firm>/<proj>/monthlysalaries/<month>/<mode>/', views.Gen_Monthly_Salaries, name='monthlysalaries'),
    path('<firm>/<proj>/orderwisesalaries/<month>/<mode>/', views.Get_Order_Wise_Salaries, name='orderwisesalaries'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
