#!/usr/bin/env python3
"""
把本地音频批量上传到 Supabase Storage（替代在网页里一个个拖）。

用法（在你自己电脑的终端里跑）：
    python upload_to_supabase.py \
        --ref     你的项目ref（地址栏 supabase.co/dashboard/project/<ref> 那段） \
        --key     你的 service_role key（Project Settings → API → service_role，注意保密！） \
        --bucket  cet-audio \
        --folder  C:/baidunetdiskdownload \
        --prefix  cet6

说明：
- 会把 folder 里所有 *.mp3 上传到 桶/prefix/文件名，例如 cet-audio/cet6/2017-12-1.mp3
- 需要 Python 3，无需安装任何第三方库（只用标准库）
- service_role key 权限很高，只在本地用、不要提交到代码库
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.request
from pathlib import Path


def upload_one(ref: str, key: str, bucket: str, dest_path: str, file_path: Path) -> None:
    url = f"https://{ref}.supabase.co/storage/v1/object/{bucket}/{dest_path}"
    data = file_path.read_bytes()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("apikey", key)
    req.add_header("Content-Type", "application/octet-stream")
    req.add_header("x-upsert", "true")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            print(f"  OK  {dest_path}  ({len(data)//1024} KB)  -> {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        print(f"  FAIL {dest_path}  -> {e.code} {body[:200]}")
        raise SystemExit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description="上传音频到 Supabase Storage")
    ap.add_argument("--ref", required=True, help="Supabase 项目 ref")
    ap.add_argument("--key", required=True, help="service_role key")
    ap.add_argument("--bucket", default="cet-audio", help="桶名")
    ap.add_argument("--folder", required=True, help="本地音频所在文件夹")
    ap.add_argument("--prefix", default="cet6", help="上传到桶内的前缀文件夹")
    args = ap.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"文件夹不存在：{folder}")
        raise SystemExit(1)

    files = sorted(folder.glob("*.mp3"))
    if not files:
        print("没找到任何 .mp3 文件")
        raise SystemExit(1)

    print(f"找到 {len(files)} 个 mp3，开始上传到 {args.bucket}/{args.prefix}/ ...")
    for f in files:
        dest = f"{args.prefix}/{f.name}"
        upload_one(args.ref, args.key, args.bucket, dest, f)
    print("全部上传完成。")


if __name__ == "__main__":
    main()
