import logging
import time

from serial import Serial, SerialException
from serial.tools import list_ports


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
            default=None
        )
        parser.add_argument(
            '-b', '--baud',
            dest='baud',
            type=str,
            help='Baudrate (default 9600)',
            default=9600
        )
        parser.add_argument(
            '--dry',
            dest='dry',
            action='store_true')

    def get_port(self, initial):
        available_ports = list_ports.comports()
        if len(available_ports) == 0:
            return None
        return next(port.device for port in available_ports if port.device == initial) or available_ports[0].device

    def handle(self, *args, **options):
        initial_port, baud, dry = options.get('port'), options.get('baud'), options.get('dry')
        port = self.get_port(initial_port)
        ser = Serial(port, baud)

        logger = logging.getLogger(__name__)

        reader = ReadingContainer()

        while 1:
            while not ser.is_open:
                port = self.get_port(initial_port)
                print('.', end='', flush=True)
                if port:
                    ser.setPort(port)
                    try:
                        ser.open()
                        logger.info('Serial connected', port, baud)
                        print('Serial connected', port, baud)
                        break
                    except SerialException as e:
                        print('\n', e)
                time.sleep(5)

            try:
                serial_line = ser.readline().decode("utf-8")
                reader.parse_line(serial_line)
                if reader.completed:
                    if dry:
                        print(reader.last_raw)
                    else:
                        reader.save()
                    reader = ReadingContainer()

            except KeyboardInterrupt:
                logger.info('Serial reader closed, keyboard interrupt')
                print('Serial reader closed, keyboard interrupt')
                ser.close()
                break

            except SerialException as e:
                logger.info('Serial exception', e)
                print('Serial exception', e)
                ser.close()

