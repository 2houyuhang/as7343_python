import smbus
import time
import re
from definition import *


class AS7343:
    def __init__(self):
        self.bus = smbus.SMBus(1)  # 1 means /dev/i2c-1
        self.data_num = 7

    def reset(self):
        info = self.bus.read_byte_data(device_address, CONTROL_REGISTER)
        print("info: ", info)
        self.bus.write_byte_data(device_address, CONTROL_REGISTER, info | RESET)
        time.sleep(0.5)
        self.bus.write_byte_data(device_address, CFG20_REGISTER, 0x00)
        print("reset done!")

    def power_off(self):
        info = self.bus.read_byte_data(device_address, ENABLE_REGISTER)
        print("info: ", info)
        self.bus.write_byte_data(device_address, ENABLE_REGISTER, ENABLE_POWER_OFF)
        time.sleep(0.5)
        print("powerOff done!")

    def power_on(self):
        info = self.bus.read_byte_data(device_address, ENABLE_REGISTER)
        print("info: ", info)
        self.bus.write_byte_data(device_address, ENABLE_REGISTER, info | ENABLE_POWER_ON)
        print("powerOn done!")

    def get_id_info(self):
        AUXID = self.bus.read_byte_data(device_address, AUXID_REGISTER)
        REVID = self.bus.read_byte_data(device_address, REVID_REGISTER)
        ID = self.bus.read_byte_data(device_address, ID_REGISTER)
        print("ID: " + str(ID) + " AUXID: " + str(AUXID) + " REVID: " + str(REVID))
        return ID, AUXID, REVID

    def set_reg_blank(self, mode):
        info = self.bus.read_byte_data(device_address, CFG0_REGISTER)
        if mode:
            self.bus.write_byte_data(device_address, CFG0_REGISTER, info | ACCESS_REGISTER_ABOVE)
        else:
            self.bus.write_byte_data(device_address, CFG0_REGISTER, info | ACCESS_REGISTER_BELOW)
        print("setRegBlank done!")

    def set_adc_gain(self, gain):
        gain = int(gain)
        if gain < 0 or gain > 12:
            raise ValueError("Invalid Gain. Expected integer in [0,12].")
        else:
            self.bus.write_byte_data(device_address, CFG1_REGISTER, gain)
        print("setADCGain done!")

    def channel_select(self, mode):
        if mode not in (6, 12, 18):
            raise ValueError("Invalid mode. Expected 6, 12 or 18.")
        info = self.bus.read_byte_data(device_address, CFG20_REGISTER)
        mode = int(mode / 6)

        if mode == 1:
            mode = 0
        self.bus.write_byte_data(device_address, CFG20_REGISTER, info | (mode << 5))
        info = self.bus.read_byte_data(device_address, CFG20_REGISTER)
        print(bin(info))
        print("channelSelect done!")

    def set_wait_time(self, wtime):
        wtime = wtime - 1
        self.bus.write_byte_data(device_address, WTIME_REGISTER, wtime)
        print("setWaitTime done!")

    def set_integration_time(self, atime, astep):
        self.bus.write_byte_data(device_address, ATIME_REGISTER, atime)
        astep_l = int(astep % 256)
        astep_h = int(astep / 256)
        self.bus.write_byte_data(device_address, ASTEP_H_REGISTER, astep_h)
        self.bus.write_byte_data(device_address, ASTEP_L_REGISTER, astep_l)
        print("Integration Time: ", int((atime + 1) * (astep + 1) * 2.78))
        print("setIntegtrationTime done!")

    def enable_spectral_measurement(self):
        info = self.bus.read_byte_data(device_address, ENABLE_REGISTER)
        print(bin(info | ENABLE_SpectralMeasurement))
        self.bus.write_byte_data(device_address, ENABLE_REGISTER, info | ENABLE_SpectralMeasurement)
        print("enableSpectralMeasurement done!")

    def enable_flicker_detection(self):
        info = self.bus.read_byte_data(device_address, ENABLE_REGISTER)
        self.bus.write_byte_data(device_address, ENABLE_REGISTER, info | ENABLE_FlickerDetection)
        print("enableFlickerDetection done!")

    def led_control(self, switch, brightness):
        if switch:
            brightness = int(brightness / 100 * 0x7F)
            self.bus.write_byte_data(device_address, LED_REGISTER, brightness | (1 << 7))
        else:
            self.bus.write_byte_data(device_address, LED_REGISTER, LED_OFF)
        print("LEDControl done!")

    def read_spectral_counts(self):
        channels = [0x95, 0x97, 0x99, 0x9B, 0x9D, 0x9F, 0xA1, 0xA3, 0XA5, 0xA7, 0XA9, 0xAB, 0xAD, 0XAF, 0xB1, 0xB3,
                    0xB5,
                    0xB7]
        result = [0] * 17
        for index, channel in enumerate(channels):
            data_l = self.bus.read_byte_data(device_address, channel)
            data_h = self.bus.read_byte_data(device_address, channel + 1)
            data = (data_h << 8) | data_l
            result[index - 1] = data
        print("readSpectralCounts done!")
        return result

    def sp_fifo_map_set(self):
        info = self.bus.read_byte_data(device_address, FIFO_MAP_REGISTER)
        self.bus.write_byte_data(device_address, FIFO_MAP_REGISTER, info | SP_FIFO_MAP_SET)

    def fd_fifo_map_set(self):
        info = self.bus.read_byte_data(device_address, FIFO_CFG0_REGISTER)
        self.bus.write_byte_data(device_address, FIFO_CFG0_REGISTER, info | FD_FIFO_MAP_SET)
        print("FD_FIFO_map_set done!")

    def init_as7343(self, cycle_num):
        self.reset()
        self.power_on()
        self.set_reg_blank(0)
        self.get_id_info()
        self.set_reg_blank(1)
        self.channel_select(cycle_num)
        self.set_adc_gain(10)
        self.set_wait_time(100)
        self.set_integration_time(99, 99)
        self.led_control(0, 0)
        self.sp_fifo_map_set()
        self.enable_spectral_measurement()
        self.cycle_num = cycle_num
        print("init_as7343 done!")

    def read_data(self, cycle_num):
        data = []
        FIFO_LVL_info = self.bus.read_byte_data(device_address, FIFO_LVL_REGISTER)

        while self.bus.read_byte_data(device_address, FIFO_LVL_REGISTER) < cycle_num / 6 * self.data_num:
            time.sleep(0.001)

        FIFO_LVL_info = self.bus.read_byte_data(device_address, FIFO_LVL_REGISTER)
        for i in range(cycle_num * self.data_num):
            FIFO_DATA_H = self.bus.read_byte_data(device_address, FDATA_H_REGISTER)
            FIFO_DATA_L = self.bus.read_byte_data(device_address, FDATA_L_REGISTER)
            FDATA = (FIFO_DATA_H << 8) | FIFO_DATA_L
            data.append(FDATA)

        FIFO_LVL_info = self.bus.read_byte_data(device_address, FIFO_LVL_REGISTER)
        return data

    def get_data(self, cycle_num):
        result = []
        result1Keys = ['FZ', 'FY', 'FXL', 'NIR', '2xVIS', 'FD']
        result2Keys = ['F2', 'F3', 'F4', 'F6', '2xVIS', 'FD']
        result3Keys = ['F1', 'F7', 'F8', 'F5', '2xVIS', 'FD']
        FDATA = self.read_data(cycle_num)
        if cycle_num == 6:
            result1_dict = dict(zip(result1Keys, FDATA[0:7]))
            result.append(result1_dict)
        elif cycle_num == 12:
            result1_dict = dict(zip(result1Keys, FDATA[0:7]))
            result.append(result1_dict)
            result2_dict = dict(zip(result2Keys, FDATA[7:14]))
            result.append(result2_dict)
        else:
            result1_dict = dict(zip(result1Keys, FDATA[0:7]))
            result.append(result1_dict)
            result2_dict = dict(zip(result2Keys, FDATA[7:14]))
            result.append(result2_dict)
            result3_dict = dict(zip(result3Keys, FDATA[14:21]))
            result.append(result3_dict)
        print("getData done!")
        return result

    def extract_numbers(self, s):
        numbers = [int(num) for num in re.findall(r'\d+', s)]
        return numbers[0] if numbers else None

    def data_process(self):
        data = self.get_data(self.cycle_num)
        keys = []
        values = []
        merged_dict = {}
        for d in data:
            d.pop('FD', None)
            d.pop('2xVIS', None)

            keys += list(d.keys())
            values += list(d.values())
            merged_dict.update(d)

        key_mapping = {'F1': '405+-30nm', 'F2': '425+-22nm', 'FZ': '450+-55nm', 'F3': '475+-30nm', 'F4': '515+-40nm',
                       'FY': '555+-100nm', 'F5': '550+-35nm', 'FXL': '600+-80nm', 'F6': '640+-50nm', 'F7': '690+-55nm',
                       'F8': '745+-60nm', 'NIR': '855+-54nm'}

        merged_dict = {key_mapping.get(old_key, old_key): value for old_key, value in merged_dict.items()}
        sorted_dict = {key: merged_dict[key] for key in sorted(merged_dict, key=lambda x: self.extract_numbers(x))}
        print(sorted_dict)
        return keys, values, sorted_dict


if __name__ == '__main__':
    # example
    cycle_num = 6
    as7343_instance = AS7343()
    as7343_instance.init_as7343(cycle_num)
    as7343_instance.data_process()
