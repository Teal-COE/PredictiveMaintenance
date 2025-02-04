import requests

sensor_url = 'http://127.0.0.1:8000/predictive/pred_sensors/'
prediction_url = 'http://127.0.0.1:8000/predictive/predict/'

prediction_elements = requests.post(sensor_url)




for element_data in prediction_elements.json():
    if element_data['model_path'] != 'model not created':
        print(element_data['element_id'])
        data = {
            "element_id": element_data['element_id'],
            "no_of_prediction": "2",
            "with_actual": 'false'
        }
        res = requests.post(prediction_url , data)
        print(res.json())
