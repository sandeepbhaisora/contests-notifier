import time
import notify2
import requests
import json
import datetime
import socket

notify2.init("Test")
site_url = 'https://kontests.net/api/v1'



is_connected = False
iterations = 0
#initializing notification
print("starting script")
n =  notify2.Notification(None)
n.set_urgency(notify2.URGENCY_NORMAL)

#checking if network connection is available
while not is_connected:
    print('test')
    if(iterations > 12):
        break
    try:
        socket.create_connection(("1.1.1.1",53))
        is_connected =True
        break
    except OSError:
        print('not able to connect to network')
        iterations +=1
        print('waiting for another 5 Seconds')
        time.sleep(5)

if is_connected:
    print("got connection fetc data ...")
    try:
        response = requests.get(f'{site_url}/sites')
#lists of all the sites
        sites = []
        contest_info = []
    
        if response.status_code == 200:
            res = response.json()
            for r in res:
                sites.append(r[1])
            print(sites)
            for site_name in sites:
                print("============================")
                print(f'site found {site_name}')
                print(f'getting data for site:{site_name}')
                data =  requests.get(f'{site_url}/{site_name}')
                if  data.status_code == 200:
                    contests = data.json()
                    #print(f'data found for {site_name} => {contests}')

                    for contest in contests:
                        print(contest)
                        if(contest['in_24_hours'] == 'Yes'):
                            #getting remaining time logic needs to change
                            starts_in  = contest['start_time']
                            # %Y-%m-%dT%H:%M:%S.%LZ this is the format in utc
                            #removing y m and d not required
                            starts_in = starts_in.split('T',1)[1]
                            #removing extra stuff
                            starts_in = starts_in.split('.',1)[0]
                            start_h = starts_in.split(':',1)[0]
                            start_m = starts_in.split(':',1)[1].split(':',1)[0]
                            start_in_minutes = int(start_h)*60 + int(start_m)
                            #current time in utc
                            current_h= datetime.datetime.utcnow().hour
                            current_min = datetime.datetime.utcnow().minute
                            current_time_in_minutes = current_h*60 +current_min

                            remaining_time = (start_in_minutes - current_time_in_minutes)/60
                            if remaining_time< 0 :
                                remaining_time +=24

                            remaining_time = str(remaining_time) + ' Hours'
                            contes_data = {
                                'name':site_name,
                                'contest':contest['name'],
                                'starts_in':remaining_time
                            }

                            contest_info.append(contes_data)
                else:
                    print(f'data not found for site:{site_name} with status:{data.status_code}')

            print(contest_info)
        else:
            print(f'data not found code:{status_code}')



        n.set_timeout(30000)
        n.update('Contests Today',json.dumps(contest_info,indent = 3))
    except:
        n.set_timeout(1000)
        n.update('Contests Today','Error occured while fetching data')
else:
    print('not connected to internet')
    n.set_timeout(10000)
    n.update('Contests today','not able to connect to network')
n.show()
