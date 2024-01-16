import requests

def get_temperature_reading(response: dict, sensor_number: int) -> float:
    return int(response[str(sensor_number)]["state"]["temperature"]) / 100

def get_hue_sensor_readings() -> tuple:
    response = requests.get("http://192.168.0.11/api/iL0YcF4WFvvEo0Sdf-BdBNdrtA2-YQ1PIwO-YP96/sensors").json()
    bathroom_temp = get_temperature_reading(response, 25)
    closet_temp = get_temperature_reading(response, 53)
    staircase_temp = get_temperature_reading(response, 62)
    return(bathroom_temp, closet_temp, staircase_temp)
