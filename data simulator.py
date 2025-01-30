import random

import requests

url = 'http://127.0.0.1:8000/predictive/datalog/'


def get_random_data():
    common_range = range(15, 21)  # 15 to 20
    rare_range = range(20, 26)  # 20 to 25
    very_rare_range = range(25, 31)  # 25 to 3

    weights = [0.6] * len(common_range) + [0.2] * len(rare_range) + [0.1] * len(very_rare_range)

    all_numbers = list(common_range) + list(rare_range) + list(very_rare_range)
    return random.choices(all_numbers, weights=weights, k=3)[0]


for date in range(20, 32):
    for hour in range(24):
        for minute in range(1, 60):
            minute = str(minute)
            if len(minute) == 1:
                minute = '0' + str(minute)

            data = {
                "element_id": "S20",
                "max": get_random_data(),
                "min": random.randint(13, 15),
                "avg": random.randint(16, 21),
                "no_of_records": "60",
                "timestamp": f"2024-12-{date} {hour}:{minute}:19.000",
                "org_id": "19"}

            req = requests.post(url, data)
            if req.status_code == 201:
                print(f"2024-12-{date} {hour}:{minute}:19.000")
            else:
                print(req.status_code)
