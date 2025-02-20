import random

import requests

url = 'http://192.168.119.1:9001/predictive/datalog/'


def get_random_data():
    common_range = range(15, 21)  # 15 to 20
    rare_range = range(20, 26)  # 20 to 25
    very_rare_range = range(25, 31)  # 25 to 3

    weights = [0.6] * len(common_range) + [0.2] * len(rare_range) + [0.1] * len(very_rare_range)

    all_numbers = list(common_range) + list(rare_range) + list(very_rare_range)
    return random.choices(all_numbers, weights=weights, k=3)[0]


value = 0.0

for date in range(1, 8):
         for hour in range(23):
            value = value+1.5
            data = {
                "element_id": "inc1",
                "max": value,
                "min": random.randint(13, 15),
                "avg": random.randint(16, 21),
                "no_of_records": "60",
                "timestamp": f"2025-02-{f'{date:02}'} {f'{hour:02}'}:10:19.000",
                "org_id": "5"}
            req = requests.post(url, data)
            if req.status_code == 201:
                print(f"2024-12-{date} {hour}:{19}:19.000"  , value)
            else:
                print(req.status_code , value)
