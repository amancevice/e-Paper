import time
from datetime import datetime

from RPi import GPIO  # noqa
from waveshare.uart import (
    DisplayImage,
    EPaper,
    FillRectangle,
    Handshake,
    RefreshAndUpdate,
    SetCurrentDisplayRotation,
)


def main():
    now = datetime.now()
    hour = 'H{:02d}.BMP'.format(now.hour % 12).encode()
    minute = 'M{:02d}.BMP'.format(now.minute - now.minute % 5).encode()
    y = 315 if hour != b'H08.BMP' else 395

    with EPaper() as paper:
        paper.send(Handshake())
        time.sleep(2)
        paper.send(SetCurrentDisplayRotation(SetCurrentDisplayRotation.FLIP))

        paper.send(FillRectangle(0, 0, 800, 600))
        paper.send(DisplayImage(0, 0, hour))
        paper.read_responses()

        paper.send(DisplayImage(0, y, minute))
        paper.send(RefreshAndUpdate())
        paper.read_responses()


if __name__ == '__main__':
    main()
