from rest_framework import serializers
from RoutePlot_APP.models import StationInfo, RouteInfo, RouteStationInfo


class RouteStationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteStationInfo
        fields = '__all__'


class StationInfoSerializer(serializers.ModelSerializer):
    # station_information = RouteStationInfoSerializer(many=True, read_only=True)
    station_information = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = StationInfo
        fields = '__all__'
    
class RouteInfoSerializer(serializers.ModelSerializer):
    # route_information = RouteStationInfoSerializer(many=True, read_only=True)
    route_information = serializers.StringRelatedField(many=True, read_only=True)
    

    class Meta:
        model = RouteInfo
        fields = '__all__'



 #This api key works fine ..
 # https://api.thingspeak.com/channels/2417089/feeds.json?api_key=GUSP9F8XLDNG8VV0&results=5

    

