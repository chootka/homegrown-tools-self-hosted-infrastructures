# Raspberry Pi: Using an External USB Hard Drive for Storage

In this setup, the OS lives on the microSD card (Raspbian/Raspberry Pi OS, boot files, system packages), and the USB drive is used for file storage.

## 1. Connect and identify the drive

Plug in the USB drive, then find it:

```bash
lsblk
# or
sudo fdisk -l
```

It will typically show up as `/dev/sda` (with partitions like `/dev/sda1`).

## 2. (Optional) Format the drive

If you need to format it:

```bash
# Create a partition
sudo fdisk /dev/sda
# Then: n (new), p (primary), 1, Enter, Enter, w (write)

# Format as ext4
sudo mkfs.ext4 /dev/sda1
```

## 3. Create a mount point and mount

```bash
sudo mkdir -p /mnt/usbdrive
sudo mount /dev/sda1 /mnt/usbdrive
```

## 4. Auto-mount on boot

Get the drive's UUID:

```bash
sudo blkid /dev/sda1
```

Then add an entry to `/etc/fstab`:

```
UUID=your-uuid-here  /mnt/usbdrive  ext4  defaults,nofail  0  2
```

The `nofail` option prevents boot failure if the drive isn't connected.

Run `sudo mount -a` after editing fstab to verify there are no errors before rebooting.

## 5. Set permissions

```bash
sudo chown pi:pi /mnt/usbdrive
```

## Tips

- **Powered hub**: If the drive is bus-powered and the Pi can't supply enough current (common on Pi 3 and older), use a powered USB hub.
- **NTFS/exFAT**: If you need to keep NTFS or exFAT format (e.g., for Windows compatibility), install the appropriate driver:
  ```bash
  sudo apt install ntfs-3g    # for NTFS
  sudo apt install exfat-fuse  # for exFAT
  ```
- **SD card wear**: SD cards have limited write cycles. If you have write-heavy workloads (databases, logging, torrents, etc.), pointing those to the USB drive helps extend the SD card's life.
- **Moving directories**: You can symlink directories like `/home` or `/var` to the external drive so apps naturally write there instead of the SD card.
- **Booting from USB**: If you want to skip the SD card entirely, newer Pi models (Pi 4, Pi 5) support booting directly from USB. This requires enabling USB boot in the bootloader config with `raspi-config` or `rpi-eeprom-config`. But the SD + USB combo is simpler and works great for most use cases.
