import time, traceback
import json, math
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
from django.db.models import Max, F
from sklearn.ensemble import IsolationForest
from .LSTM import ModelBuilder, predictor, anamoly_limits
import shutil
import regex as re
from django.core.mail import send_mail
from collections import defaultdict

MODEL_MAIN_PATH = 'all_models/'
ANOMALY_VARIABLES = {}
HOUR_MODE = False


def get_folders_in_directory(directory_path):
    return [f for f in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, f))]



@api_view(['POST'])
def run_predictions(request):
    is_api_call = False
    if request.method == 'POST':
        params = {
            'element_id': request.POST.get('sensor_name'),
            'no_of_prediction': request.POST.get('number_predications'),
            'with_actual': request.POST.get('additionalFeature'),
        }

        if params['element_id'] is None:
            is_api_call = True
            params = {
                'element_id': request.data['sensor_name'],
                'no_of_prediction': request.data['number_predications'],
                'with_actual': request.data['with_actual'],
            }

        print("params", params, is_api_call)

        model_data = SettingsElement.objects.filter(element_id=params['element_id']).values('model_path')
        for file in os.listdir(model_data[0]['model_path']):
            if file.find('.h5') != -1:
                path = model_data[0]['model_path']
                match = re.search(r'-(\d+)\.', file)
                sequence_length = int(match.group(1))
                if match:
                    params['sequence_length'] = sequence_length
                    hour_labeled = orm_sensor_data(params, 'predict')
                    inputs = [float(object['value']) for object in hour_labeled]
                    time_stamps = [str(object['time']) for object in hour_labeled]

                    inputs = inputs[::-1]
                    time_stamps = time_stamps[::-1]


                    # !!
                    if params['with_actual'] == 'true':
                        print("with actual data is True")
                        input_set = inputs[:-int(params['no_of_prediction'])][-sequence_length:]
                        pred_time_stamps = time_stamps[-int(params['no_of_prediction']):]
                        print(f"**no_of_prediction: {params['no_of_prediction']} ** sequence_length: {sequence_length}")
                        print("***************  INPUTS  *******************************")
                        print(inputs)
                        print("***************** TIME_STAMP ********************")
                        print(time_stamps)
                        print("***************  INPUT_SET  *******************************")
                        print(input_set)
                        print("****************** PRED TIME_STAMP ******************")
                        print(pred_time_stamps)

                        res, msg = predictor(input_set, path, sequence_length,
                                             no_of_pred=int(params['no_of_prediction']), result=True)
                        predictions = []
                        for id, pred in enumerate(msg):
                            predictions.append({'time': pred_time_stamps[id], 'value': pred})

                        # predictions.insert(0, list(hour_labeled)[int(params['no_of_prediction'])])
                        print(predictions, "----------------------------pred")
                        if res:
                            final_res = {
                                "success": True,
                                "data": {
                                    "actual_data": list(hour_labeled)[::-1],
                                    "predictions": predictions,
                                    "is_actual": params['with_actual']
                                }
                            }
                            return JsonResponse(final_res, safe=False)
                        else:
                            return JsonResponse({'message': msg}, safe=False)

                    else:  # only predicition
                        print("with actual data is False")
                        input_set = inputs[-sequence_length:]
                        timestamp_set = time_stamps[-sequence_length:]

                        res, msg = predictor(input_set, path, sequence_length,
                                             no_of_pred=int(params['no_of_prediction']), result=True)

                        predictions = [{'time': 'hour' + str(id + 1), 'value': i} for id, i in enumerate(msg)]

                        predictions.insert(0, list(hour_labeled)[0])

                        if res:
                            final_res = {
                                "success": True,
                                "data": {
                                    "actual_data": list(hour_labeled)[::-1],
                                    "predictions": predictions},
                                "is_actual": params['with_actual']
                            }
                            return JsonResponse(final_res, safe=False)
                        else:
                            return JsonResponse({'message': msg}, safe=False)

                else:
                    return JsonResponse({'message': "Couldn't find the seq len in  model name"}, safe=False)

            return JsonResponse({"message": 'Model not found in the given path'}, safe=False)



def two_point_ref_scaling():
    pass


@api_view(['POST'])
def run_predictions1(request):
    is_api_call = False
    if request.method == 'POST':
        params = {
            'element_id': request.POST.get('sensor_name'),
            'no_of_prediction': request.POST.get('number_predications'),
            'with_actual': request.POST.get('additionalFeature'),
        }

        if params['element_id'] is None:
            is_api_call = True
            params = {
                'element_id': request.data['sensor_name'],
                'no_of_prediction': request.data['number_predications'],
                'with_actual': request.data['with_actual'],
            }

        print("params", params, is_api_call)

        model_data = SettingsElement.objects.filter(element_id=params['element_id']).values('model_path')
        for file in os.listdir(model_data[0]['model_path']):
            if file.find('.h5') != -1:
                path = model_data[0]['model_path']
                match = re.search(r'-(\d+)\.', file)
                sequence_length = int(match.group(1))
                if match:
                    params['sequence_length'] = sequence_length
                    hour_labeled = orm_sensor_data(params, 'predict')
                    inputs = [float(object['value']) for object in hour_labeled]
                    time_stamps = [str(object['time']) for object in hour_labeled]
                    # !!
                    if params['with_actual'] == 'true':
                        print("with actual data is True")
                        input_set = inputs[:-int(params['no_of_prediction'])][-sequence_length:]
                        pred_time_stamps = time_stamps[-int(params['no_of_prediction']):]
                        print(f"**no_of_prediction: {params['no_of_prediction']} ** sequence_length: {sequence_length}")
                        print("***************  INPUTS  *******************************")
                        print(inputs)
                        print("***************** TIME_STAMP ********************")
                        print(time_stamps)
                        print("***************  INPUT_SET  *******************************")
                        print(input_set)
                        print("****************** PRED TIME_STAMP ******************")
                        print(pred_time_stamps)

                        res, msg = predictor(input_set, path, sequence_length,
                                             no_of_pred=int(params['no_of_prediction']), result=True)
                        predictions = []
                        for id, pred in enumerate(msg):
                            predictions.append({'time': pred_time_stamps[id], 'value': pred})

                        # predictions.insert(0, list(hour_labeled)[int(params['no_of_prediction'])])
                        print(predictions, "----------------------------pred")
                        if res:
                            final_res = {
                                "success": True,
                                "data": {
                                    "actual_data": list(hour_labeled)[::-1],
                                    "predictions": predictions,
                                    "is_actual": params['with_actual']
                                }
                            }
                            return JsonResponse(final_res, safe=False)
                        else:
                            return JsonResponse({'message': msg}, safe=False)

                    else:  # only predicition
                        print("with actual data is False")
                        input_set = inputs[-sequence_length:]
                        timestamp_set = time_stamps[-sequence_length:]

                        res, msg = predictor(input_set, path, sequence_length,
                                             no_of_pred=int(params['no_of_prediction']), result=True)

                        predictions = [{'time': 'hour' + str(id + 1), 'value': i} for id, i in enumerate(msg)]

                        predictions.insert(0, list(hour_labeled)[0])

                        if res:
                            final_res = {
                                "success": True,
                                "data": {
                                    "actual_data": list(hour_labeled)[::-1],
                                    "predictions": predictions},
                                "is_actual": params['with_actual']
                            }
                            return JsonResponse(final_res, safe=False)
                        else:
                            return JsonResponse({'message': msg}, safe=False)

                else:
                    return JsonResponse({'message': "Couldn't find the seq len in  model name"}, safe=False)

            return JsonResponse({"message": 'Model not found in the given path'}, safe=False)


def ajax_predictive_screen1(request):
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
        additional_feature = request.POST.get('additionalFeature') == 'true'

        print(sensor_name, start_datetime, end_datetime, number_predications, additional_feature, 'number_predications')

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
    sensors = SettingsElement.objects.filter(prediction=True).values('element_id', 'element_name')

    return render(request, 'predictive_screen.html', {'sensors': sensors})


def model_evaluation(request):
    if request.method == 'POST':
        element_name = request.POST.get('element_name')
        graph_type = request.POST.get('loss_function')
        model = request.POST.get('model_path')

        path = f'{MODEL_MAIN_PATH}{element_name}/{model}/{element_name}_metrics.json'
        try:
            data = json.loads(open(path).read())
            graph_data = data[graph_type][20:]
            return JsonResponse({
                'labels': [i for i in range(1, 1 + len(graph_data))],
                'data': graph_data,
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
    sensor_list = SettingsElement.objects.filter(prediction=True).values('element_id', 'element_name')
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


def model_analysis(request):
    sensors = SettingsElement.objects.filter(prediction=True).order_by('-element_id')

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
    sensor_list = SettingsElement.objects.filter(prediction=True).values('element_id', 'model_path',

                                                                       'org_id', 'upper_anamoly_limit',
                                                                         'lower_anamoly_limit')

    res = defaultdict(list)
    for element in list(sensor_list):
        res[element['org_id']].append(element)

    return JsonResponse(res, safe=False)


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

        min_data_to_train = 49

        q1 = orm_sensor_data(train_params, 'train')
        train_data = [float(object['value']) for object in q1]
        print(train_data)
        if len(train_data) >= min_data_to_train:
            modeling_start_time = datetime.now()
            model_path = f"{MODEL_MAIN_PATH}{train_params['element_id']}"
            try:
                anamoly_results = anamoly_limits(train_data , train_params['anomaly_percentage'])
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
                                                                                                     'lower_limit'],
                                                                                                 aggregation_type='max',
                                                                                                 prediction=True)
                    return JsonResponse({"success": "True", "message": f"Model Created at {msg}"}, safe=False)
                else:
                    ModelLog(start_time=str(modeling_start_time), model_path=msg, model_created='False',
                             remarks=msg, log_time=str(datetime.now())).save()
                    return JsonResponse({"success": "False", "message": f"{msg}"}, safe=False)
            except Exception as e:
                ModelLog(start_time=str(modeling_start_time), model_path=model_path, model_created='False',
                         remarks=e, log_time=str(datetime.now())).save()
                return JsonResponse({"success": "False", "message": e}, safe=False)
        else:
            return JsonResponse({"message": f"Need min of {min_data_to_train} datas got {len(train_data)}"},
                                safe=False)


def anomaly_check(sender, instance, created, **kwargs):
    print(instance.element_id, instance.max)
    limits = SettingsElement.objects.filter(element_id=instance.element_id).values('element_id', 'element_name',
                                                                                   'upper_anamoly_limit',
                                                                                   'lower_anamoly_limit', 'prediction')
    try:
        if not limits[0]['upper_anamoly_limit'] == 'model not created':
            if not float(limits[0]['lower_anamoly_limit']) <= float(instance.max) <= float(
                    limits[0]['upper_anamoly_limit']):
                print(
                    f"Alert - Anomaly ---- HL {limits[0]['upper_anamoly_limit']} , LL {limits[0]['lower_anamoly_limit']} , Value {instance.max}")
                data = {
                    'time_stamp': '',
                    'sensor_name': limits[0]['element_name'],
                    'ranges': f"{limits[0]['upper_anamoly_limit']} - {limits[0]['lower_anamoly_limit']}",
                    'actual': instance.max
                }

                print(limits[0]['prediction'], "check thus")
                # print(alert_anamoly(['faj@titan.co.in', 'akashadi@titan.co.in', 'bsh.wed@delphitvs.com'], data))
    except Exception as e:
        pass


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
        html_message = f'''
        <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Alert Email</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
      <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #dddddd;">
        <div style="background-color:  #FFFF00; color: black; padding: 20px; text-align: center;">
          <h1 style="margin: 0;">Alert | Anamoly in Injector Line!</h1>
        </div>
        <div style="padding: 20px;">
          <p>Following are the list of anomalies found {datetime.now()}</p>
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
def element_raw_data(request):
    if request.method == 'POST':
        data = {
            'element_id': request.POST.get('sensor_name'),
            'start_time': request.POST.get('start_datetime'),
            'end_time': request.POST.get('end_datetime')
        }
        element_data = orm_sensor_data(data, 'train')
        res = {
            "success": True,
            "data": {"chartData": list(element_data)}
        }
        print("----------------------------------- raw data -------------------------------------")
        print([i['value'] for i in list(element_data)])
        return JsonResponse(res, safe=False)


def delete_all_records(request, sensor_id):
    try:
        count = SensorDataLog.objects.filter(element_id=sensor_id)
        print(len(count))

        SensorDataLog.objects.filter(element_id=sensor_id , max__gt = 45  ).delete()
        return JsonResponse({"status": f"deleted , {len(count)}"}, safe=False)
    except Exception as e:
        return JsonResponse({"status": e}, safe=False)


def test_function(requests):
    pass


def orm_sensor_data(data, usecase):
    if HOUR_MODE:
        if usecase == 'train':
            return (SensorDataLog.objects.filter(timestamp__range=[data['start_time'], data['end_time']],
                                                 element_id=data['element_id'])
                    .annotate(time=TruncHour('timestamp'))
                    .values('time')
                    .annotate(value=Max('max')).
                    values('time', 'value'))

        elif usecase == 'predict':
            no_of_points = data['sequence_length'] + int(data['no_of_prediction'])
            return (SensorDataLog.objects.filter(element_id=data['element_id'])
                    .annotate(time=TruncHour('timestamp'))
                    .values('time').annotate(value=Max('max'))
                    .values('time', 'value')
                    .order_by('-timestamp')[:no_of_points])

    else:
        print("Minute Mode")
        if usecase == 'train':
            return (SensorDataLog.objects.filter(timestamp__range=[data['start_time'], data['end_time']],
                                                 element_id=data['element_id'], max__gt=0.01)
                    .annotate(time=F('timestamp'))
                    .annotate(value=F('max')).
                    values('time', 'value'))
        elif usecase == 'predict':
            no_of_points = data['sequence_length'] + int(data['no_of_prediction'])
            return (SensorDataLog.objects.filter(element_id=data['element_id'], max__gt=0.01)
                    .annotate(time=F('timestamp'))
                    .annotate(value=F('max'))
                    .values('time', 'value')
                    .order_by('-timestamp')[:no_of_points])


@receiver(post_save, sender=SensorDataLog)
def anomaly_logger(sender, instance, created, **kwargs):
    setting_data = (
        SettingsElement.objects.filter(element_id=instance.element_id).values('element_name', 'upper_anamoly_limit',
                                                                              'lower_anamoly_limit', 'prediction',
                                                                              'aggregation_type'))
    anamoly_record = (AnomalyDataLog.objects.filter(element_id=instance.element_id, new_anamoly=True))

    if (setting_data[0]["lower_anamoly_limit"] != 'model not created' and
            setting_data[0]["prediction"] and not (
                    float(setting_data[0]['lower_anamoly_limit']) <= float(instance.max) <= float(
                setting_data[0]['upper_anamoly_limit']))):

        if anamoly_record:
            anamoly_record.update(current_value=instance.max,
                                  aggregation_type=setting_data[0]["aggregation_type"],
                                  time_stamp=instance.timestamp,
                                  no_of_records=instance.no_of_records,
                                  )
        else:
            AnomalyDataLog(element_name=setting_data[0]["element_name"],
                           element_id=instance.element_id,
                           current_value=instance.max,
                           aggregation_type=setting_data[0]["aggregation_type"],
                           time_stamp=instance.timestamp,
                           no_of_records=instance.no_of_records,
                           org_id=instance.org_id,
                           anomaly_ranges=f"{setting_data[0]["lower_anamoly_limit"]} to {setting_data[0]["upper_anamoly_limit"]}",
                           machine='M19').save()


@api_view(['POST'])
def refresh_anomalies(requests):
    try:
        res = {
            'new_set': [],
            'old_set': []
        }
        data = AnomalyDataLog.objects.all()
        for record in list(data.values()):
            if record['new_anamoly']:
                res['new_set'].append(record)
            else:
                res['old_set'].append(record)
        if not requests.data['trail_request']:
            try:
                print("its not trail request")
                a = AnomalyDataLog.objects.filter(new_anamoly=False).delete()
                b = AnomalyDataLog.objects.all().update(new_anamoly=False)
                after_data = AnomalyDataLog.objects.all()
                return JsonResponse(res, safe=False)

            except Exception as e:
                return JsonResponse({"error": e}, safe=False)
        else:
            res['trail_request'] = 'trail request'
            return JsonResponse(['enable trail request to True'], safe=False)
    except Exception as e:
        return JsonResponse([traceback.format_exc()], safe=False)
def dynamic_string(str_,**kwargs):
    return str_.format(**kwargs)

@api_view(['POST'])
def email_anamoly_alert(requests):


    final_data = requests.data['email_data']
    print("dxfgdghfghnfhgnfhnfgh",final_data)

    html_message = open('predictive/templates/mailbody.html', mode='r').read()
    start, end = html_message.find("<!--st-->"), html_message.find("<!--ed-->")
    row_format = html_message[start + 9:end]

    html_rows_dict = dict()
    for table_data in final_data:
        if table_data['org_id'] not in html_rows_dict:
            html_rows_dict[table_data['org_id']] = ''
            print('first')

        html_rows_dict[table_data['org_id']] += dynamic_string(row_format, Sensor=table_data['element_name'],
                                     Limits=table_data['anomaly_ranges'], Actual=table_data['current_value'],
                                     Aggregation=table_data['aggregation_type'],
                                     Status=table_data['Status'])
        print(dynamic_string(row_format, Sensor=table_data['element_name'],
                                     Limits=table_data['anomaly_ranges'], Actual=table_data['current_value'],
                                     Aggregation=table_data['aggregation_type'],
                                     Status=table_data['Status']))

    for i in  html_rows_dict:
         line = SettingsOrg.objects.filter(org_id = i).values('line_code')
         html_message = html_message.replace(row_format, str(html_rows_dict[i]))
         html_message = dynamic_string(html_message,line =line[0]['line_code'] )
         if os.path.exists(i+'.html'): os.remove(i+'.html')
         open(i+'.html', mode='w').write(html_message)
         # send_mail(mail_data['subject'], mail_data['message'], mail_data['from_email'], mail_data['recipient_list'], html_message=html_message)

    return JsonResponse(html_message, safe=False)
