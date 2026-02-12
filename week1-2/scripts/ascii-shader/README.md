# ascii-shader — GPU Shader in the Terminal

A Python script that renders an animated shader effect using ASCII characters. Inspired by GPU fragment shaders (like those on ShaderToy), but running entirely in your terminal.

## Setup

```bash
# Install dependencies
pip3 install numpy keyboard
```

## Usage

```bash
# Requires sudo on macOS (the keyboard library needs it to detect key presses)
sudo python3 ascii_shader.py
```

Press `Esc` to quit.

## What You're Looking At

The script treats your terminal like a screen of pixels. For every character position, it:

1. Calculates a **UV coordinate** (normalized x,y from 0 to 1)
2. Translates and distorts the UVs using sine waves
3. Rotates the UVs over time
4. Generates a stripe texture from the distorted coordinates
5. Maps the brightness to an ASCII character (`$@B%8&...` from dark to light)

The result is an animated, wobbly stripe pattern that shifts and rotates — the same kind of math that runs on your graphics card thousands of times per second.

## Python Concepts Walkthrough

### 1. Fragment shader pattern — per-pixel computation

```python
for y in range(height):
    for x in range(width):
        uv = [float(x/width), float(y/height)]
        # ... compute color for this pixel
```

This is the core idea of a **fragment shader**: a function that runs once for every pixel on screen. The UV coordinates normalize the position to a 0–1 range, making the math resolution-independent.

### 2. numpy — fast math

```python
import numpy as np
np.sin(value)
np.abs(value)
np.sqrt(value)
```

NumPy provides math functions that mirror what's available on the GPU. Here we use them per-pixel, but NumPy can also operate on entire arrays at once for massive speedups.

### 3. Time-based animation

```python
g_time += 1
m_time = ((g_time - np.pi/2) * .01) % np.pi
```

The `g_time` counter increments each frame. By feeding it into the math (translation, rotation, distortion), the pattern evolves over time. The `% np.pi` wraps it around so it loops.

### 4. UV distortion — bending space

```python
sinx = np.sin((uv[0] + g_time*.02) * 15)
siny = np.sin(uv[1] * 15)
uv[0] += (sinx * siny) * .1
uv[1] += (sinx * siny) * .1
```

Instead of drawing a straight grid, we offset each pixel's coordinates using sine waves. This creates the wobbly, organic-looking distortion. Multiplying the UV by 15 controls the frequency of the wobble.

### 5. 2D rotation

```python
uv[0] = (np.cos(r) * (uv[0]-.5) + np.sin(r) * (uv[1]-.5) + .5)
uv[1] = (np.cos(r) * (uv[1]-.5) - np.sin(r) * (uv[0]-.5) + .5)
```

This is a standard 2D rotation matrix applied to the UV coordinates. We subtract 0.5 to rotate around the center, apply the rotation, then add 0.5 back.

### 6. ASCII brightness mapping

```python
ASCII_LOOKUP = "$@B%8&WM#oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,^'. "
cchar = ASCII_LOOKUP[int(tex * ASCII_LEN)]
```

Each character has a different visual "density." `$` and `@` look heavy/dark, while `.` and ` ` look light. By mapping a brightness value to this string, we get grayscale rendering using text.

## Try It

1. `sudo python3 ascii_shader.py` — watch the animation
2. Change `s = 15` to `s = 5` — wider stripes
3. Change `*.1` (the distortion amount) to `*.3` — more wobble
4. Replace `np.sin(uv[0]*s)` with `np.sin(uv[0]*s + uv[1]*s)` — diagonal stripes
5. Try a different `ASCII_LOOKUP` string — fewer characters = more contrast

## Note

The `keyboard` library requires root access on macOS to detect key presses globally. If you don't want to use `sudo`, you can replace the keyboard check with a simple frame counter to run for a fixed number of frames instead.
