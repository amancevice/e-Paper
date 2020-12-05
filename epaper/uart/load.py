#!/usr/bin/env python3
import time

from RPi import GPIO  # noqa
from waveshare.uart import (
    EPaper,
    Handshake,
    ImportImage,
    SetStorageMode,
)


def main():
    with EPaper() as paper:
        paper.send(Handshake())
        time.sleep(2)
        paper.send(SetStorageMode(SetStorageMode.TF_MODE))
        paper.send(ImportImage())
        time.sleep(10)


if __name__ == '__main__':
    main()
