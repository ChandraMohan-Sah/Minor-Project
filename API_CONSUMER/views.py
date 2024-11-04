import requests
from django.shortcuts import render
from django.http import JsonResponse
from RoutePlot_APP.models import StationInfo
import aiohttp
from asgiref.sync import sync_to_async

def Get_Routes(request):
    api_url = "http://localhost:8000/api/get-complete-routeinfo/"
    response = requests.get(api_url)

    if response.status_code == 200:
        json_data = response.json()
        routes_data = []

        for item in json_data:  # Iterate over the list directly
            route_id = item['id']
            route_actual_id = item['route_id']
            route_name = item['route_english_name']
            route_start = item['start']
            route_end = item['end']
            
            routes_data.append({'route_id': route_id,
                                'route_actual_id': route_actual_id,
                                'route_name': route_name,
                                'route_start': route_start,
                                'route_end': route_end})
    
        context = {
            "routes_variable": routes_data
        }

    return render(request, 'home.html', context)



# Helper function to asynchronously fetch station info from the database
@sync_to_async
def Get_Stations_on_Route(request, routenumber):
    api_url = f"http://localhost:8000/api/get-all-stations-on-routeid/{routenumber}/"
    response = requests.get(api_url)

    if response.status_code == 200:
        json_data = response.json()
        # Extract station IDs from the JSON data
        station_ids = [item['station_info'] for item in json_data]

        original_order_query_set = []
        for station_id in station_ids:
            station_info = StationInfo.objects.filter(id=station_id).values(
                'station_id', 'station_english_name', 'station_latitude', 'station_longitude'
            )

            if station_info.exists():
                original_order_query_set.append(station_info.first())
        
        data = get_bus_location(routenumber=routenumber) # not working as expected

        context = {
            "stations_variable": list(original_order_query_set),  # Ensure the QuerySet is converted to a list
            "bus_location":data
        }

    else:
        context = {
            "stations_variable": [],
            "bus_location": None
        }

    return render(request, 'home2.html', context)




async def get_bus_location(routenumber):
    api_url2 = "https://api.thingspeak.com/channels/2417089/feeds.json?api_key=GUSP9F8XLDNG8VV0&results=1"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url2) as response:
            if response.status == 200:
                json_data = await response.json()
                x = int(json_data['feeds'][0]['field1'])
                device_data = [] 
            
                if x == routenumber:
                    return {
                        "device_id": int(json_data['feeds'][0]['field1']),
                        "current_latitude": json_data['feeds'][0]['field2'],
                        "current_longitude": json_data['feeds'][0]['field3']
                    }
            else:
                return {
                    "device_id": None,
                    "current_latitude": None,
                    "current_longitude": None
                }


async def bus_location_view(request, routenumber):
    # Await the result of get_bus_location without re-passing routenumber
    data = await get_bus_location(routenumber=routenumber)
    return JsonResponse(data, safe=False)


































def Post_GPS_Location(request, deviceid, latitude, longitude):
    latitude = float(latitude)
    longitude = float(longitude)
    api_url1 = "http://localhost:8000/api/post_realtime_gps_data/"
    api_url2 = "http://localhost:8000/api/post_to_backup_gps_data/"

    data1 = {
        'current_latitude': latitude,
        'current_longitude': longitude,
        'current_device_id': deviceid,
    }

    data2 = {
        'backup_latitude': latitude,
        'backup_longitude': longitude,
        'backup_device_id': deviceid,
    }

    try:
        response1 = requests.post(api_url1, json=data1)
        response1.raise_for_status()
        print(response1)

        response2 = requests.post(api_url2, json=data2)
        response2.raise_for_status()
        print(response2)

    except requests.exceptions.HTTPError as err:
        return JsonResponse({'error': f"HTTP error occurred: {err}"}, status=500)

    except requests.exceptions.ConnectionError as e:
        # Handle connection errors
        return JsonResponse({'error': f"Error connecting to the server: {e}"}, status=500)

    except requests.exceptions.Timeout as e:
        # Handle timeouts
        return JsonResponse({'error': f"Request timed out: {e}"}, status=500)

    except requests.exceptions.RequestException as e:
        # Handle other types of request exceptions
        return JsonResponse({'error': f"Error: {e}"}, status=500)

    # If everything is successful, return a JsonResponse
    data = {
        'backup_device_id': deviceid,
        'backup_latitude': latitude,
        'backup_longitude': longitude,
        'current_device_id': deviceid,
        'current_latitude': latitude,
        'current_longitude': longitude
    }

    return JsonResponse(data)


# def home(request):
#     return render(request, 'base1.html')





'''
{"my_location_name": "hanumanthan", 
"my_location_lat-long": [27.6885029, 85.3160104], 

"nearest_user_station_id": 3529, 
"nearest_user_station_english_name": "Kupandol", 
"nearest_user_station_lat-long": [27.687809242186514, 85.31633835285902], 
"nearest_dest_station_id": 1096, 

"nearest_dest_station_english_name": "Sinamangal Bus Route Point",
"nearest_dest_station_lat-long": [27.6952988, 85.3550202], 

"dest_location_name": "Tribhuvan International Airport", 
"dest_location_lat_long": [27.6939119, 85.3582197389141]
}


'''





