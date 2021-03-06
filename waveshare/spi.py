import logging
import time

import spidev
from RPi import GPIO


class RaspberryPi:
    # Pin definition
    RESET_PIN = 17
    DC_PIN = 25
    CS_PIN = 8
    BUSY_PIN = 24

    def __init__(self):
        # SPI device, bus = 0, device = 0
        self.SPI = spidev.SpiDev(0, 0)

    def digital_write(self, pin, value):
        GPIO.output(pin, value)

    def digital_read(self, pin):
        return GPIO.input(pin)

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes(data)

    def module_init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.RESET_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        GPIO.setup(self.BUSY_PIN, GPIO.IN)
        self.SPI.max_speed_hz = 4000000
        self.SPI.mode = 0b00
        return 0

    def module_exit(self):
        logging.debug('spi end')
        self.SPI.close()

        logging.debug('close 5V, Module enters 0 power consumption ...')
        GPIO.output(self.RESET_PIN, 0)
        GPIO.output(self.DC_PIN, 0)

        GPIO.cleanup()


class EPaper:
    def __init__(self, width=400, height=300):
        self.board = RaspberryPi()
        self.width = width
        self.height = height
        self.size = int(self.width * self.height / 8)

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, type, value, traceback):
        self.dev_exit()
        GPIO.cleanup()

    def clear(self):
        self.send_command(0x10)
        self.send_data(*([0xFF] * self.size))

        self.send_command(0x13)
        self.send_data(*([0xFF] * self.size))

        self.send_command(0x12)
        self.read_busy()

    def dev_exit(self):
        self.board.module_exit()

    def display(self, imageblack, imagered):
        self.send_command(0x10)
        self.send_data(*imageblack)

        self.send_command(0x13)
        self.send_data(*imagered)

        self.send_command(0x12)
        self.read_busy()

    def getbuffer(self, image):
        # logging.debug('bufsiz = ', int(self.width / 8) * self.height)
        buf = [0xFF] * (int(self.width / 8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        # logging.debug('imwidth = %d, imheight = %d', imwidth, imheight)
        if(imwidth == self.width and imheight == self.height):
            logging.debug("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels
                    # at the current position.
                    if pixels[x, y] == 0:
                        z = x + y * self.width
                        buf[int(z / 8)] &= ~(0x80 >> (x % 8))
        elif(imwidth == self.height and imheight == self.width):
            logging.debug("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        z = newx + newy * self.width
                        buf[int(z / 8)] &= ~(0x80 >> (y % 8))
        return buf

    def init(self):
        if (self.board.module_init() != 0):
            return -1

        self.reset()

        self.send_command(0x06)  # BOOSTER_SOFT_START
        self.send_data(0x17)
        self.send_data(0x17)
        self.send_data(0x17)  # 07 0f 17 1f 27 2F 37 2f

        self.send_command(0x04)  # POWER_ON
        self.read_busy()

        self.send_command(0x00)  # PANEL_SETTING
        self.send_data(0x0F)  # LUT from OTP

        return 0

    def read_busy(self):
        logging.debug("e-Paper busy")

        # 0: idle, 1: busy
        while(self.board.digital_read(self.board.BUSY_PIN) == 0):
            self.board.delay_ms(100)

        logging.debug("e-Paper busy release")

    def reset(self):
        self.board.digital_write(self.board.RESET_PIN, 1)
        self.board.delay_ms(200)
        self.board.digital_write(self.board.RESET_PIN, 0)
        self.board.delay_ms(10)
        self.board.digital_write(self.board.RESET_PIN, 1)
        self.board.delay_ms(200)

    def send_command(self, command):
        self.board.digital_write(self.board.DC_PIN, 0)
        self.board.digital_write(self.board.CS_PIN, 0)
        self.board.spi_writebyte([command])
        self.board.digital_write(self.board.CS_PIN, 1)

    def send_data(self, *data):
        for byte in data:
            self.board.digital_write(self.board.DC_PIN, 1)
            self.board.digital_write(self.board.CS_PIN, 0)
            self.board.spi_writebyte([byte])
            self.board.digital_write(self.board.CS_PIN, 1)

    def sleep(self):
        self.send_command(0x02)  # POWER_OFF
        self.read_busy()
        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)  # check code
