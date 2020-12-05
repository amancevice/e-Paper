import logging

from PIL import Image

from waveshare.spi import EPaper

logging.basicConfig(level=logging.DEBUG)


def main():
    with EPaper(400, 300) as epd:
        epd.init()
        epd.clear()

        # imageblack = self.getbuffer(Image.open('../pic/4in2b-b.bmp'))
        # imagered = self.getbuffer(Image.open('../pic/4in2b-r.bmp'))
        # self.display(imageblack, imagered)


if __name__ == '__main__':
    main()
