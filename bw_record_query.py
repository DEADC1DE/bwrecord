#!/usr/bin/env python3
import os, time

FILE_DN = "/mnt/glftpd/ftp-data/misc/gl_bw_dn.stat"
FILE_UP = "/mnt/glftpd/ftp-data/misc/gl_bw_up.stat"
FILE_TO = "/mnt/glftpd/ftp-data/misc/gl_bw_to.stat"

def read_stat(fp):
    try:
        with open(fp, 'r') as f:
            content = f.read().strip()
        return int(content) if content.isdigit() else 0
    except Exception:
        return 0

def get_timestamp(fp):
    try:
        st = os.stat(fp)
        return time.ctime(st.st_mtime)
    except Exception:
        return "N/A"

up_val = read_stat(FILE_UP)
dn_val = read_stat(FILE_DN)
to_val = read_stat(FILE_TO)
up_ts = get_timestamp(FILE_UP) if os.path.exists(FILE_UP) else "N/A"
dn_ts = get_timestamp(FILE_DN) if os.path.exists(FILE_DN) else "N/A"
to_ts = get_timestamp(FILE_TO) if os.path.exists(FILE_TO) else "N/A"
current_time = time.ctime()

print(f'{current_time} \x037[\x0314BWRECORD\x037] - \x037[\x0314UP\x037]\x030: {up_val/1024:.2f}MB/s (set at: {up_ts})')
print(f'{current_time} \x037[\x0314BWRECORD\x037] - \x037[\x0314DN\x037]\x030: {dn_val/1024:.2f}MB/s (set at: {dn_ts})')
print(f'{current_time} \x037[\x0314BWRECORD\x037] - \x037[\x0314TOTAL\x037]\x030: {to_val/1024:.2f}MB/s (set at: {to_ts})')
