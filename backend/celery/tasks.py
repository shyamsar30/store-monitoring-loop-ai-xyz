from datetime import datetime
from celery import shared_task
import pandas as pd

from backend.celery.helpers import calculate_time, get_mean_time
from backend.database.dao import store_status_dao

@shared_task()
def generate_report(current_timestamp):

    # DF to store the calcualted results
    df = pd.DataFrame(columns=[
        'store_id',
        'uptime_last_hour',
        'uptime_last_day',
        'uptime_last_week',
        'downtime_last_hour',
        'downtime_last_day',
        'downtime_last_week'
    ])

    index = 0

    all_store_ids = store_status_dao.get_all_ids()
    all_store_ids = [record.store_id for record in all_store_ids]

    # Calculate timings one-by-one
    for store_id in all_store_ids[:100]:

        store_status = store_status_dao.get_store_status(current_timestamp, store_id)

        day_wise_status = {}

        # Separate each day's records
        for _ in store_status:
            if day_wise_status.get((_.timestamp_utc).weekday()):
                day_wise_status[(_.timestamp_utc).weekday()].append({
                    "timestamp_utc": _.timestamp_utc,
                    "status": _.status
                })
            else:
                day_wise_status[(_.timestamp_utc).weekday()] = [{
                    "timestamp_utc": _.timestamp_utc,
                    "status": _.status
                }]

        bins = {}


        # Make bins of time interval
        for key in day_wise_status.keys():
            data = day_wise_status[key]

            size = len(data)
            i = 0
            j = 1
            start = data[i]['timestamp_utc']
            while i < size and j+1 < size:
                if data[i]['status'] == data[j]['status']:
                    j = j + 1
                else:
                    if bins.get(key):
                        bins[key].append(
                            {
                                "start": start,
                                "end": get_mean_time(data[j-1]['timestamp_utc'], data[j]['timestamp_utc']),
                                "status": data[i]['status']
                            }
                        )
                    else:
                        bins[key] = [{
                                "start": start,
                                "end": get_mean_time(data[j-1]['timestamp_utc'], data[j]['timestamp_utc']),
                                "status": data[i]['status']
                            }]

                    start = get_mean_time(data[j-1]['timestamp_utc'], data[j]['timestamp_utc'])
                    i = j
                    j = j + 1
            
            if bins.get(key):
                bins[key].append(
                    {
                        "start": start,
                        "end": get_mean_time(data[j-1]['timestamp_utc'], data[j]['timestamp_utc']),
                        "status": data[i]['status']
                    }
                )
            else:
                bins[key] = [{
                    "start": start,
                    "end": get_mean_time(data[j-1]['timestamp_utc'], data[j]['timestamp_utc']),
                    "status": data[i]['status']
                }]
                    
        result = calculate_time(store_id, bins, datetime.strptime(current_timestamp, "%Y-%m-%d %H:%M:%S.%f"))   

        df.loc[index] = {
            "store_id": store_id,
            'uptime_last_hour': result[0],
            'uptime_last_day': result[1],
            'uptime_last_week': result[2],
            'downtime_last_hour': result[3],
            'downtime_last_day': result[4],
            'downtime_last_week': result[5]
        }

        print(index)
        index = index + 1

    df.to_csv('data.csv', index=False)