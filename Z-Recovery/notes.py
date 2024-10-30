'''You have used async functions:

--------------------------------------------One ChatGPT Question -----------------------------
folder heirarchy :

API_CONSUMER : it is not any djnago app
  	-views.py
	-consumers.py
	-routers.py

PROJECT_MAP_API : main project folder 
	-settings.py
	-asgi.py
	-wsgi.py

Other apps

templates
	-index.html
static


---------------------------------------------------
inside views.py of API_CONSUMER I have a list of functions'''


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


# Define an asynchronous function to fetch station info using database_sync_to_async
@database_sync_to_async
def get_station_info_async(station_ids):
    original_order_query_set = []
    for station_id in station_ids:
        station_info = StationInfo.objects.filter(id=station_id).values(
            'station_id', 'station_english_name', 'station_latitude', 'station_longitude'
        )

        if station_info.exists():
            original_order_query_set.append(station_info.first())

    return original_order_query_set





def get_nearest_station(stations, bus_location, radius=300):  # Default radius of 300 meters
    nearest_station = None
    nearest_distance = float('inf')

    for station in stations:
        station_location = (float(station['station_latitude']), float(station['station_longitude']))
        distance = geodesic(bus_location, station_location).meters

        if distance <= radius and distance < nearest_distance:
            nearest_station = station
            nearest_distance = distance

    return nearest_station, nearest_distance




async def Get_Stations_and_Devices_on_Route(request, routenumber):
    api_url1 = f"http://localhost:8000/api/get-all-stations-on-routeid/{routenumber}/"
    response1 = requests.get(api_url1)

    if response1.status_code == 200:
        json_data1 = response1.json()
        # Extract station IDs from the JSON data
        station_ids = [item['station_info'] for item in json_data1]

        # Use database_sync_to_async to make asynchronous database queries
        original_order_query_set = await get_station_info_async(station_ids)

        # Fetch bus location asynchronously
        loop = asyncio.get_event_loop()
        bus_location_task = loop.create_task(get_bus_location(routenumber))
        bus_location = await bus_location_task

        if bus_location is not None:  # Check if bus location is retrieved successfully
            # Extract bus location and calculate nearest station
            nearest_station, nearest_distance = get_nearest_station(original_order_query_set, (bus_location['current_latitude'], bus_location['current_longitude']))

        context = {
            "stations_variable": original_order_query_set,
            "device_variable": [{'device_id': bus_location['device_id'],
                                'current_latitude': bus_location['current_latitude'],
                                'current_longitude': bus_location['current_longitude']}],
            "current_station": nearest_station['station_english_name'] if nearest_station else None,
            "nearest_distance": nearest_distance
        }
    else:
        context = {
            "stations_variable": [],
            "device_variable": []
        }

    return render(request, 'home2.html', context)

# ----------------------------------------------------------------------------------
# Now write exact code for all asgi and other frontent as well as backend tool 
# so that websocket gets connected and real time location of get_bus_location(routenumber) can be fetched
# I am new to djnago so please write in detail


def Get_Stations_and_Devices_on_Route(request, routenumber):
    api_url1 = f"http://localhost:8000/api/get-all-stations-on-routeid/{routenumber}/"
    response1 = requests.get(api_url1)

    api_url2 = "https://api.thingspeak.com/channels/2417089/feeds.json?api_key=GUSP9F8XLDNG8VV0&results=2"
    response2 = requests.get(api_url2)

    if response1.status_code == 200 and response2.status_code == 200:
        json_data1 = response1.json()
        # Extract station IDs from the JSON data
        station_ids = [item['station_info'] for item in json_data1]

        original_order_query_set = []
        for station_id in station_ids:
            station_info = StationInfo.objects.filter(id=station_id).values(
                'station_id', 'station_english_name', 'station_latitude', 'station_longitude'
            )

            if station_info.exists():
                original_order_query_set.append(station_info.first())


        json_data2 = response2.json()
        device_data = []

        device_id = int(json_data2['feeds'][0]['field1'])
        current_latitude = json_data2['feeds'][0]['field2']
        current_longitude = json_data2['feeds'][0]['field3']

        if device_id == routenumber:
            device_data.append({'device_id': device_id,
                    'current_latitude': current_latitude,
                    'current_longitude': current_longitude})