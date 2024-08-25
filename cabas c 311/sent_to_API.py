import sqlite3
import json
import requests

def send_data_to_api(api_url, single_result):
    payload = {'data': single_result}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(api_url, headers=headers, json=payload)
    return response

def get_unsent_data_from_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = 'SELECT id, sample_id, json_data FROM astm_data WHERE sent_to_api = 0 ORDER BY id DESC LIMIT 1000'
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    if not data:
        print("All data has already been sent.")
    return data

def format_data(data):
    formatted_data = []
    for row in data:
        formatted_data.append({
            'id': row[0],
            # 'sample_id': row[1],
            'json_data': json.loads(row[2]),
        })
    return formatted_data

def update_sent_status(db_path, ids):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = 'UPDATE astm_data SET sent_to_api = 1 WHERE id IN ({})'.format(','.join('?' for _ in ids))
    cursor.execute(query, ids)
    conn.commit()
    conn.close()

# Example usage
db_path = 'habib07.db'
data = get_unsent_data_from_database(db_path)

if data:
    formatted_data = format_data(data)

    try:
        api_url = json.load(open('serial_params.json'))['api_link']
    except FileNotFoundError:
        print("serial_params.json file not found.")
        api_url = None
    except json.JSONDecodeError:
        print("Error decoding JSON from serial_params.json.")
        api_url = None

    if api_url:
        successful_Serial_ids = []
        response = None  # Ensuring-------- response is defined

        for single_result in formatted_data:
            response = send_data_to_api(api_url, single_result)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    successful_Serial_ids.append(single_result['id'])

        if successful_Serial_ids:
            update_sent_status(db_path, successful_Serial_ids)
        else:
            print("No data was successfully sent.")

        print("Successfully sent IDs:", successful_Serial_ids)

        if response:
            print(response.status_code)
            print(response.json())
else:
    print("No data to send.")
