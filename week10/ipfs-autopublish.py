#!/usr/bin/env python3
"""
Watch a folder for changes and automatically publish it to IPFS.

Usage:
    python ipfs-autopublish.py ~/my-knowledge-base
    python ipfs-autopublish.py ~/my-knowledge-base --ipns
"""

import argparse
import os
import subprocess
import sys
import threading
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

GATEWAY_URL = "https://ipfs.io/ipfs"


class DebouncedHandler(FileSystemEventHandler):
    def __init__(self, folder, publish_ipns=False):
        super().__init__()
        self.folder = folder
        self.publish_ipns = publish_ipns
        self._timer = None
        self._lock = threading.Lock()

    def on_any_event(self, event):
        # ignore hidden files / dirs
        if any(part.startswith(".") for part in event.src_path.split(os.sep)):
            return

        print(f"  change detected: {event.src_path}")

        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(2.0, self._publish)
            self._timer.start()

    def _publish(self):
        print(f"\nadding folder to IPFS: {self.folder}")
        try:
            result = subprocess.run(
                ["ipfs", "add", "-r", "-Q", self.folder],
                capture_output=True, text=True, check=True,
            )
        except FileNotFoundError:
            print("error: 'ipfs' command not found. Is IPFS installed and on your PATH?")
            return
        except subprocess.CalledProcessError as e:
            print(f"error running ipfs add: {e.stderr.strip()}")
            return

        cid = result.stdout.strip()
        print(f"folder CID: {cid}")
        print(f"gateway URL: {GATEWAY_URL}/{cid}")

        if self.publish_ipns:
            print("publishing to IPNS...")
            try:
                result = subprocess.run(
                    ["ipfs", "name", "publish", cid],
                    capture_output=True, text=True, check=True,
                )
                print(result.stdout.strip())
            except subprocess.CalledProcessError as e:
                print(f"error running ipfs name publish: {e.stderr.strip()}")

        print("\nwatching for changes...")


def main():
    parser = argparse.ArgumentParser(
        description="Watch a folder and auto-publish it to IPFS on changes."
    )
    parser.add_argument("folder", help="path to the folder to watch and publish")
    parser.add_argument(
        "--ipns", action="store_true",
        help="also publish the CID to IPNS after each add",
    )
    args = parser.parse_args()

    folder = os.path.abspath(args.folder)
    if not os.path.isdir(folder):
        print(f"error: '{folder}' is not a directory")
        sys.exit(1)

    print(f"watching: {folder}")
    if args.ipns:
        print("IPNS publishing: enabled")
    print("waiting for changes...\n")

    handler = DebouncedHandler(folder, publish_ipns=args.ipns)
    observer = Observer()
    observer.schedule(handler, folder, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nstopping...")
        observer.stop()

    observer.join()
    print("done.")


if __name__ == "__main__":
    main()
