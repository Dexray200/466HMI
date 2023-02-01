#!/usr/bin/env python


from pymodbus.client.sync import ModbusTcpClient as ModbusClient
# from pymodbus.client.sync import ModbusUdpClient as ModbusClient
import PySimpleGUI as sg
import logging
import time

FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.INFO)

# Modbus IP and Port
MODBUS_ADDR = "localhost"
MODBUS_PORT = 502

# Graph Variables and settings
STEP_SIZE = 3
SAMPLES = 300
SAMPLE_MAX = 99
SAMPLE_MIN = 46
CANVAS_SIZE = (250, 200)

def run_sync_client():

    # Connect to the MODBUS Server
    client = ModbusClient(MODBUS_ADDR, port=MODBUS_PORT)
    if not client.connect():  # .connect() returns True if connection established
        print("[Error] Fail to connect to modbus slave %s:%d." % (MODBUS_ADDR, MODBUS_PORT))
        exit()
    client.connect()
    log.info(client)
    log.info("Example MODBUS HMI with LocalHost.")

    # Register Addresses (Coils, True/False)
    M0ADDR = 0
    M1ADDR = 1
    M2ADDR = 2
    M3ADDR = 3
    M4ADDR = 4
    M5ADDR = 5
    M7ADDR = 7
    M8ADDR = 8
    M9ADDR = 9

    # Holding Registers, 16Bit Words
    MW0ADDR = 0
    MW1ADDR = 1
    MW2ADDR = 2
    MW3ADDR = 3

    # Create and initialize the window for HMI
    sg.ChangeLookAndFeel('DarkRed')
    layout = [
        [sg.Text('Voltage: ', font=('Helvetica', 16)), sg.Text(size=(3, 1), key='-volts-', font=('Helvetica', 14)),
         sg.Text(size=(2, 1), key=('-unit-'), font=('Helvetica', 14))],
        [sg.Text('Threshold:    ', font=('Helvetica', 16)),
         sg.Text(size=(3, 1), key='-OUTPUT-', font=('Helvetica', 14)),
         sg.Text(size=(2, 1), key=('-unit-'), font=('Helvetica', 14))],
        [sg.Frame('Threshold Setting:', [[
            sg.Slider(size=(40, 45), range=(35, 104), orientation='h', default_value=85, key='-IN-')], [
            sg.Text(key='-hightemp-', font=('Helvetica', 16))]])],
    [sg.Graph(CANVAS_SIZE, (0, SAMPLE_MIN), (SAMPLES, SAMPLE_MAX), background_color= 'white', key = '-graph-')]]

    window = sg.Window('Voltage and Current Setting', layout)
   # graph = window['-graph-']

   # lastTemp = prev_y = 50
   # i = prev_x = 0
    #line = graph.draw_line((0, 85), (SAMPLES, 85), color='red')
    line_y = 85

    while True:
        event, values = window.read(timeout=100)
        if event in (sg.WIN_CLOSED, 'EXIT'):
            break
        threshold = int(values['-IN-'])
        window['-OUTPUT-'].update(threshold)

        rr = client.write_register(MW1ADDR, threshold)
        assert not rr.isError()

        rr = client.read_holding_registers(MW1ADDR, 1)
        assert not rr.isError()

        threshold_server = rr.registers[0]

        log.info(f"Reading back Threshold from Server")
        log.info(f"Threshold = {threshold_server}")

        rr = client.read_holding_registers(MW3ADDR, 1)
        assert not rr.isError()
        adc_value = rr.registers[0]

        # Assume 10bit adc with ref voltage of 200
        volts = ((adc_value/1024)*200)

        unit = 'V'
        rq1 = client.read_coils(M0ADDR, 1)
        assert not rq1.isError()
        if rq1.bits[0]:
            unit = 'V'

        rq2 = client.read_coils(M1ADDR, 1)
        assert not rq2.isError()
        if rq2.bits[0]:
            unit = 'A'

        window['-volts-'].update(volts)
        window['-unit-'].update(unit)

        #new_x, new_y = i, volts
        #if i >= SAMPLES:
        # shift graph over if full of data
       #     graph.move(-STEP_SIZE, 0)
       #    graph.MoveFigure(line, STEP_SIZE, 0)
       #     prev_x = prev_x - STEP_SIZE

       #graph.draw_line((prev_x, prev_y), (new_x, new_y), color='black')

        #a = values['-IN-']
        #graph.MoveFigure(line, 0, a - line_y)
       # line_y = a
       # prev_x, prev_y = new_x, new_y
       # i += STEP_SIZE if i < SAMPLES else 0
       # lastTemp = volts

        # Check if temperature is above threshold and update the window
        #if volt_value >= threshold:
        #    window['-hightemp-'].update('HIGH TEMP ALERT')
        #    window['-heater-'].update('OFF')
        #    window['-fan-'].update('OFF')
        #else:
        #    window['-hightemp-'].update('')
        #    window['-heater-'].update('ON')
        #    window['-fan-'].update('ON')

        # Set the fan setting on the PLC side through modbus
        #if values['-fanset-'] == 'Fan AUTO':
        #    rq = client.write_coil(M5ADDR, 1)
        #    assert not rq.isError()
        #else:
        #    rq = client.write_coil(M5ADDR, 0)
        #    assert not rq.isError()

        #if values['-fanset-'] == 'Fan ON':
        #    rq = client.write_coil(M4ADDR, 1)
        #    assert not rq.isError()
        #else:
        #    rq = client.write_coil(M4ADDR, 0)
        #   assert not rq.isError()
    #
    # close the client
    #
    client.close()
    window.close()
    log.info(f"Exiting")


if __name__ == "__main__":
    run_sync_client()
