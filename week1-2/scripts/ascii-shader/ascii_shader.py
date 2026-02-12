# Creating Shader Code From Scratch

# Imports
import numpy as np
import os
import keyboard

# Consts
ASCII_LOOKUP = "$@B%8&WM#oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,^'. "
ASCII_LEN    = len(ASCII_LOOKUP)

# Creating the buffer
term_size = os.get_terminal_size()
width     = term_size[0]
height    = term_size[1]
magnitude = np.sqrt(height*height + width*width)
buffer    = np.zeros(shape=(width, height))
pbuffer   = ""

# Main print code
active = True
g_time = 0
while active:
    # Main loop
    if keyboard.is_pressed("esc"):
        active = False

    g_time += 1

    # Entire shader code loop
    pbuffer = ""

    for y in range(height):
        for x in range(width):
            # UVs
            uv            = [float(x/width), float(y/height)]
            # Circle
            circle        = np.sqrt(pow((uv[0]-0.5), 2) + pow((uv[1]-0.5), 2))
            # UV Translate
            m_time        = ((g_time-np.pi/2)*.01)%np.pi
            uv            = [uv[0] + m_time, uv[1] + m_time]
            # Funky distortion
            sinx          = np.sin((uv[0] + g_time*.02)*15)
            siny          = np.sin(uv[1]*15)
            dist          = (sinx*siny)*.1
            uv[0]        += dist
            uv[1]        += dist

            # Rotate
            r             = m_time
            uv[0]         = (np.cos(r) * (uv[0]-.5) + np.sin(r) * (uv[1]-.5) + .5)
            uv[1]         = (np.cos(r) * (uv[1]-.5) - np.sin(r) * (uv[0]-.5) + .5)
            # Main texture
            s             = 15
            tex           = np.abs(np.sin(uv[0]*s))
            buffer[x, y]  = tex

            # Print Related
            cchar         = ASCII_LOOKUP[min(int(buffer[x, y]*ASCII_LEN), ASCII_LEN-1)]
            pbuffer      += cchar

    print(pbuffer)
