import datetime

from backend.database.datatypes import StoreStatusTypes
from backend.database.dao import menu_hours_dao

# Generate store staring and ending time dictonary for a store
def get_start_end_time_utc(store_id):

    records = menu_hours_dao.get_start_end_time_utc_by_store_id(store_id)

    if records:
        if not records[0].start_time:
            records = menu_hours_dao.get_null_menu_hours(store_id)

    dic = {}

    for record in records:
        if dic.get(record.day):
            dic[record.day].append((record.start_time, record.end_time))
        else:
            dic[record.day] = [(record.start_time, record.end_time)]

    for i in range(0,7):
        if not dic.get(i):
            dic[i] = [(datetime.time(hour=0, minute=0, second=1), datetime.time(hour=23, minute=59, second=59))]

    return dic

def get_mean_time(t1, t2):
    t1 = t1.timestamp()
    t2 = t2.timestamp()

    return datetime.datetime.fromtimestamp(int((t1 + t2)/2))

# Start Calculating time
def calculate_time(store_id, bins, current_timestamp):
    start_end_time_dic = get_start_end_time_utc(store_id)

    current_day = current_timestamp.weekday()
    last_day = current_day - 1 if current_day > 0 else 6

    current_time = datetime.datetime.strptime(str(current_timestamp)[11:19], '%H:%M:%S').time()


    store_start_time = start_end_time_dic[last_day][0][0]
    store_start_time = datetime.datetime.strptime(str(store_start_time), '%H:%M:%S')
    store_end_time = start_end_time_dic[last_day][0][1]
    store_end_time = datetime.datetime.strptime(str(store_end_time), '%H:%M:%S')

    last_hr_uptime = 0
    last_hr_downtime = 0

    # Calculate Current Day's timings
    if bins.get(current_day):

        store_start_time = start_end_time_dic[current_day][0][0]
        store_start_time = datetime.datetime.strptime(str(store_start_time), '%H:%M:%S')

        store_end_time = start_end_time_dic[current_day][0][1]
        store_end_time = datetime.datetime.strptime(str(store_end_time), '%H:%M:%S')

        last_hr_data = calculate_last_hr(bins[current_day], current_timestamp, store_start_time, store_end_time)
        last_hr_uptime = last_hr_data[0]/60.0
        last_hr_downtime = last_hr_data[1]/60.0

    last_day_uptime = 0
    last_day_downtime = 0

    # Calculate Last Day's timings
    if bins.get(last_day):
        last_day_uptime = calculate_one_day(store_start_time, store_end_time, bins[last_day])/3600.0

        last_day_downtime = get_total_hours_between(store_start_time, store_end_time) - last_day_uptime


    days = [0,1,2,3,4,5,6]
    days.remove(last_day)

    last_week_uptime = last_day_uptime
    last_week_downtime = last_day_downtime

    # Calculate rest days timing
    for day in days:

        store_start_time = start_end_time_dic[day][0][0]
        store_start_time = datetime.datetime.strptime(str(store_start_time), '%H:%M:%S')

        store_end_time = start_end_time_dic[day][0][1]
        if day == current_day and store_end_time > current_time:
            store_end_time = current_time
        store_end_time = datetime.datetime.strptime(str(store_end_time), '%H:%M:%S')

        if bins.get(day):
            this_day = calculate_one_day(store_start_time, store_end_time, bins[day])/3600.0
            last_week_uptime += this_day
            last_week_downtime += get_total_hours_between(store_start_time, store_end_time) - this_day

    return (
        last_hr_uptime,
        last_day_uptime,
        last_week_uptime,
        last_hr_downtime,
        last_day_downtime,
        last_week_downtime
    )
            
# Calculate for one day based on parameters
def calculate_one_day(store_start_time, store_end_time, data):

    result = 0

    tn_end = data[-1]['end'].time()
    tn_end = datetime.datetime.strptime(str(tn_end)[:8], '%H:%M:%S')

    t0_start = data[0]['start'].time()
    t0_start = datetime.datetime.strptime(str(t0_start)[:8], '%H:%M:%S')


    if store_start_time < store_end_time:

        # start time after last interval
        if store_start_time > tn_end:
            if data[-1]['status'] == StoreStatusTypes.ACTIVE:
                result += (store_end_time - store_start_time).total_seconds()
            return result
        
        # end time before first interval
        if t0_start > store_end_time:
            if data[0]['status'] == StoreStatusTypes.ACTIVE:
                result += (store_end_time - store_start_time).total_seconds()
            return result
        
        # start time before first interval
        if store_start_time < t0_start:
            if data[0]['status'] == StoreStatusTypes.ACTIVE:
                result += (t0_start - store_start_time).total_seconds()

        # end time after last interval
        if store_end_time > tn_end:
            if data[-1]['status'] == StoreStatusTypes.ACTIVE:
                result += (store_end_time - tn_end).total_seconds()
        
        for bin in data:

            bin_start = bin['start'].time()
            bin_start = datetime.datetime.strptime(str(bin_start)[:8], '%H:%M:%S')

            bin_end = bin['end'].time()
            bin_end = datetime.datetime.strptime(str(bin_end)[:8], '%H:%M:%S')

            # if whole bussiness hour inside the interval
            if (bin_start <= store_start_time and store_end_time <= bin_end):
                if bin['status'] == StoreStatusTypes.ACTIVE:
                    result += (store_end_time - store_start_time).total_seconds()
                continue

            # Inter - interval
            if (bin_start <= store_start_time and store_start_time < store_start_time):
                if bin['status'] == StoreStatusTypes.ACTIVE:
                    result += (bin_end - store_start_time).total_seconds()
            if (bin_start < store_end_time and store_end_time <= bin_end):
                if bin['status'] == StoreStatusTypes.ACTIVE:
                    result += (bin_start - store_end_time).total_seconds()
            
        return result

    else:

        # if start-time is in upper part of bins
        if store_start_time < t0_start:
            if data[0]['status'] == StoreStatusTypes.ACTIVE:
                result += (t0_start - store_start_time).total_seconds()
        
        # if start-time is in lower part of bins
        if store_start_time >= tn_end:
            if data[-1]['status'] == StoreStatusTypes.ACTIVE:
                result += (datetime.datetime.strptime('23:59:59', '%H:%M:%S') - store_start_time).total_seconds()

        # if end-time is in upper part of bins
        if store_end_time <= t0_start:
            if data[0]['status'] == StoreStatusTypes.ACTIVE:
                result += (store_end_time - datetime.datetime.strptime('00:00:01', '%H:%M:%S')).total_seconds()

        # if end-time is in lower part of bins
        if store_end_time >= tn_end:
            if data[-1]['status'] == StoreStatusTypes.ACTIVE:
                result += (store_start_time - store_end_time).total_seconds()

        for bin in data:

            bin_start = bin['start'].time()
            bin_start = datetime.datetime.strptime(str(bin_start)[:8], '%H:%M:%S')

            bin_end = bin['end'].time()
            bin_end = datetime.datetime.strptime(str(bin_end)[:8], '%H:%M:%S')

            # if store-end-time inbetween bin-interval
            if bin_start < store_end_time and store_end_time <= bin_end:
                if bin['status'] == StoreStatusTypes.ACTIVE:
                    result += (store_end_time - bin_start).total_seconds()

            # when store-start-time inbetwwen interval
            if bin_start <= store_start_time and store_start_time < bin_end:
                if bin['status'] == StoreStatusTypes.ACTIVE:
                    result += (bin_end - store_start_time).total_seconds()
        
    return result

# Calculate timings for last hour data
def calculate_last_hr(data, current_timestamp, store_start_time, store_end_time):
    uptime = 0
    downtime = 0

    tn_end = data[-1]['end'].time()
    tn_end = datetime.datetime.strptime(str(tn_end)[:8], '%H:%M:%S')

    t0_start = data[0]['start'].time()
    t0_start = datetime.datetime.strptime(str(t0_start)[:8], '%H:%M:%S')

    lower = datetime.datetime.strptime(str(current_timestamp)[11:19], '%H:%M:%S')
    upper = lower - datetime.timedelta(hours=1)


    # if last hr in upper of bins
    if lower < store_start_time:
        return (0, 0)
    
    # if last hr in lower of bins
    if upper > store_end_time:
        return (0, 0)
    
    # ---> update upper and lower to bussiness hours <---
    if upper < store_start_time and lower > store_start_time:
        upper = store_start_time
    elif upper < store_end_time and lower > store_end_time:
        lower = store_end_time

    

    for bin in data[::-1]:
        
        bin_start = bin['start'].time()
        bin_start = datetime.datetime.strptime(str(bin_start)[:8], '%H:%M:%S')

        bin_end = bin['end'].time()
        bin_end = datetime.datetime.strptime(str(bin_end)[:8], '%H:%M:%S')

        if upper >= bin_end:
            break

        if lower <= bin_end and upper > bin_start:
            if bin['status'] == StoreStatusTypes.ACTIVE:
                uptime += (lower - upper).total_seconds()
            else:
                downtime += (lower - upper).total_seconds()
        
        if lower <= bin_end and upper < bin_start:
            if bin['status'] == StoreStatusTypes.ACTIVE:
                uptime += (lower - bin_start).total_seconds()
            else:
                downtime += (lower - bin_start).total_seconds()

        if bin_start <= upper and lower > bin_end:
            if bin['status'] == StoreStatusTypes.ACTIVE:
                uptime += (bin_end - upper).total_seconds()
            else:
                downtime += (bin_end - upper).total_seconds()

    return (uptime, downtime)

def get_minutes_between_two_time(t2, t1):
    return ((t2 - t1).total_seconds())/60.0
  
# For calculating total business hours
def get_total_hours_between(start, end):
    if start < end:
        return (((end - start).total_seconds())/60.0)/60.0
    else:
        day_end = datetime.datetime.strptime("23:59:59", '%H:%M:%S')
        day_start = datetime.datetime.strptime("00:00:01", '%H:%M:%S')
        return ((
            (day_end - start).total_seconds() + (end - day_start).total_seconds()
        )/60.0)/60.0