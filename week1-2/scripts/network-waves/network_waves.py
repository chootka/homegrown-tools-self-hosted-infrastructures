#!/usr/bin/env python3
"""
Network Waves
Every device on your WiFi network becomes a wave source.
The waves overlap and interfere to create a unique pattern.
Different network = different art.

Press Ctrl+C to quit.
"""

import subprocess
import math
import random
import os
import time
import sys

# ---- Step 1: Scan the local network ----
# arp -a lists all devices your computer knows about on the network
result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
devices = [line for line in result.stdout.strip().split("\n") if line]

print(f"\n  Found {len(devices)} devices on your network.\n")
time.sleep(1)

# ---- Step 2: Turn each device into a wave source ----
# We use each device's info (IP, MAC address) as a random seed
# so the same device always produces the same wave
sources = []
for device in devices:
    random.seed(device)
    sources.append({
        "x": random.random(),         # position on screen (0 to 1)
        "y": random.random(),
        "freq": random.uniform(5, 20), # wave frequency
        "phase": random.uniform(0, math.pi * 2),
    })

# ---- Step 3: Set up the canvas ----
try:
    width, height = os.get_terminal_size()
except OSError:
    width, height = 80, 24  # fallback
height -= 1  # leave room at the bottom

# Characters from dark to bright
shades = " .:-=+*#%@"

# Terminal colors (ANSI escape codes)
colors = [
    "\033[91m",  # red
    "\033[92m",  # green
    "\033[93m",  # yellow
    "\033[94m",  # blue
    "\033[95m",  # magenta
    "\033[96m",  # cyan
]
reset = "\033[0m"
hide_cursor = "\033[?25l"
show_cursor = "\033[?25h"

n = max(len(sources), 1)
frame = 0

# ---- Step 4: Animate the interference pattern ----
# Each line prints immediately so you see it drawing in real time
try:
    print(hide_cursor)  # hide the blinking cursor
    while True:
        # Move cursor to top-left instead of clearing (less flicker)
        sys.stdout.write("\033[H")

        for y in range(height):
            line = ""
            for x in range(width):
                # Normalize x,y to 0-1 range
                nx = x / width
                ny = y / height

                # Add up waves from every device
                total = 0
                strongest = 0
                strongest_val = 0

                for i, src in enumerate(sources):
                    # Distance from this pixel to the wave source
                    dist = math.sqrt((nx - src["x"]) ** 2 + (ny - src["y"]) ** 2)
                    # The wave: a sine ripple spreading out from the source
                    # 'frame' makes it animate over time
                    wave = math.sin(dist * src["freq"] * math.pi * 2 + src["phase"] + frame * 0.1)
                    total += wave
                    # Track which device has the strongest signal here
                    if abs(wave) > strongest_val:
                        strongest_val = abs(wave)
                        strongest = i

                # Map the combined wave value to a character
                brightness = (total / n + 1) / 2
                char = shades[int(brightness * (len(shades) - 1))]

                # Color based on the dominant device at this pixel
                color = colors[strongest % len(colors)]
                line += color + char + reset

            # Print each line immediately as it's computed
            sys.stdout.write(line + "\n")
            sys.stdout.flush()

        frame += 1

except KeyboardInterrupt:
    # Clean exit on Ctrl+C
    print(show_cursor + reset)
    print("\n  Goodbye!")
