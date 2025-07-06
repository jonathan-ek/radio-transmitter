MQTT_HOST = "homectrl.se"
MQTT_PORT = 1883
MQTT_USERNAME = "lights"
MQTT_PASSWORD = "lightserver123"
MQTT_CLIENT_ID = "light-control-1"
GPIO_FOR_433_SENDER = 23
GPIO_FOR_315_SENDER = 27
TOPICS_TO_GPIO_MAP = {
    "home/light/433/switch": GPIO_FOR_433_SENDER,
    "home/cover/433/set": GPIO_FOR_433_SENDER,
    "home/light/315/switch": GPIO_FOR_433_SENDER,
}

DB_NAME = "light_control.db"

