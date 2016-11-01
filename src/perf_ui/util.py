import datetime
import re

def get_test_content_number(content_names):
    if content_names.find('[') < 0:
        return content_names.split('_')[-1]
    
    p = r'.*\[(\d+)~(\d+)\]/*\S*'  # match test_[1,13]
    t = re.findall(p, content_names.strip())
    if len(t) > 0:
        return t[0][1]
    else:
        return 0

def get_current_day_start_date(d_time=datetime.datetime.utcnow(), t_format="%Y-%m-%d %H:%M:%S"):
    time_string = '%s-%s-%s 00:00:00' % (d_time.year, d_time.month, d_time.day)
    dt = datetime.datetime.strptime(time_string, t_format)
    return dt

def get_datetime_after(t_date=datetime.datetime.utcnow(), delta_seconds=0, delta_minutes=0, delta_hours=0, delta_days=0, delta_milliseconds=0):
    return t_date + datetime.timedelta(seconds=delta_seconds, minutes=delta_minutes, hours=delta_hours, days=delta_days, milliseconds=delta_milliseconds)