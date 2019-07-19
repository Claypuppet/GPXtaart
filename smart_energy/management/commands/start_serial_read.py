import logging
import time

import serial
from django.core.management.base import BaseCommand, CommandError
from smart_energy.models import ReadingContainer


class Command(BaseCommand):
    help = 'Starts the serial read of the smart meter'

    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--port',
            type=str,
            dest='port',
            help='Device location, e.g. /dev/ttyUSBx or COMx',
            required=True
        )
        parser.add_argument(
            '-b', '--baud',
            dest='baud',
            type=str,
            help='Baudrate (default 9600)',
            default=9600
        )

    def handle(self, *args, **options):
        port, baud = options.get('port'), options.get('baud')
        ser = serial.Serial(port, baud)

        logger = logging.getLogger(__name__)

        reader = ReadingContainer()
        print('Starting ser conn', port, baud)

        while 1:
            while not ser.is_open:
                try:
                    ser.open()
                    logger.info('Serial connected', port, baud)
                    print('Serial connected', port, baud)
                except serial.SerialException as e:
                    print('.', e)
                    time.sleep(1)

            try:
                serial_line = ser.readline().decode("utf-8")
                reader.parse_line(serial_line)

            except KeyboardInterrupt:
                logger.info('Serial reader closed, keyboard interrupt')
                print('Serial reader closed, keyboard interrupt')
                ser.close()
                break

            except serial.SerialException as e:
                logger.info('Serial exception', e)
                print('Serial exception', e)
                ser.close()

