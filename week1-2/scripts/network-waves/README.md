# network-garden — WiFi Interference Art

A Python script that scans your local network and turns every connected device into a wave source. The waves overlap to create a colorful animated interference pattern in your terminal.

Different WiFi network = different art.

## Usage

```bash
python3 network_waves.py
```

Press `Ctrl+C` to quit.

## What You're Looking At

1. The script runs `arp -a` to discover devices on your WiFi network
2. Each device (phone, laptop, router, smart speaker...) becomes a **wave source** at a unique position
3. The device's MAC address determines its position, frequency, and color, so the same device always produces the same wave
4. Where waves overlap, they **interfere** — adding together or cancelling out, just like ripples in water
5. The combined wave value at each pixel maps to an ASCII character (` .:-=+*#%@`, dark to bright)
6. The color at each pixel comes from whichever device's wave is strongest there
7. A `frame` counter shifts the waves over time, creating animation

## Python Concepts Walkthrough

### 1. `subprocess` — running shell commands from Python

```python
result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
```

`subprocess.run` lets you execute any terminal command and capture its output. `capture_output=True` grabs stdout, and `text=True` gives you a string instead of raw bytes.

### 2. `random.seed()` — deterministic randomness

```python
random.seed(device)
x = random.random()
```

Normally `random` gives different results each time. But if you set a **seed**, you get the same sequence every time. We seed with the device's info string, so each device always gets the same position and frequency.

### 3. ANSI escape codes — terminal colors and cursor control

```python
"\033[91m"   # red text
"\033[H"     # move cursor to top-left
"\033[?25l"  # hide cursor
```

These are special character sequences that terminals interpret as commands. `\033[` starts an escape sequence. This is how command-line programs create colored, animated output without any GUI.

### 4. Trigonometry — `math.sin()` for waves

```python
wave = math.sin(dist * freq * math.pi * 2 + phase + frame * 0.1)
```

Sine waves are the building block of interference patterns. The distance from a source determines the wave's position in its cycle. Adding `frame * 0.1` shifts the wave over time, creating animation.

### 5. Nested loops — pixel-by-pixel rendering

```python
for y in range(height):
    for x in range(width):
        # compute one pixel
```

This is essentially how a GPU shader works — a function that runs for every pixel on screen. Here we do it in Python, which is much slower, but the principle is identical.

## Try It

1. `python3 network_waves.py` — watch the pattern
2. Connect/disconnect a device from WiFi, then restart — the pattern changes
3. Try it on a different network (coffee shop, school, home) — completely different art
4. Modify the `shades` string to change the ASCII characters used
5. Change `frame * 0.1` to `frame * 0.5` for faster animation
6. Add more colors to the `colors` list
