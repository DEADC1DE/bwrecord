#!/usr/bin/env python3
import time, os, sys

INTERFACES = ["eth0"] # ["eth0", "eth1"] to add more nic´s
FILE_DN = "/mnt/glftpd/ftp-data/misc/gl_bw_dn.stat"
FILE_UP = "/mnt/glftpd/ftp-data/misc/gl_bw_up.stat"
FILE_TO = "/mnt/glftpd/ftp-data/misc/gl_bw_to.stat"
LOG_FILE = "/mnt/glftpd/ftp-data/logs/glftpd.log"

DEBUG = "--debug" in sys.argv
if DEBUG and "--debug" in sys.argv:
    sys.argv.remove("--debug")

def debug_print(msg):
    if DEBUG:
        print(msg)

def read_stat(fp):
    try:
        with open(fp, 'r') as f:
            val = int(f.read().strip())
        debug_print(f"read_stat: {fp} = {val}")
        return val
    except Exception as e:
        debug_print(f"read_stat: Error reading {fp}: {e}")
        return 0

def write_stat(fp, val):
    try:
        with open(fp, 'w') as f:
            f.write(f"{val}\n")
        debug_print(f"write_stat: Set {fp} to {val}")
    except Exception as e:
        debug_print(f"write_stat: Error writing to {fp}: {e}")

def log_record(msg):
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(msg + "\r\n")
        debug_print(f"log_record: {msg}")
    except Exception as e:
        debug_print(f"log_record: Error writing to log file: {e}")

def get_old_timestamp(fp):
    try:
        st = os.stat(fp)
        ts = time.ctime(st.st_mtime)
        debug_print(f"get_old_timestamp: {fp} timestamp is {ts}")
        return ts
    except Exception as e:
        debug_print(f"get_old_timestamp: Error for {fp}: {e}")
        return "N/A"

def read_bytes(stat_type):
    total = 0
    for iface in INTERFACES:
        path = f"/sys/class/net/{iface}/statistics/{stat_type}"
        try:
            with open(path, "r") as f:
                total += int(f.read().strip())
        except Exception as e:
            debug_print(f"read_bytes: Error reading {path}: {e}")
    return total

def get_bw():
    tol_low = 1.99
    tol_high = 2.01
    max_attempts = 3
    for attempt in range(1, max_attempts+1):
        debug_print(f"get_bw: Attempt {attempt}")
        try:
            br1 = read_bytes("rx_bytes")
            bt1 = read_bytes("tx_bytes")
            debug_print(f"get_bw: br1={br1}, bt1={bt1}")
        except Exception as e:
            debug_print(f"get_bw: Error reading initial values: {e}")
            return None, None
        t1 = time.time()
        time.sleep(2)
        t2 = time.time()
        delta = t2 - t1
        debug_print(f"get_bw: Measured duration = {delta:.4f} seconds")
        if tol_low <= delta <= tol_high:
            try:
                br2 = read_bytes("rx_bytes")
                bt2 = read_bytes("tx_bytes")
                debug_print(f"get_bw: br2={br2}, bt2={bt2}")
            except Exception as e:
                debug_print(f"get_bw: Error reading second values: {e}")
                return None, None
            in_kb = ((br2 - br1) / delta) / 1024
            out_kb = ((bt2 - bt1) / delta) / 1024
            debug_print(f"get_bw: in_kb={in_kb:.4f}, out_kb={out_kb:.4f}")
            return int(in_kb), int(out_kb)
        else:
            debug_print(f"get_bw: Time delta out of tolerance: {delta:.4f} seconds")
    debug_print("get_bw: No exact 2-second measurement achieved, measurement discarded")
    return None, None

while True:
    log_ts = time.ctime()
    debug_print(f"Loop: Start time {log_ts}")
    bw_dn = read_stat(FILE_DN)
    bw_up = read_stat(FILE_UP)
    bw_to = read_stat(FILE_TO)
    cu_dn, cu_up = get_bw()
    if (cu_dn, cu_up) == (None, None):
        debug_print("Loop: Invalid measurement, skipping update")
        continue
    if cu_up > bw_up:
        old_ts = get_old_timestamp(FILE_UP) if os.path.exists(FILE_UP) else "N/A"
        write_stat(FILE_UP, cu_up)
        log_line = (f'{log_ts} BWRECORD: "\x037[\x0314BWRECORD\x037] - '
                    f'\x037[\x0314UP\x037]\x030: {cu_up/1024:.2f}MB/s - (old: {bw_up/1024:.2f}MB/s set at: {old_ts})"')
        log_record(log_line)
    if cu_dn > bw_dn:
        old_ts = get_old_timestamp(FILE_DN) if os.path.exists(FILE_DN) else "N/A"
        write_stat(FILE_DN, cu_dn)
        log_line = (f'{log_ts} BWRECORD: "\x037[\x0314BWRECORD\x037] - '
                    f'\x037[\x0314DN\x037]\x030: {cu_dn/1024:.2f}MB/s - (old: {bw_dn/1024:.2f}MB/s set at: {old_ts})"')
        log_record(log_line)
    if (cu_up + cu_dn) > bw_to:
        old_ts = get_old_timestamp(FILE_TO) if os.path.exists(FILE_TO) else "N/A"
        write_stat(FILE_TO, cu_up + cu_dn)
        log_line = (f'{log_ts} BWRECORD: "\x037[\x0314BWRECORD\x037] - '
                    f'\x037[\x0314TOTAL\x037]\x030: {(cu_up+cu_dn)/1024:.2f}MB/s - (old: {bw_to/1024:.2f}MB/s set at: {old_ts})"')
        log_record(log_line)
