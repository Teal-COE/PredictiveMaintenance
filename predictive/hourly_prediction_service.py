import requests

sensor_url = 'http://127.0.0.1:8000/predictive/pred_sensors/'
prediction_url = 'http://127.0.0.1:8000/predictive/pred_sensors/'

prediction_elements = requests.post(url)

for element_data in prediction_elements.json():
    if element_data['model_path'] != 'model not created':
        print(element_data['model_path'])
