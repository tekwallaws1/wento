from datetime import date, datetime, timedelta 

#function take input of the datestring like 2017-05-01
def get_financial_year(datestring):
	date = datetime.strptime(datestring, "%Y-%m-%d").date()
	#initialize the current year
	year_of_date=date.year
	#initialize the current financial year start date
	financial_year_start_date = datetime.strptime(str(year_of_date)+"-04-01","%Y-%m-%d").date()
	if date<financial_year_start_date:
	        # return 'April, '+ str(financial_year_start_date.year-1)+' to March, '+ str(financial_year_start_date.year)
	        return (str(financial_year_start_date.year-1))[-2:]+'-'+(str(financial_year_start_date.year))[-2:]
	else:
	        # return 'April, '+ str(financial_year_start_date.year)+' to March, '+ str(financial_year_start_date.year+1)
	        return (str(financial_year_start_date.year))[-2:]+'-'+(str(financial_year_start_date.year+1))[-2:]


def get_fy_date():
	date = datetime.strptime(date.today(), "%Y-%m-%d").date()
	#initialize the current year
	year_of_date=date.year
	financial_year_start_date = datetime.strptime(str(year_of_date)+"-04-01","%Y-%m-%d").date()
	return financial_year_start_date
