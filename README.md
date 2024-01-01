# AS7343 Spectrum Sensor Python Library

[中文](https://github.com/719084/as7343_python/blob/main/README.zh_CN.md)

![AS7343 Spectrum Sensor](https://github.com/719084/as7343_python/blob/main/GYAS7341_7343.jpg)

A Python library for interfacing with the AS7343 Spectrum Sensor. This library provides an easy-to-use interface to communicate with the sensor, read spectral data, and perform various operations.

## Features

- **Read Spectral Data:** Retrieve spectral data from the AS7343 sensor.
- **Control Sensor Settings:** Easily configure settings such as integration time, ADC gain, and more.
- **Flicker Detection:** Enable flicker detection and get real-time data for analysis (to be finished).
- **Data Processing:** Convenient methods for processing and extracting meaningful information from the sensor data.

## Usage
```python
from as7343 import AS7343

# Create an instance of the AS7343 class
sensor = AS7343()

# Initialize the sensor
sensor.init_as7343(cycle_num=6)

# Read spectral data
data = sensor.get_data(cycle_num=6)

# Process the data
keys, values, sorted_dict = sensor.data_process()

# Perform other operations...
```
## Documentation
Check out the datasheet [here](https://github.com/719084/as7343_python/blob/main/AS7343_DS001046_4_00.pdf) for detailed information.

## Contributing
Contributions are welcome! Fork the repository, create your feature branch, commit your changes, and submit a pull request.