import json
import sqlite3
import paho.mqtt.client as paho
from config import TOPICS_TO_GPIO_MAP, MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD, MQTT_HOST, MQTT_PORT, DB_NAME
from shared_state import queue


def on_publish(client, userdata, result):  # create function for callback
    print("data published \n")


def on_message(client, userdata, message):
    data = json.loads(message.payload.decode("utf-8"))
    transmitter_gpio = TOPICS_TO_GPIO_MAP.get(message.topic, None)
    if transmitter_gpio is None:
        print("Unknown topic")
        return
    send_signals(
        transmitter_gpio=transmitter_gpio,
        payload=data.get('payload', ''),
        signals=data.get('chars', {}),
        protocol_time=data.get('T', 0.00025),
        rounds=data.get('M', 10),
        device_id=data.get('id', None),
        state=data.get('state', None),
    )


def on_connect(client, userdata, flags, rc, *extra_params, **extra_kwargs):
    print("Connected with result code:" + str(rc))
    # subscribe for all devices of user
    for topic, gpio in TOPICS_TO_GPIO_MAP.items():
        client.subscribe([(topic, 0)])


def convert_to_signal(payload, signals, protocol_time):
    str_payload = payload.replace(" ", "")
    t = protocol_time
    _payload = []
    for c in str_payload:
        on, off = signals.get(c, (None, None))
        if on is not None:
            _payload.append((1, on * t))
        if off is not None:
            _payload.append((0, off * t))
    return _payload


def send_signals(device_id, state, transmitter_gpio, payload, signals, protocol_time, rounds):
    pl = convert_to_signal(payload, signals, protocol_time)
    data = (pl, transmitter_gpio, rounds)
    if device_id is not None and state is not None:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        payload_json = str(json.dumps(pl))
        # print(device_id, state, transmitter_gpio, rounds, payload_json)
        # Save state to database or update if id exists
        cur.execute("SELECT * FROM state WHERE id=?", (device_id,))
        if cur.fetchone() is not None:
            cur.execute("UPDATE state SET state=?, payload=?, transmitter_gpio=?, rounds=? WHERE id=?",
                        (state, payload_json, transmitter_gpio, rounds, device_id))
        else:
            cur.execute("INSERT INTO state(id, state, payload, transmitter_gpio, rounds) VALUES (?, ?, ?, ?, ?)",
                        (device_id, state, payload_json, transmitter_gpio, rounds))
        con.commit()
    queue.put(data)


def run_client():
    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION2,
                         client_id=MQTT_CLIENT_ID)  # create client object
    client.on_connect = on_connect
    client.on_publish = on_publish  # assign function to callback
    client.on_message = on_message  # assign function to callback
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.connect(MQTT_HOST, MQTT_PORT)  # establish connection
    client.loop_forever(retry_first_connection=True)  # start loop to process received messages

