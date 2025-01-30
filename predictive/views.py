import time
import json
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import *
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from .models import *
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import datetime, timedelta
from asyncio import sleep
from django.db.models.functions import TruncHour
import os
from django.db.models import Max
from sklearn.ensemble import IsolationForest
from .LSTM import ModelBuilder, predictor, anamoly_limits
import shutil
import regex as re
from django.core.mail import send_mail

MODEL_MAIN_PATH = 'all_models/'
ANOMALY_VARIABLES = {}


######################################################### Start Django Funcation #######################################
#######################################################################################################################
def get_folders_in_directory(directory_path):
    return [f for f in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, f))]

def ajax_predictive_screen(request):
    """
    Handles POST requests to filter and return data based on the provided
    sensor name and date range (start_datetime and end_datetime).
    Returns a JSON response with filtered data for chart rendering.
    """
    if request.method == 'POST':
        sensor_name = request.POST.get('sensor_name')
        start_datetime = request.POST.get('start_datetime')
        end_datetime = request.POST.get('end_datetime')
        number_predications = request.POST.get('number_predications')
        additional_feature = request.POST.get('additional_feature') == 'true' 
        

        print(sensor_name, start_datetime, end_datetime,number_predications , additional_feature, 'number_predications')
       
        path = f'predictive.json'
        try:
            data = json.loads(open(path).read())

            return JsonResponse({
                "success": True,
                "data": data['data'],

            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})


def predictive_screen(request):
    """
    Retrieves all sensor data from SettingsElement and renders it in the
    'predictive_maintenance.html' template.
    """
    # sensors = SettingsElement.objects.all().order_by('-element_id')
    sensors = SettingsElement.objects.values('element_id', 'element_name').order_by('-element_id')
    return render(request, 'predictive_screen.html', {'sensors': sensors})

def model_evaluation(request):
    if request.method == 'POST':
        element_name = request.POST.get('element_name')
        graph_type = request.POST.get('loss_function')
        model = request.POST.get('model_path')

        path = f'{MODEL_MAIN_PATH}{element_name}/{model}/{element_name}_metrics.json'
        try:
            data = json.loads(open(path).read())
            return JsonResponse({
                'labels': [i for i in range(1, 1 + len(data[graph_type]))],
                'data': data[graph_type],
                'title': f'{graph_type} Graph'
            })
        except:
            return JsonResponse({
                'labels': [0],
                'data': [0],
                'title': f'No data to Load {graph_type} Graph'
            })


def training_screen(request):
    # sensors = SettingsElement.objects.values('element_id', 'element_name').order_by('-element_id')
    sensor_list = SettingsElement.objects.filter(prediction=True, active=True).values('element_id', 'element_name')

    return render(request, 'training_screen.html', {'sensors': sensor_list})


def get_models(request):
    try:
        element_id = request.GET.get('element_id')

        # Check if element_id is provided in the request
        if not element_id:
            return JsonResponse({'error': 'element_id is required'}, status=400)

        base_directory = os.getcwd()  # Gets the current working directory
        directory_path = os.path.join(base_directory, 'all_models', element_id)

        # Attempt to get the folders from the directory
        models_data = get_folders_in_directory(directory_path)

        # Return the models data as a JSON response
        return JsonResponse({'models': models_data})

    except FileNotFoundError:
        return JsonResponse({'error': f"Directory '{directory_path}' not found."}, status=404)

    except PermissionError:
        return JsonResponse({'error': f"Permission denied to access '{directory_path}'."}, status=403)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def ajax_success_view1(request):
    """
    Handles POST requests to filter and return data based on the provided
    sensor name and date range (start_datetime and end_datetime).
    Returns a JSON response with filtered data for chart rendering.
    """
    if request.method == 'POST':
        sensor_name = request.POST.get('sensor_name')
        start_datetime = request.POST.get('start_datetime')
        end_datetime = request.POST.get('end_datetime')

        try:

            data = [

                {"year": 2000, "value": 52},
                {"year": 2001, "value": 67},
                {"year": 2002, "value": 34},
                {"year": 2003, "value": 49},
                {"year": 2004, "value": 27},
                {"year": 2005, "value": 58},
                {"year": 2006, "value": 75},
                {"year": 2007, "value": 42},
                {"year": 2008, "value": 61},
                {"year": 2009, "value": 69},
                {"year": 2010, "value": 28},
                {"year": 2011, "value": 56},
                {"year": 2012, "value": 72},
                {"year": 2013, "value": 30},
                {"year": 2014, "value": 66},
                {"year": 2015, "value": 33},
                {"year": 2016, "value": 70},
                {"year": 2017, "value": 45},
                {"year": 2018, "value": 67},
                {"year": 2019, "value": 25},
                {"year": 2020, "value": 10},
                {"year": 2021, "value": 45},
                {"year": 2022, "value": 58},
                {"year": 2023, "value": 39},
                {"year": 2024, "value": 68},
                {"year": 2025, "value": 63},
                {"year": 2026, "value": 27},
                {"year": 2027, "value": 79},
                {"year": 2028, "value": 53},
                {"year": 2029, "value": 48},
                {"year": 2030, "value": 32},
                {"year": 2031, "value": 60},
                {"year": 2032, "value": 51},
                {"year": 2033, "value": 64},
                {"year": 2034, "value": 71},
                {"year": 2035, "value": 26},
                {"year": 2036, "value": 55},
                {"year": 2037, "value": 70},
                {"year": 2038, "value": 36},
                {"year": 2039, "value": 65},
                {"year": 2040, "value": 53},
                {"year": 2041, "value": 24},
                {"year": 2042, "value": 75},
                {"year": 2043, "value": 56},
                {"year": 2044, "value": 47},
                {"year": 2045, "value": 64},
                {"year": 2046, "value": 33},
                {"year": 2047, "value": 58},
                {"year": 2048, "value": 25},
                {"year": 2049, "value": 66},
                {"year": 2050, "value": 59},
                {"year": 2051, "value": 31},
                {"year": 2052, "value": 48},
                {"year": 2053, "value": 54},
                {"year": 2054, "value": 50},
                {"year": 2055, "value": 41},
                {"year": 2056, "value": 63},
                {"year": 2057, "value": 44},
                {"year": 2058, "value": 55},
                {"year": 2059, "value": 32},
                {"year": 2060, "value": 69},
                {"year": 2061, "value": 75},
                {"year": 2062, "value": 33},
                {"year": 2063, "value": 64},
                {"year": 2064, "value": 68},
                {"year": 2065, "value": 49},
                {"year": 2066, "value": 42},
                {"year": 2067, "value": 38},
                {"year": 2068, "value": 30},
                {"year": 2069, "value": 52},
                {"year": 2070, "value": 46},
                {"year": 2071, "value": 39},
                {"year": 2072, "value": 61},
                {"year": 2073, "value": 29},
                {"year": 2074, "value": 63},
                {"year": 2075, "value": 55},
                {"year": 2076, "value": 71},
                {"year": 2077, "value": 73},
                {"year": 2078, "value": 62},
                {"year": 2079, "value": 45},
                {"year": 2080, "value": 40},
                {"year": 2081, "value": 50},
                {"year": 2082, "value": 47},
                {"year": 2083, "value": 62},
                {"year": 2084, "value": 61},
                {"year": 2085, "value": 63},
                {"year": 2086, "value": 35},
                {"year": 2087, "value": 48},
                {"year": 2088, "value": 28},
                {"year": 2089, "value": 44},
                {"year": 2090, "value": 71},
                {"year": 2091, "value": 35},
                {"year": 2092, "value": 43},
                {"year": 2093, "value": 29},
                {"year": 2094, "value": 69},
                {"year": 2095, "value": 30},
                {"year": 2096, "value": 60},
                {"year": 2097, "value": 78},
                {"year": 2098, "value": 38},
                {"year": 2099, "value": 52},
                {"year": 2100, "value": 27},
                {"year": 2101, "value": 45},
                {"year": 2102, "value": 48},
                {"year": 2103, "value": 39},
                {"year": 2104, "value": 57},
                {"year": 2105, "value": 64},
                {"year": 2106, "value": 33},
                {"year": 2107, "value": 73},
                {"year": 2108, "value": 46},
                {"year": 2109, "value": 56},
                {"year": 2110, "value": 62},
                {"year": 2111, "value": 71},
                {"year": 2112, "value": 77},
                {"year": 2113, "value": 50},
                {"year": 2114, "value": 69},
                {"year": 2115, "value": 65},
                {"year": 2116, "value": 28},
                {"year": 2117, "value": 46},
                {"year": 2118, "value": 56},
                {"year": 2119, "value": 67},
                {"year": 2120, "value": 73},
                {"year": 2121, "value": 41},
                {"year": 2122, "value": 59},
                {"year": 2123, "value": 75},
                {"year": 2124, "value": 31},
                {"year": 2125, "value": 39},
                {"year": 2126, "value": 62},
                {"year": 2127, "value": 42},
                {"year": 2128, "value": 69},
                {"year": 2129, "value": 51},
                {"year": 2130, "value": 47},
                {"year": 2131, "value": 58},
                {"year": 2132, "value": 44},
                {"year": 2133, "value": 77},
                {"year": 2134, "value": 63},
                {"year": 2135, "value": 60},
                {"year": 2136, "value": 39},
                {"year": 2137, "value": 53},
                {"year": 2138, "value": 70},
                {"year": 2139, "value": 25},
                {"year": 2140, "value": 68},
                {"year": 2141, "value": 72},
                {"year": 2142, "value": 44},
                {"year": 2143, "value": 38},
                {"year": 2144, "value": 56},
                {"year": 2145, "value": 73},
                {"year": 2146, "value": 51},
                {"year": 2147, "value": 45},
                {"year": 2148, "value": 28},
                {"year": 2149, "value": 70},
                {"year": 2150, "value": 65},
                {"year": 2151, "value": 59},
                {"year": 2152, "value": 56},
                {"year": 2153, "value": 64},
                {"year": 2154, "value": 35},
                {"year": 2155, "value": 51},
                {"year": 2156, "value": 46},
                {"year": 2157, "value": 54},
                {"year": 2158, "value": 32},
                {"year": 2159, "value": 57},
                {"year": 2160, "value": 64},
                {"year": 2161, "value": 59},
                {"year": 2162, "value": 43},
                {"year": 2163, "value": 67},
                {"year": 2164, "value": 62},
                {"year": 2165, "value": 40},
                {"year": 2166, "value": 77},
                {"year": 2167, "value": 54},
                {"year": 2168, "value": 66},
                {"year": 2169, "value": 34},
                {"year": 2170, "value": 50},
                {"year": 2171, "value": 55},
                {"year": 2172, "value": 66},
                {"year": 2173, "value": 42},
                {"year": 2174, "value": 71},
                {"year": 2175, "value": 55},
                {"year": 2176, "value": 47},
                {"year": 2177, "value": 58},
                {"year": 2178, "value": 51},
                {"year": 2179, "value": 40},
                {"year": 2180, "value": 64},
                {"year": 2181, "value": 72},
                {"year": 2182, "value": 37},
                {"year": 2183, "value": 33},
                {"year": 2184, "value": 62},
                {"year": 2185, "value": 59},
                {"year": 2186, "value": 73},
                {"year": 2187, "value": 65},
                {"year": 2188, "value": 54},
                {"year": 2189, "value": 40},
                {"year": 2190, "value": 72},
                {"year": 2191, "value": 63},
                {"year": 2192, "value": 44},
                {"year": 2193, "value": 58},
                {"year": 2194, "value": 75},
                {"year": 2195, "value": 52},
                {"year": 2196, "value": 39},
                {"year": 2197, "value": 43},
                {"year": 2198, "value": 69},
                {"year": 2199, "value": 30},
                {"year": 2200, "value": 63}

            ]
            # Filter data by the provided year range
            # Return filtered data in JSON response
            return JsonResponse({
                "success": True,
                "data": {"chartData": data}
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})


def start_training(request):
    if request.method == 'POST':
        try:
            no_of_epochs = request.POST.get('No_of_Epochs')
            no_of_steps = request.POST.get('No_of_steps')
            anomaly_percentage = request.POST.get('anomaly_percentage')
            time.sleep(30)
            return JsonResponse({'success': True, 'result': 'Training Complete'})

        except Exception as e:
            # If any error occurs, return an error response
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def model_analysis(request):
    sensors = SettingsElement.objects.all().order_by('-element_id')

    return render(request, 'model_analysis.html', {'sensors': sensors})


#######################################################################################################################
#################################################### end ##############################################################

async def my_async_view(request):
    await sleep(5)  # Simulate a time-consuming operation
    return JsonResponse({"message": "This is an async response!"})


@api_view(['GET'])
def is_server_live(requests):
    return JsonResponse({"status": "True"}, safe=False)


@api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
def datalog(request):
    if request.method == 'POST':
        datalog_serializer = SensorDataLogSerializer(data=request.data)
        if datalog_serializer.is_valid():
            datalog_serializer.save()
            return Response({"message": "data saved successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(datalog_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
def get_pred_sensor_list(request):
    sensor_list = SettingsElement.objects.filter(prediction=True, active=True).values('element_id' , 'model_path' , 'org_id')
    sensor = list(sensor_list)
    return JsonResponse(sensor, safe=False)


@api_view(['POST'])
def get_sensor_data(request):
    try:
        MANDATORY_FIELD = ['element_id', 'count', 'end_date']
        sensor_params = request.data

        if set(MANDATORY_FIELD).issubset(set(sensor_params)):
            if sensor_params['end_date'] == '': sensor_params['end_date'] = datetime.now().date()
            start_date = sensor_params['end_date'] - timedelta(days=int(sensor_params['count']))

            sensor_data = SensorDataLog.objects.filter(element_id=sensor_params['element_id'],
                                                       timestamp__range=['2024-12-28 00:00:00.00',
                                                                         '2024-12-28 23:00:00.00'])  # [sensor_params['end_date'] , start_date])
            return JsonResponse(list(sensor_data.values()), safe=False)
        else:
            return JsonResponse({'message': f'some parameters in {MANDATORY_FIELD} are missing'}, safe=False)
    except Exception as e:
        return JsonResponse({'error': f'{e}'}, safe=False)


@api_view(['POST'])
def train_model(requests):
    if requests.method == 'POST':
        train_params = {
            'element_id': requests.POST.get('sensor_name'),
            'start_time': requests.POST.get('start_datetime'),
            'end_time': requests.POST.get('end_datetime'),
            'epochs': int(requests.POST.get('No_of_Epochs')),
            'sequence_length': int(requests.POST.get('No_of_steps')),
            'anomaly_percentage': requests.POST.get('anomaly_percentage')
        }

        print(train_params)

        min_data_to_train = 80
        element_list = SettingsElement.objects.filter(prediction='True').values('element_id')
        if train_params['element_id'] in [element['element_id'] for element in list(element_list)]:
            hour_labeled = SensorDataLog.objects.filter(
                timestamp__range=[train_params['start_time'], train_params['end_time']],
                element_id=train_params['element_id']).annotate(
                hour=TruncHour('timestamp')).values('hour').annotate(hourly_max=Max('max')).values('hour',
                                                                                                   'hourly_max')
            train_data = [float(object['hourly_max']) for object in hour_labeled]
            if len(train_data) >= min_data_to_train:
                modeling_start_time = datetime.now()
                model_path = f"{MODEL_MAIN_PATH}{train_params['element_id']}"
                try:
                    # anamoly limits
                    anamoly_results = anamoly_limits(train_data)
                    if not anamoly_results['status']: return JsonResponse(
                        {"success": "False", "message": anamoly_results['error']}, safe=False)

                    # model builder
                    model = ModelBuilder(train_params['element_id'], model_path, train_params['epochs'],
                                         train_params['sequence_length'])
                    res, msg = model.build_model(train_data)

                    if res:
                        ModelLog(start_time=str(modeling_start_time), model_path=msg, model_created='True',
                                 remarks='Successfully created', log_time=str(datetime.now())).save()
                        SettingsElement.objects.filter(element_id=train_params['element_id']).update(model_path=msg,
                                                                                                     upper_anamoly_limit=
                                                                                                     anamoly_results[
                                                                                                         'upper_limit'],
                                                                                                     lower_anamoly_limit=
                                                                                                     anamoly_results[
                                                                                                         'lower_limit'])
                        return JsonResponse({"success": "True", "message": f"Model Created at {msg}"}, safe=False)
                    else:
                        ModelLog(start_time=str(modeling_start_time), model_path=msg, model_created='True',
                                 remarks=msg, log_time=str(datetime.now())).save()
                        return JsonResponse({"success": "False", "message": f"{msg}"}, safe=False)
                except Exception as e:
                    ModelLog(start_time=str(modeling_start_time), model_path=model_path, model_created='False',
                             remarks=e, log_time=str(datetime.now())).save()
                    return JsonResponse({"success": "False", "message": e}, safe=False)
            else:
                return JsonResponse({"message": f"Need min of {min_data_to_train} datas got {len(train_data)}"},
                                    safe=False)
        else:
            return JsonResponse({"message": f"check element id in settings with prediction enabled"}, safe=False)


@receiver(post_save, sender=SensorDataLog)
def anomaly_check(sender, instance, created, **kwargs):
    print(instance.element_id, instance.max)
    limits = SettingsElement.objects.filter(element_id=instance.element_id).values('element_id', 'element_name',
                                                                                   'upper_anamoly_limit',
                                                                                   'lower_anamoly_limit')

    if not limits[0]['upper_anamoly_limit'] == 'model not created':
        if not float(limits[0]['lower_anamoly_limit']) <= float(instance.max) <= float(
                limits[0]['upper_anamoly_limit']):
            print(
                f"Alert - Anomaly ---- HL {limits[0]['upper_anamoly_limit']} , LL {limits[0]['lower_anamoly_limit']} , Value {instance.max}")
            data = {
                'sensor_name': limits[0]['element_name'],
                'ranges': f"{limits[0]['upper_anamoly_limit']} - {limits[0]['upper_anamoly_limit']}",
                'actual': instance.max
            }
            print(alert_anamoly([ 'faj@titan.co.in', 'tamilmozhi.mj@titan.co.in'], data))


@receiver(post_save, sender=SettingsElement)
def create_model_folder(sender, instance, created, **kwargs):
    if created:
        os.mkdir(MODEL_MAIN_PATH + str(instance.element_id))


@receiver(post_delete, sender=SettingsElement)
def delete_model_folder(sender, instance, **kwargs):
    try:
        shutil.rmtree(MODEL_MAIN_PATH + str(instance.element_id))
    except:
        print(f"Error on deleteing model path {MODEL_MAIN_PATH + str(instance.element_id)}")


@api_view(['POST'])
def datalog_sensor_list(request):
    res = {}
    sensor_list = SettingsElement.objects.filter(active=True)
    sensor = list(sensor_list.values('element_id', 'tag', 'org_id', 'server_ip', 'rec_train_data'))

    for i in sensor:
        try:
            res[i['server_ip']]
        except:
            res[i['server_ip']] = {}
        res[i['server_ip']][i['element_id']] = [i['tag'], i['org_id'], i['rec_train_data']]

    return JsonResponse(res, safe=False)


@api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
def error_log(request):
    if request.method == 'POST':
        error_log_serializer = ErrorLogSerializer(data=request.data)
        if error_log_serializer.is_valid():
            error_log_serializer.save()
            return Response({"message": "error logged successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(error_log_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def alert_anamoly(recipient_list, table_data):
    try:
        subject = "Alert-Anamoly"
        message = "This is a test email from Django."
        from_email = "tealappmailer1@titan.co.in"
        # recipient_list = ["baswasanjay19@gmail.com"]  # Replace with the recipient's email
        #
        # table_rows = ''
        #
        # for id, row_data in table_data:
        #     table_rows += f'''
        #
        #     '''

        html_message = f'''
        <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Welcome Email</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
      <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #dddddd;">
        <div style="background-color:  #FFFF00; color: black; padding: 20px; text-align: center;">
          <h1 style="margin: 0;">Alert for Anamoly in Injector Line!</h1>
        </div>
        <div style="padding: 20px;">
          <p>Following are the list of anomalies found 2025-Jan-05 4:26 PM</p>
          <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <thead>
              <tr>
                <th style="border: 1px solid #dddddd; padding: 8px; background-color: #f4f4f4;">Sno</th>
                <th style="border: 1px solid #dddddd; padding: 8px; background-color: #f4f4f4;">Sensor</th>
                <th style="border: 1px solid #dddddd; padding: 8px; background-color: #f4f4f4;">Limits -°C</th>
		        <th style="border: 1px solid #dddddd; padding: 8px; background-color: #f4f4f4;">Actual Value</th>
              </tr>
            </thead>
            <tbody>
               <tr>
                    <td style="border: 1px solid #dddddd; padding: 4px;">1</td>
                    <td style="border: 1px solid #dddddd; padding: 8px;">{table_data['sensor_name']}</td>
                    <td style="border: 1px solid #dddddd; padding: 8px;">{table_data['ranges']}</td>
                    <td style="border: 1px solid #dddddd; padding: 8px;">{table_data['actual']}</td>
                  </tr>
            </tbody>
          </table>
          <p style="margin-top: 20px;">This is test version of email</p>
        </div>
        <div style="background-color: #f4f4f4; color: #777; text-align: center; padding: 10px;">
          <p style="margin: 0;">© 2025 TEAL. All rights reserved.</p>
        </div>
      </div>
    </body>
    </html>
        '''

        send_mail(subject, message, from_email, recipient_list, html_message=html_message)

        return JsonResponse({"status": 'sent email'}, safe=False)
    except Exception as E:
        return JsonResponse({"status": E}, safe=False)


@api_view(['POST'])
def test_function(requests):
    try:
        subject = "Test Email"
        message = "This is a test email from Django."
        from_email = "tealappmailer1@titan.co.in"
        recipient_list = ["baswasanjay19@gmail.com"]  # Replace with the recipient's email

        html_message = f'''
        <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Welcome Email</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
      <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #dddddd;">
        <div style="background-color:  #FFFF00; color: black; padding: 20px; text-align: center;">
          <h1 style="margin: 0;">Alert for Anamoly in Injector Line!</h1>
        </div>
        <div style="padding: 20px;">
          <p>Following are the list of anomiles found 2025-Jan-05 4:26 PM</p>
          <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <thead>
              <tr>
                <th style="border: 1px solid #dddddd; padding: 8px; background-color: #f4f4f4;">Sno</th>
                <th style="border: 1px solid #dddddd; padding: 8px; background-color: #f4f4f4;">Sensor</th>
                <th style="border: 1px solid #dddddd; padding: 8px; background-color: #f4f4f4;">Limits -°C</th>
		<th style="border: 1px solid #dddddd; padding: 8px; background-color: #f4f4f4;">Actual Value</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style="border: 1px solid #dddddd; padding: 4px;">1</td>
                <td style="border: 1px solid #dddddd; padding: 8px;">Temperature</td>
                <td style="border: 1px solid #dddddd; padding: 8px;">30 - 35</td>
		<td style="border: 1px solid #dddddd; padding: 8px;">36</td>
              </tr>
            </tbody>
          </table>
          <p style="margin-top: 20px;">This is test version of email</p>
        </div>
        <div style="background-color: #f4f4f4; color: #777; text-align: center; padding: 10px;">
          <p style="margin: 0;">© 2025 TEAL. All rights reserved.</p>
        </div>
      </div>
    </body>
    </html>
        '''

        send_mail(subject, message, from_email, recipient_list, html_message=html_message)

        return JsonResponse({"status": 'sent email'}, safe=False)
    except Exception as E:
        return JsonResponse({"status": E}, safe=False)

@api_view(['POST'])
def prediction(requests):
    params = requests.data
    element_list = SettingsElement.objects.filter(prediction='True').values('element_id')
    if params['element_id'] in [element['element_id'] for element in list(element_list)]:
        model_data = SettingsElement.objects.filter(element_id=params['element_id']).values('model_path')
        for file in os.listdir(model_data[0]['model_path']):
            if file.find('.h5') != -1:
                path = model_data[0]['model_path']
                match = re.search(r'-(\d+)\.', file)
                sequence_length = int(match.group(1))
                if match:

                    inputs = SensorDataLog.objects.filter(element_id = params['element_id']).values('timestamp' , 'max') .order_by('-timestamp')[:sequence_length*1000]

                    return JsonResponse(list(inputs), safe=False)



                    res, msg = predictor(requests.data['data'], path,sequence_length ,
                                         no_of_pred=int(requests.data['no_of_prediction']), result=True)
                    if res:
                        return JsonResponse({"prediction": msg}, safe=False)
                    else:
                        return JsonResponse({'message': msg}, safe=False)
                else:
                    return JsonResponse({'message': "Couldn't find the seq len in  model name"}, safe=False)

        return JsonResponse({"message": 'Model not found in the given path'}, safe=False)
    return JsonResponse({"msg": "element is not in settings"}, safe=False)


@api_view(['POST'])
def predict_data(requests):
    MANDATORY_FIELD = ['element_id', 'data', 'no_of_prediction']
    params = requests.data
    if set(MANDATORY_FIELD).issubset(set(params)):
        element_list = SettingsElement.objects.filter(prediction='True').values('element_id')
        if params['element_id'] in [element['element_id'] for element in list(element_list)]:
            model_data = SettingsElement.objects.filter(element_id=params['element_id']).values('model_path')
            for file in os.listdir(model_data[0]['model_path']):
                if file.find('.h5') != -1:
                    path = model_data[0]['model_path']
                    match = re.search(r'-(\d+)\.', file)
                    if match:
                        res, msg = predictor(requests.data['data'], path, int(match.group(1)),
                                             no_of_pred=int(requests.data['no_of_prediction']), result=True)
                        if res:
                            return JsonResponse({"prediction": msg}, safe=False)
                        else:
                            return JsonResponse({'message': msg}, safe=False)
                    else:
                        return JsonResponse({'message': "Couldn't find the seq len in  model name"}, safe=False)

            return JsonResponse({"message": 'Model not found in the given path'}, safe=False)
        return JsonResponse({"msg": "element is not in settings"}, safe=False)
    return JsonResponse({"msg": f"Missing Mandatory '{MANDATORY_FIELD}' fields"}, safe=False)


@api_view(['POST'])
def element_raw_data_hourly_api(request):
    if request.method == 'POST':
        print("elemenmt raw atable")
        element_id = request.POST.get('sensor_name')
        start_time = request.POST.get('start_datetime')
        end_time = request.POST.get('end_datetime')
        print(f'{element_id}-{start_time}-{end_time}')
        hour_labeled = SensorDataLog.objects.filter(timestamp__range=[start_time, end_time],
                                                    element_id=element_id).annotate(
            year=TruncHour('timestamp')).values('year').annotate(value=Max('max')).values('year', 'value')

        res = {
            "success": True,
            "data": {"chartData": list(hour_labeled)}
        }

        return JsonResponse(res, safe=False)


@api_view(['POST'])
def element_raw_data_hourly(request):
    if request.method == 'POST':
        data = request.data

        hour_labeled = SensorDataLog.objects.filter(timestamp__range=[data['start_time'], data['end_time']],
                                                    element_id=data['element_id']).annotate(
            year=TruncHour('timestamp')).values('year').annotate(value=Max('max')).values('year', 'value')

        res = {
            "success": True,
            "data": {"chartData": list(hour_labeled)}
        }

        return JsonResponse(res, safe=False)


def delete_all_records(request, sensor_id):
    try:
        SensorDataLog.objects.filter(element_id=sensor_id).delete()
        return JsonResponse({"status": "deleteed"}, safe=False)
    except Exception as e:
        return JsonResponse({"status": e}, safe=False)
