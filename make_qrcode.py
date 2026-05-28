#!/usr/bin/env python3
"""根据公网问卷地址生成二维码 PNG。"""
import argparse
from pathlib import Path

import qrcode


def main() -> None:
    parser = argparse.ArgumentParser(description="生成问卷分享二维码")
    parser.add_argument(
        "url",
        nargs="?",
        default="https://odd-dolls-scream.loca.lt/",
        help="问卷公网地址（建议以 / 结尾，对应 index.html）",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="问卷二维码.png",
        help="输出图片路径",
    )
    args = parser.parse_args()

    qr = qrcode.QRCode(version=None, box_size=10, border=4)
    qr.add_data(args.url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    out = Path(args.output)
    img.save(out)
    print(f"已生成: {out.resolve()}")
    print(f"链接: {args.url}")


if __name__ == "__main__":
    main()
