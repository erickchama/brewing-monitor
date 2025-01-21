def calibrate_sensor(sensor_value, sensor_value1, actual_value1, sensor_value2, actual_value2):
    # Calculate the scaling factor (a) and the offset (b)
    a = (actual_value2 - actual_value1) / (sensor_value2 - sensor_value1) 
    b = actual_value1 - a * sensor_value1
    
    # Apply the calibration to the sensor_value
    calibrated_value = a * sensor_value + b
    
    return calibrated_value
# Example usage:
sensor_value1 = 1.054 # Raw sensor value at point 1 
actual_value1 = 1.049 # Known actual value at point 1 (e.g., 0) 
sensor_value2 = 1.011 # Raw sensor value at 
actual_value2 = 1.000 # Known actual value at point 2 (e.g., 50)
# A raw sensor value to calibrate
raw_sensor_value = 1.0466
# Calibrate the sensor
calibrated_value = calibrate_sensor(raw_sensor_value, sensor_value1, actual_value1, sensor_value2, actual_value2)
print(f"Calibrated value: {calibrated_value}")
