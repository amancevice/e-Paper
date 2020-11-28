import time
from datetime import datetime

from RPi import GPIO  # noqa
from .epaper import (
    DisplayImage,
    EPaper,
    FillRectangle,
    Handshake,
    RefreshAndUpdate,
    SetCurrentDisplayRotation,
)


def main():
    filename = datetime.now().strftime('T%I00.BMP').encode()
    with EPaper() as paper:
        paper.send(Handshake())
        time.sleep(2)
        paper.send(SetCurrentDisplayRotation(SetCurrentDisplayRotation.FLIP))
        paper.send(FillRectangle(0, 0, 800, 600))
        paper.send(DisplayImage(0, 0, filename))
        paper.send(RefreshAndUpdate())
        paper.read_responses(timeout=10)


if __name__ == '__main__':
    main()
