from datetime import datetime
day_of_year = datetime.now().timetuple().tm_yday

print("day_of_year",day_of_year)

d = "2020-01-28"
#[year,month,day] = d.split('-')
#date = datetime.datetime(year,month,day)

import datetime
date = datetime.datetime.strptime(d, '%Y-%m-%d').date()
print("date ",date)

day_of_year = date.timetuple().tm_yday
print("day_of_year",day_of_year)

