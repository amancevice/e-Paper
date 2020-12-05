import logging

from PIL import Image

from waveshare.spi import EPaper

logging.basicConfig(level=logging.DEBUG)


def main():
    blk = Image.open('400x300/BH11M21.BMP')
    red = Image.open('400x300/RH11M21.BMP')
    with EPaper(400, 300) as epd:
        epd.init()
        epd.clear()
        epd.display(epd.getbuffer(blk), epd.getbuffer(red))


if __name__ == '__main__':
    main()
