from flask import Flask, render_template
from flask_sse import sse
from concurrent.futures import ThreadPoolExecutor
import serial
import logging
import time
from time import sleep

PORT = '/dev/ttyUSB0'
TELEINFO_MEASURE_KEYS = ['IMAX', 'HCHC', 'IINST', 'PAPP', 'ISOUSC', 'ADCO', 'HCHP']

executor = ThreadPoolExecutor(2)

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

@app.route('/push')
def publish_hello():
    sse.publish({"message": "Hello!"}, type='greeting')
    return "Message sent!"

def teleinfo():
    with app.app_context():
        with serial.Serial(
                port=PORT,
                baudrate=1200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.SEVENBITS,
                timeout=1) as ser:

            logging.info("Teleinfo is reading on %s.." % (PORT))

            message = dict()

            line = ser.readline()

            while b'\x02' not in line:
              line = ser.readline()

            line = ser.readline()

            while True:
              decoded_line = line.decode("utf-8")

              print(decoded_line)

              data = line_str.split(" ")

              key = message[0]

              if key in TELEINFO_MEASURE_KEYS :
                  message[key] = int(data[1])
              else:
                  message[key] = data[1]

              if b'\x03' in line:
                print(data)
                #sse.publish({"": "Hello!"}, type='greeting')

              line = ser.readline()

executor.submit(teleinfo)
