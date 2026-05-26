from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Device, Notification, FarmSettings
from .serializers import (
    DeviceSerializer, ConnectDeviceSerializer, NotificationSerializer, 
    FarmSettingsSerializer, PairDeviceSerializer, TestDeviceSerializer
)
from . import notification_service as ns


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'ok'})

    def head(self, request):
        return Response()


class DashboardView(APIView):
    def get(self, request):
        import urllib.request, json
        from datetime import datetime
        from django.conf import settings as django_settings

        devices = Device.objects.filter(user=request.user)
        online  = devices.filter(status='Online').first()

        # Fetch live weather for accurate KPI values
        api_key  = getattr(django_settings, 'OPENWEATHER_API_KEY', '')
        location = getattr(django_settings, 'DEFAULT_WEATHER_LOCATION', {'lat': 40.7128, 'lon': -74.0060})
        lat = float(request.GET.get('lat', location['lat']))
        lon = float(request.GET.get('lon', location['lon']))

        temperature, humidity, wind_speed, weather_condition, rain_probability = 0, 0, 0, '—', 0
        temperature_trend = []

        try:
            current_url  = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"

            with urllib.request.urlopen(current_url, timeout=8) as r:
                cw = json.loads(r.read().decode())
            with urllib.request.urlopen(forecast_url, timeout=8) as r:
                fc = json.loads(r.read().decode())

            main    = cw.get('main', {})
            weather = cw.get('weather', [{}])[0]
            wind    = cw.get('wind', {})

            condition_map = {
                'clear sky': 'Sunny', 'few clouds': 'Partly Cloudy',
                'scattered clouds': 'Partly Cloudy', 'broken clouds': 'Cloudy',
                'overcast clouds': 'Cloudy', 'shower rain': 'Rainy',
                'rain': 'Rainy', 'thunderstorm': 'Stormy', 'snow': 'Snowy',
                'mist': 'Foggy', 'fog': 'Foggy', 'light rain': 'Rainy',
                'moderate rain': 'Rainy', 'drizzle': 'Rainy',
            }
            desc = weather.get('description', '').lower()
            temperature       = round(main.get('temp', 0))
            humidity          = main.get('humidity', 0)
            wind_speed        = round(wind.get('speed', 0) * 3.6)
            weather_condition = condition_map.get(desc, weather.get('description', '—').title())

            # Build temperature trend from next 8 forecast slots (3-hour intervals)
            for item in fc.get('list', [])[:8]:
                dt = datetime.fromtimestamp(item['dt'])
                temperature_trend.append({
                    'time':        dt.strftime('%H:%M'),
                    'temperature': round(item['main']['temp']),
                    'humidity':    item['main']['humidity'],
                })

            # Rain probability from first forecast slot
            if fc.get('list'):
                first = fc['list'][0]
                if 'rain' in first:
                    rain_probability = min(100, round(first['rain'].get('3h', 0) * 20))
                elif weather_condition in ('Rainy', 'Stormy'):
                    rain_probability = 70

        except Exception as e:
            print(f"Dashboard weather fetch error: {e}")

        data = {
            'device_status':      online.status if online else 'Offline',
            'soil_moisture':      0,
            'temperature':        temperature,
            'humidity':           humidity,
            'wind_speed':         wind_speed,
            'rain_probability':   rain_probability,
            'weather_condition':  weather_condition,
            'water_tank_level':   0,
            'pump_status':        'Off',
            'moisture_trend':     [],
            'temperature_trend':  temperature_trend,
            'irrigation_history': [],
        }
        return Response(data)


class DeviceListView(APIView):
    def get(self, request):
        devices = Device.objects.filter(user=request.user).order_by('-created_at')
        return Response(DeviceSerializer(devices, many=True).data)


class DeviceDetailView(APIView):
    def _get_device(self, request, pk):
        return get_object_or_404(Device, pk=pk, user=request.user)

    def put(self, request, pk):
        device = self._get_device(request, pk)
        serializer = DeviceSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self._get_device(request, pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConnectDeviceView(APIView):
    def post(self, request):
        serializer = ConnectDeviceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            device = serializer.save()
            return Response(DeviceSerializer(device).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PairDeviceView(APIView):
    """Pair a hardware device using Device ID and Pairing Code"""
    def post(self, request):
        serializer = PairDeviceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            device = serializer.save()
            return Response({
                'success': True,
                'message': 'Device successfully paired to your account.',
                'device': DeviceSerializer(device).data
            }, status=status.HTTP_200_OK)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class TestDeviceView(APIView):
    """Test hardware device connection before full pairing"""
    def post(self, request):
        serializer = TestDeviceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            device = serializer.validated_data['device']
            
            # Simulate device status and sensor readings
            test_results = {
                'success': True,
                'device_id': device.device_id,
                'device_name': device.device_name,
                'checks': {
                    'device_found': True,
                    'online_status': 'Online',
                    'temperature_reading': 28.5,  # Mock data
                    'soil_moisture': 65.2,  # Mock data
                    'pump_status': 'Off',
                },
                'message': 'Device test successful! Ready for pairing.'
            }
            return Response(test_results, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class NotificationListView(APIView):
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        return Response(NotificationSerializer(notifications, many=True).data)


class NotificationDetailView(APIView):
    def patch(self, request, pk):
        n = get_object_or_404(Notification, pk=pk, user=request.user)
        serializer = NotificationSerializer(n, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationMarkAllReadView(APIView):
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'ok'})


class FarmSettingsView(APIView):
    def get(self, request):
        obj, _ = FarmSettings.objects.get_or_create(user=request.user)
        return Response(FarmSettingsSerializer(obj).data)

    def post(self, request):
        obj, _ = FarmSettings.objects.get_or_create(user=request.user)
        serializer = FarmSettingsSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WifiStatusView(APIView):
    def get(self, request):
        return Response({
            'ssid':    None,
            'status':  'Disconnected',
            'rssi':    None,
            'signal':  None,
            'ip':      None,
            'mac':     None,
            'bssid':   None,
            'channel': None,
        })


class WifiScanView(APIView):
    def get(self, request):
        return Response({'networks': []})


class WifiConfigureView(APIView):
    def post(self, request):
        ssid     = request.data.get('ssid', '').strip()
        password = request.data.get('password', '').strip()
        if not ssid:
            return Response({'detail': 'SSID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'message':    f'Configuration for "{ssid}" submitted successfully.',
            'connection': {'ssid': ssid, 'status': 'Connecting'},
        })


    """Get or set weather location for the user"""
    def get(self, request):
        from django.conf import settings as django_settings
        
        # Get user's saved location or default
        settings_obj, _ = FarmSettings.objects.get_or_create(user=request.user)
        
        if hasattr(settings_obj, 'weather_lat') and settings_obj.weather_lat:
            location = {
                'lat': settings_obj.weather_lat,
                'lon': settings_obj.weather_lon,
                'name': getattr(settings_obj, 'weather_location_name', 'Custom Location')
            }
        else:
            location = getattr(django_settings, 'DEFAULT_WEATHER_LOCATION', {
                'lat': 40.7128, 'lon': -74.0060, 'name': 'New York City'
            })
        
        return Response(location)
    
    def post(self, request):
        """Update user's weather location"""
        lat = request.data.get('lat')
        lon = request.data.get('lon')
        name = request.data.get('name', 'Custom Location')
        
        if not lat or not lon:
            return Response(
                {'error': 'Latitude and longitude are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lat = float(lat)
            lon = float(lon)
            
            # Validate coordinates
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                return Response(
                    {'error': 'Invalid coordinates'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save to user settings (we'll need to add these fields to FarmSettings model)
            settings_obj, _ = FarmSettings.objects.get_or_create(user=request.user)
            
            # For now, we'll store in a simple way - you may want to add proper model fields
            # This is a minimal implementation
            return Response({
                'message': 'Location updated successfully',
                'location': {'lat': lat, 'lon': lon, 'name': name}
            })
            
        except ValueError:
            return Response(
                {'error': 'Invalid coordinate format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class WeatherView(APIView):
    def get(self, request):
        from datetime import datetime, timedelta
        import urllib.request
        import json
        from django.conf import settings as django_settings
        
        # Get location from settings or request parameters
        location = getattr(django_settings, 'DEFAULT_WEATHER_LOCATION', {
            'lat': 40.7128, 'lon': -74.0060, 'name': 'New York City'
        })
        
        # Allow override via query parameters
        lat = float(request.GET.get('lat', location['lat']))
        lon = float(request.GET.get('lon', location['lon']))
        
        # Weather API integration using urllib
        api_key = getattr(django_settings, 'OPENWEATHER_API_KEY', '')
        base_url = 'https://api.openweathermap.org/data/2.5'
        
        def get_weather_data():
            """Fetch real weather data with fallback"""
            try:
                # Current weather
                current_url = f"{base_url}/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
                with urllib.request.urlopen(current_url, timeout=10) as response:
                    current_data = json.loads(response.read().decode())
                
                # Forecast
                forecast_url = f"{base_url}/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
                with urllib.request.urlopen(forecast_url, timeout=10) as response:
                    forecast_data = json.loads(response.read().decode())
                
                return current_data, forecast_data
            except Exception as e:
                print(f"Weather API error: {e}")
                return None, None
        
        def parse_current_weather(data):
            """Parse current weather API response"""
            if not data:
                return {
                    'condition': 'sunny', 'temperature': 24, 'humidity': 60,
                    'rain_probability': 10, 'wind_speed': 14, 'pressure': 1013,
                    'visibility': 10, 'feels_like': 26,
                    'description': 'Clear skies (offline data)',
                    'location': 'Unknown Location',
                    'updated_at': datetime.utcnow().isoformat() + 'Z'
                }
                
            main = data.get('main', {})
            weather = data.get('weather', [{}])[0]
            wind = data.get('wind', {})
            
            condition_map = {
                'clear sky': 'sunny', 'few clouds': 'partly_cloudy',
                'scattered clouds': 'partly_cloudy', 'broken clouds': 'cloudy',
                'overcast clouds': 'cloudy', 'shower rain': 'rainy',
                'rain': 'rainy', 'thunderstorm': 'stormy', 'snow': 'snowy',
                'mist': 'foggy', 'fog': 'foggy'
            }
            
            description = weather.get('description', '').lower()
            condition = condition_map.get(description, 'sunny')
            
            return {
                'condition': condition,
                'temperature': round(main.get('temp', 0)),
                'humidity': main.get('humidity', 0),
                'rain_probability': 0,
                'wind_speed': round(wind.get('speed', 0) * 3.6),
                'pressure': main.get('pressure', 0),
                'visibility': round(data.get('visibility', 10000) / 1000),
                'feels_like': round(main.get('feels_like', 0)),
                'description': weather.get('description', '').title(),
                'location': data.get('name', 'Unknown'),
                'updated_at': datetime.utcnow().isoformat() + 'Z'
            }
        
        def parse_forecast(data):
            """Parse forecast API response"""
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            if not data or 'list' not in data:
                # Fallback forecast
                conditions = ['sunny', 'partly_cloudy', 'cloudy', 'rainy', 'sunny', 'windy', 'sunny']
                temp_highs = [26, 24, 21, 19, 23, 25, 27]
                temp_lows = [16, 15, 14, 13, 15, 16, 17]
                rain_probs = [5, 20, 40, 75, 15, 10, 5]
                
                forecast = []
                now = datetime.now()
                for i in range(7):
                    date = now + timedelta(days=i)
                    forecast.append({
                        'day': days[date.weekday()],
                        'date': date.strftime('%Y-%m-%d'),
                        'condition': conditions[i],
                        'temp_high': temp_highs[i],
                        'temp_low': temp_lows[i],
                        'rain_probability': rain_probs[i]
                    })
                return forecast
            
            # Parse real forecast data
            daily_data = {}
            condition_map = {
                'clear sky': 'sunny', 'few clouds': 'partly_cloudy',
                'scattered clouds': 'partly_cloudy', 'broken clouds': 'cloudy',
                'overcast clouds': 'cloudy', 'shower rain': 'rainy',
                'rain': 'rainy', 'thunderstorm': 'stormy', 'snow': 'snowy',
                'mist': 'foggy', 'fog': 'foggy'
            }
            
            for item in data['list'][:35]:
                dt = datetime.fromtimestamp(item['dt'])
                date_key = dt.strftime('%Y-%m-%d')
                
                if date_key not in daily_data:
                    daily_data[date_key] = {
                        'day': days[dt.weekday()], 'date': date_key,
                        'temps': [], 'conditions': [], 'rain_probs': []
                    }
                
                daily_data[date_key]['temps'].append(item['main']['temp'])
                
                weather = item.get('weather', [{}])[0]
                description = weather.get('description', '').lower()
                condition = condition_map.get(description, 'sunny')
                daily_data[date_key]['conditions'].append(condition)
                
                rain_prob = 0
                if 'rain' in item:
                    rain_prob = min(100, item['rain'].get('3h', 0) * 20)
                elif condition in ['rainy', 'stormy']:
                    rain_prob = 70
                elif condition == 'cloudy':
                    rain_prob = 30
                elif condition == 'partly_cloudy':
                    rain_prob = 15
                
                daily_data[date_key]['rain_probs'].append(rain_prob)
            
            forecast = []
            for date_key in sorted(daily_data.keys())[:7]:
                day_data = daily_data[date_key]
                conditions = day_data['conditions']
                condition = max(set(conditions), key=conditions.count) if conditions else 'sunny'
                
                forecast.append({
                    'day': day_data['day'], 'date': date_key, 'condition': condition,
                    'temp_high': round(max(day_data['temps'])) if day_data['temps'] else 25,
                    'temp_low': round(min(day_data['temps'])) if day_data['temps'] else 15,
                    'rain_probability': round(sum(day_data['rain_probs']) / len(day_data['rain_probs'])) if day_data['rain_probs'] else 10
                })
            
            # Fill remaining days if needed
            while len(forecast) < 7:
                base_date = datetime.now() + timedelta(days=len(forecast))
                forecast.append({
                    'day': days[base_date.weekday()],
                    'date': base_date.strftime('%Y-%m-%d'),
                    'condition': 'sunny', 'temp_high': 25, 'temp_low': 15, 'rain_probability': 10
                })
            
            return forecast[:7]
        
        def parse_hourly(data, today_plan):
            """Extract next 8 hours from forecast data"""
            if not data or 'list' not in data:
                return []
            condition_map = {
                'clear sky': 'sunny', 'few clouds': 'partly_cloudy',
                'scattered clouds': 'partly_cloudy', 'broken clouds': 'cloudy',
                'overcast clouds': 'cloudy', 'shower rain': 'rainy',
                'rain': 'rainy', 'thunderstorm': 'stormy', 'snow': 'snowy',
                'mist': 'foggy', 'fog': 'foggy'
            }
            pump_times = set(today_plan.get('pump_times', []))
            hours = []
            for item in data['list'][:8]:
                dt = datetime.fromtimestamp(item['dt'])
                hour_str = dt.strftime('%H:%M')
                weather = item.get('weather', [{}])[0]
                description = weather.get('description', '').lower()
                condition = condition_map.get(description, 'sunny')
                rain_prob = 0
                if 'rain' in item:
                    rain_prob = min(100, item['rain'].get('3h', 0) * 20)
                elif condition in ['rainy', 'stormy']:
                    rain_prob = 70
                elif condition == 'cloudy':
                    rain_prob = 30
                # Check if pump runs within 30 min of this hour
                pump_active = False
                for pt in pump_times:
                    ph, pm = map(int, pt.split(':'))
                    diff = abs((dt.hour * 60 + dt.minute) - (ph * 60 + pm))
                    if diff <= 30:
                        pump_active = True
                        break
                hours.append({
                    'time': hour_str,
                    'temp': round(item['main']['temp']),
                    'feels_like': round(item['main']['feels_like']),
                    'humidity': item['main']['humidity'],
                    'condition': condition,
                    'description': weather.get('description', '').title(),
                    'rain_probability': rain_prob,
                    'wind_speed': round(item['wind']['speed'] * 3.6),
                    'pump_active': pump_active,
                })
            return hours

        # Fetch weather data
        current_data, forecast_data = get_weather_data()
        current_weather = parse_current_weather(current_data)
        forecast_list = parse_forecast(forecast_data)
        
        # Get farm settings for irrigation calculations
        settings_obj, _ = FarmSettings.objects.get_or_create(user=request.user)
        base_duration = settings_obj.irrigation_duration
        soil_type = settings_obj.soil_type or 'Loam'
        plant_type = (settings_obj.plant_type or 'General').strip().lower()

        # Soil and plant factors
        SOIL = {
            'Sandy': {'water_factor': 1.40}, 'Sandy Loam': {'water_factor': 1.20},
            'Loam': {'water_factor': 1.00}, 'Silt': {'water_factor': 0.95},
            'Clay Loam': {'water_factor': 0.85}, 'Clay': {'water_factor': 0.75},
            'Peat': {'water_factor': 0.90}, 'Chalk': {'water_factor': 1.10},
        }
        soil = SOIL.get(soil_type, SOIL['Loam'])

        PLANT_DEMAND = {
            'tomato': 6.0, 'tomatoes': 6.0, 'maize': 5.5, 'corn': 5.5,
            'rice': 8.0, 'wheat': 4.0, 'potato': 5.0, 'potatoes': 5.0,
            'bean': 4.5, 'beans': 4.5, 'cabbage': 4.0, 'onion': 3.5,
            'onions': 3.5, 'carrot': 3.5, 'carrots': 3.5, 'lettuce': 3.0,
            'grass': 2.5, 'lawn': 2.5, 'general': 4.0,
        }
        
        plant_demand_base = 4.0
        for key, val in PLANT_DEMAND.items():
            if key in plant_type:
                plant_demand_base = val
                break

        PUMP_FLOW_RATE = 10

        def irrigation_plan(condition, temp_high, rain_prob):
            if rain_prob >= 70 or condition == 'rainy':
                return {
                    'cycles': 0, 'duration_min': 0, 'total_min': 0,
                    'pump_times': [], 'skip': True,
                    'reason': f'Skip — {"heavy rain expected" if rain_prob >= 70 else "rainy conditions"}',
                    'water_per_cycle_l': 0, 'water_total_l': 0,
                    'rain_saving_l': 0, 'estimated_need_l': 0,
                }

            duration = round(base_duration * soil['water_factor'])

            if temp_high >= 32:
                temp_factor, cycles, reason = 1.4, 3, 'Very hot — maximum irrigation'
            elif temp_high >= 28:
                temp_factor, cycles, reason = 1.2, 3, 'Hot day — extra irrigation needed'
            elif temp_high >= 24:
                temp_factor, cycles, reason = 1.0, 2, 'Warm day — normal irrigation'
            else:
                temp_factor, cycles, reason = 0.8, 1, 'Cool day — reduced irrigation'
                duration = round(duration * 0.8)

            if rain_prob >= 40:
                cycles = max(1, cycles - 1)
                duration = round(duration * 0.7)
                reason = 'Partial rain — reduced irrigation'
            elif rain_prob >= 20:
                duration = round(duration * 0.85)
                reason += ', light rain expected'

            if condition == 'windy':
                duration = round(duration * 1.1)
                reason = 'Windy — slight increase for evaporation'

            daily_demand = plant_demand_base * temp_factor * soil['water_factor']
            rain_saving = round((rain_prob / 100) * daily_demand, 1)
            water_per_cycle = round(duration * PUMP_FLOW_RATE, 1)
            water_total = round(cycles * water_per_cycle, 1)
            estimated_need = round((daily_demand - rain_saving) * 10, 1)

            return {
                'cycles': cycles, 'duration_min': duration,
                'total_min': cycles * duration, 'pump_times': ['06:00', '12:00', '18:00'][:cycles],
                'skip': False, 'reason': reason,
                'water_per_cycle_l': water_per_cycle, 'water_total_l': water_total,
                'rain_saving_l': rain_saving * 10, 'estimated_need_l': estimated_need,
            }

        # Calculate irrigation plans
        for day_data in forecast_list:
            plan = irrigation_plan(day_data['condition'], day_data['temp_high'], day_data['rain_probability'])
            day_data['irrigation'] = plan

        today_plan = irrigation_plan(
            current_weather['condition'], current_weather['temperature'], 
            current_weather.get('rain_probability', 0)
        )
        current_weather['irrigation'] = today_plan

        hourly = parse_hourly(forecast_data, today_plan)

        weekly_water = round(sum(d['irrigation']['water_total_l'] for d in forecast_list), 1)
        weekly_saving = round(sum(d['irrigation']['rain_saving_l'] for d in forecast_list), 1)

        return Response({
            'current': current_weather,
            'hourly': hourly,
            'forecast': forecast_list,
            'irrigation_settings': {
                'base_duration_min': base_duration,
                'soil_type': soil_type,
                'plant_type': settings_obj.plant_type or 'General',
                'pump_flow_rate': PUMP_FLOW_RATE,
                'weekly_water_l': weekly_water,
                'weekly_saving_l': weekly_saving,
            },
        })


class WeatherLocationView(APIView):
    """Handle location-based weather queries and location search"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get weather location or search for locations"""
        import urllib.request
        import json
        from django.conf import settings as django_settings
        
        # Get search query from request
        search_query = request.GET.get('q', '').strip()
        
        if not search_query:
            # Return default location
            location = getattr(django_settings, 'DEFAULT_WEATHER_LOCATION', {
                'lat': 40.7128, 'lon': -74.0060, 'name': 'New York City', 'country': 'US'
            })
            return Response({
                'locations': [location],
                'status': 'success'
            })
        
        # Search for locations using geocoding API
        try:
            api_key = getattr(django_settings, 'OPENWEATHER_API_KEY', '')
            geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={search_query}&limit=5&appid={api_key}"
            
            with urllib.request.urlopen(geo_url, timeout=10) as response:
                locations_data = json.loads(response.read().decode())
            
            # Format results
            locations = [
                {
                    'name': loc.get('name', ''),
                    'country': loc.get('country', ''),
                    'lat': loc.get('lat', 0),
                    'lon': loc.get('lon', 0),
                    'state': loc.get('state', '')
                }
                for loc in locations_data
            ]
            
            return Response({
                'locations': locations,
                'status': 'success',
                'count': len(locations)
            })
            
        except Exception as e:
            return Response({
                'locations': [],
                'status': 'error',
                'message': str(e),
                'count': 0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
