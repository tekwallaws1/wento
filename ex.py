vndr = VendDt.objects.all()
  print(Vendor_Invoices.objects.filter(Due_Amount__lt=0).values_list('Due_Amount'))
  ex, du, exceed = 0, 0, 0
  for v in vndr:
    b = Vendor_Invoices.objects.filter(PO_No__Vendor=v, PO_No__Related_Project__Short_Name='Supplies')
    tb = sum(b.values_list('Invoice_Amount', flat=True))
    due = sum(b.values_list('Due_Amount', flat=True))
    p = Vendor_Payment_Status.objects.filter(PO_No__Vendor=v, PO_No__Related_Project__Short_Name='Supplies')
    pp = sum(p.values_list('Paid_Amount', flat=True))


    if tb == pp:
      print('equal', due, v.Supplier_Name)
    elif tb > pp:
      du = tb - pp
      print('less', du, due, v.Supplier_Name)
    else:
      ex = pp - tb
      exceed = exceed + ex
      print('exceed', ex, due, v.Supplier_Name)

  # return HttpResponse(exceed)


  for x in Projects.objects.all():
    for p in Pages.objects.filter(Related_Project=Projects.objects.all()[0]):
      if p.Page not in Pages.objects.filter(Related_Project=x).values_list('Page', flat=True):
        cretae = Pages.objects.create(Page=p.Page, Related_Project=x)
        cretae.Mode.add(*(p.Mode.all()))
        cretae.RC.add(*(CompanyDetails.objects.all()))
  return HttpResponse('k')