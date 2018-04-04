#!/usr/bin/python

import glob, os
import re

def find_time_millis(content):
    pattern = re.compile(r"Uptime:\s+(\d+)\s+Realtime:\s+(\d+)")
    match = pattern.search(content)
    if match:
        print("time info")
        for i in range(1, 3):
            print(match.group(i))

def find_process_name(content):
    pattern = re.compile(r"MEMINFO in pid\s+(\d+)\s+\[(.+)\]")
    match = pattern.search(content)
    if match:
        print("processes info")
        for i in range(1, 3):
            print(match.group(i))

def find_heap_detail(content, head):
    pattern = re.compile(r""+head+"\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
    match = pattern.search(content)
    if match:
        print(head)
        for i in range(1, 8):
            print(match.group(i))

def find_other_detail(content, head):
    pattern = re.compile(r""+head+"\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
    match = pattern.search(content)
    if match:
        print(head)
        for i in range(1, 5):
            print(match.group(i))



def main():
    os.chdir("files")
    for file in glob.glob("*.txt"):
        f = open(file, 'r')
        lines = f.readlines()
        for line in lines:
            find_time_millis(line)
            find_process_name(line)
            find_heap_detail(line, "Native Heap")
            find_heap_detail(line, "Dalvik Heap")
            find_other_detail(line, "Dalvik Other")
            find_other_detail(line, "Stack")
            find_other_detail(line, "Ashmem")
            find_other_detail(line, "Gfx de")
            find_other_detail(line, "Other dev")
            find_other_detail(line, ".so mmap")
            find_other_detail(line, ".apk mmap")
            find_other_detail(line, ".ttf mmap")
            find_other_detail(line, ".dex mmap")
            find_other_detail(line, ".oat mmap")
            find_other_detail(line, ".art mmap")
            find_other_detail(line, "Other mmap")
            find_other_detail(line, "GL mtrack")
            find_other_detail(line, "Unknown")
            find_heap_detail(line, "TOTAL")


        f.close()


if __name__ == "__main__":
  main()

