from AS7343 import AS7343

cycle_num = 6
as7343_instance = AS7343()
as7343_instance.init_as7343(cycle_num)
as7343_instance.led_control(1,10)
as7343_instance.data_process()
as7343_instance.led_control(0,0)