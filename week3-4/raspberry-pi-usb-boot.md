# Raspberry Pi: Booting from a USB Drive

Instead of running the OS from a microSD card, you can flash Raspberry Pi OS directly to a USB thumb drive and boot from it. This is faster and more reliable than SD cards, which wear out over time.

## What you need

- Raspberry Pi 4 or 5 (older models don't reliably support USB boot)
- USB thumb drive (32GB or larger)
- Another computer (Mac/Windows/Linux) to flash the image
- A monitor + keyboard connected to the Pi, or SSH access

## 1. Flash Raspberry Pi OS to the USB drive

On your computer (not the Pi):

1. Download and install **Raspberry Pi Imager** from [raspberrypi.com/software](https://www.raspberrypi.com/software/)
2. Insert the USB thumb drive into your computer
3. Open Raspberry Pi Imager
4. Click **Choose Device** — select your Pi model
5. Click **Choose OS** — pick **Raspberry Pi OS** (Lite for headless, Desktop for GUI)
6. Click **Choose Storage** — select your USB thumb drive (**be careful not to pick the wrong disk!**)
7. Click **Next** — it will ask if you want to customize settings. Click **Edit Settings** to:
   - Set hostname, username, and password
   - Configure WiFi
   - Enable SSH
8. Click **Save**, then **Yes** to apply the settings, and **Yes** to confirm writing (this erases the drive)
9. Wait for it to finish writing and verifying

## 2. Enable USB boot on the Pi

If your Pi has never booted from USB before, you need to enable it once. You'll need an SD card with Raspberry Pi OS for this one-time setup.

### Pi 5

USB boot is enabled by default. You can skip this step.

### Pi 4

Option A — using `raspi-config`:

```bash
sudo raspi-config
```

Go to **Advanced Options** → **Boot Order** → select **USB Boot**. Then finish and reboot.

Option B — editing the bootloader config directly:

```bash
sudo -E rpi-eeprom-config --edit
```

Change the `BOOT_ORDER` line to:

```
BOOT_ORDER=0xf41
```

This tells the Pi to try USB first, then fall back to SD card. Save and reboot.

## 3. Boot from USB

1. Shut down the Pi
2. Remove the SD card
3. Insert the flashed USB thumb drive
4. Power on the Pi

It should boot from the USB drive. To verify:

```bash
lsblk
```

The root filesystem (`/`) should be on `/dev/sda2` rather than `/dev/mmcblk0p2`.

## Tips

- **Speed matters**: Use a USB 3.0 thumb drive plugged into the Pi's USB 3.0 port (the blue ones) for the best performance. This will be noticeably faster than a microSD card.
- **Not all thumb drives work**: Some cheap or old USB drives have compatibility issues with Pi USB boot. If it doesn't boot, try a different drive.
- **Fallback boot order**: With `BOOT_ORDER=0xf41`, the Pi tries USB first, then falls back to SD card if no bootable USB is found. This is a good default to set.
- **No SD card needed after setup**: Once USB boot is enabled in the bootloader, you don't need an SD card at all — the Pi boots entirely from USB.
- **SD card for storage**: Your existing notes on [using a USB drive for storage](raspberry-pi-usb-storage.md) cover the alternative approach where the OS stays on the SD card and you use USB for data. Both setups are valid — USB boot is simpler (one device), while SD + USB gives you a separation between OS and data.
