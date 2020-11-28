#!/usr/bin/env python
"""

Original source at https://github.com/yy502/ePaperDisplay

Sample BMP header structure, total = 70 bytes
!!! little-endian !!!

Bitmap file header 14 bytes
42 4D          "BM"
C6 A9 03 00    FileSize = 240,070       <= dynamic value
00 00          Reserved
00 00          Reserved
46 00 00 00    Offset = 70 = 14+56

DIB header (bitmap information header)
BITMAPV3INFOHEADER 56 bytes
28 00 00 00    Size = 40
20 03 00 00    Width = 800              <= dynamic value
58 02 00 00    Height = 600             <= dynamic value
01 00          Planes = 1
04 00          BitCount = 4
00 00 00 00    compression
00 00 00 00    SizeImage
00 00 00 00    XPerlPerMeter
00 00 00 00    YPerlPerMeter
04 00 00 00    Colours used = 4
00 00 00 00    ColorImportant
00 00 00 00    Colour definition index 0
55 55 55 00    Colour definition index 1
AA AA AA 00    Colour definition index 2
FF FF FF 00    Colour definition index 3

"""
import argparse
import subprocess
import sys

# to insert File Size, Width and Height with hex strings in order
BMP_HEADER = (
    '42 4D %s 00 00 00 00 46 00 00 00 28 00 00 00 %s %s 01 00 04 00 00 00 00 '
    '00 00 00 00 00 00 00 00 00 00 00 00 00 04 00 00 00 00 00 00 00 00 00 00 '
    '00 55 55 55 00 AA AA AA 00 FF FF FF 00'
)
BMP_HEADER_SIZE = 70
BPP = 4
BYTE = 8
ALIGNMENT = 4  # bytes per row

BLACK = '0'
DARK_GRAY = '1'
GRAY = '2'
WHITE = '3'
GRAYSCALE = [BLACK, DARK_GRAY, GRAY, WHITE]


def to_grayscale(infile, colors, invert=False):
    """
    Convert an input file to grayscale using ImageMagik's `convert` command.
    """
    # Assemble `convert` command
    cmd = (
        "convert {infile} "
        "-colors {colors} "
        "-colorspace gray "
        "-depth 2 "
        "-resize '800x600>' "
    ).format(infile=infile, colors=colors)

    # Invert colors
    if invert:
        cmd += "-negate "

    cmd += "pgm:-"

    # Log cmd
    sys.stderr.write(f'{cmd}\n')

    # Execute and return bytes
    convert_output = subprocess.check_output(['/bin/sh', '-c', cmd])

    # Parse data where convert output looks like:
    #   P5
    #   <width> <height>
    #   255
    #   <pixel-data>
    _, dims, _, pixels = convert_output.split(b'\n')

    # Get image dimensions
    width, height = map(int, dims.split())

    # Check that dimensions match pixel count
    if width * height != len(pixels):
        raise ValueError(
            f'Inconsistent pixel count ({len(pixels)} bytes) and dimensions '
            f'({width}x{height})')

    # Convert pixels to string
    str_pixels = str.join('', [str(x) for x in pixels])

    # Get sorted set of colors found in image
    # colors = sorted(set(pixels))
    # Convert colors
    # if len(colors) == 1:
    #     new_colors = GRAYSCALE[:1]
    # elif len(colors) == 2:
    #     new_colors = GRAYSCALE[:2]
    # elif len(colors) == 3:
    #     new_colors = GRAYSCALE[1:4]
    # elif len(colors) == 4:
    #     new_colors = GRAYSCALE
    # else:
    #     new_colors = GRAYSCALE + [BLACK] * (len(colors) - 4)
    # colormap = dict(zip(colors, new_colors))
    # str_pixels = str.join('', [colormap[x] for x in pixels])

    padding = ''
    mod = (BYTE // BPP) * ALIGNMENT
    if width % mod:
        padding = 'F' * (mod - width % mod)

    aligned_pixels = bytes.fromhex(str.join('', [
        str_pixels[i:i + width] + padding
        for i in range(0, len(str_pixels), width)
    ][::-1]))

    header = get_header(aligned_pixels, width, height)

    return header + aligned_pixels


def get_header(pixels, width, height):
    """
    Get bitmap header

    :param str pixels: image pixel data
    :param int width: image width
    :param int height: image height
    :return str: bitmap header
    """
    size = len(pixels) // (BYTE // BPP) + BMP_HEADER_SIZE
    header = str.join('', BMP_HEADER.split()) % (
        int.to_bytes(size, 4, 'little').hex(),
        int.to_bytes(width, 4, 'little').hex(),
        int.to_bytes(height, 4, 'little').hex(),
    )
    return bytes.fromhex(header)


def parse_args():
    """
    Parse CLI args.
    """
    parser = argparse.ArgumentParser(description='Convert image to grayscale.')
    parser.add_argument(
        'INFILE',
        default='-',
        help="Name of input file to read (default is /dev/stdin)",
        nargs='?',
    )
    parser.add_argument(
        'OUTFILE',
        default='-',
        help="Name of output file to write (default is /dev/stdout)",
        nargs='?',
    )
    parser.add_argument(
        '-c', '--colors',
        choices=[2, 4],
        default=2,
        help='Number of colors {2, 4}',
        type=int,
    )
    parser.add_argument(
        '-i', '--invert',
        action='store_true',
        help='Invert colors',
    )
    return parser.parse_args()


def main():
    """
    Main entrypoint.
    """
    # Parse CLI args
    args = parse_args()
    infile = args.INFILE if args.INFILE != '-' else '/dev/stdin'
    outfile = args.OUTFILE if args.OUTFILE != '-' else '/dev/stdout'
    colors = args.colors
    invert = args.invert

    # Get bytes to write
    grayscale = to_grayscale(infile, colors, invert)

    # Write bytes
    with open(outfile, 'wb') as stream:
        stream.write(grayscale)


if __name__ == '__main__':
    main()
