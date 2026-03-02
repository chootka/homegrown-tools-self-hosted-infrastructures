# Alternative to Port Forwarding: Fixed IP via VPN (Portunity)

## Why use a VPN instead of port forwarding?

Port forwarding works, but has some common pain points:

- **Double NAT / CGNAT**: Some ISPs use carrier-grade NAT, meaning you don't have a real public IP. Port forwarding on your router won't help.
- **Dynamic IP**: Most home connections change your public IP periodically, requiring dynamic DNS workarounds.
- **ISP restrictions**: Many ISPs block port 25 (email) and other ports on residential connections.
- **Router access**: You may not have admin access to the router (shared housing, university networks, etc.).

A VPN service like **Portunity** gives you a **fixed public IP address** that tunnels directly to your server, bypassing all of these issues. No router configuration needed.

## How it works

1. You subscribe to a VPN tunnel service that provides a **dedicated static IP**.
2. You install a VPN client on your Raspberry Pi (or whatever machine runs YunoHost).
3. The VPN creates a tunnel between your Pi and the VPN provider's server.
4. All traffic to your fixed IP gets routed through the tunnel to your Pi.
5. You point your domain's DNS A record to the fixed IP from the VPN.

```
[Internet] → [Your Fixed IP at VPN Provider] → [VPN Tunnel] → [Your Pi]
```

Your home router doesn't need any port forwarding — traffic arrives via the tunnel.

## Setup with Portunity

Portunity (portunity.de) is a German provider offering VPN tunnels with static IPs, starting at around €1.80/month.

### 1. Register for an account

- Go to [portunity.de](https://www.portunity.de) and sign up for a **vpnTunnel** plan.
- After registration, you'll receive your VPN credentials and a configuration profile (typically an OpenVPN `.ovpn` file or WireGuard config).

### 2. Install the VPN client on your Pi

**For OpenVPN:**

```bash
sudo apt update
sudo apt install openvpn
```

**For WireGuard:**

```bash
sudo apt update
sudo apt install wireguard
```

### 3. Add the VPN configuration

Copy the config file you received from Portunity to your Pi.

**For OpenVPN:**

```bash
# Copy your .ovpn file to the OpenVPN config directory
sudo cp /path/to/portunity.ovpn /etc/openvpn/client/portunity.conf
```

**For WireGuard:**

```bash
# Copy your WireGuard config
sudo cp /path/to/portunity.conf /etc/wireguard/portunity.conf
```

### 4. Start the VPN and enable it on boot

**For OpenVPN:**

```bash
# Start the VPN
sudo systemctl start openvpn-client@portunity

# Enable on boot
sudo systemctl enable openvpn-client@portunity

# Check status
sudo systemctl status openvpn-client@portunity
```

**For WireGuard:**

```bash
# Start the VPN
sudo wg-quick up portunity

# Enable on boot
sudo systemctl enable wg-quick@portunity

# Check status
sudo wg show
```

### 5. Verify your public IP has changed

```bash
curl ifconfig.me
```

This should now show your Portunity fixed IP, not your home IP.

### 6. Point your domain to the fixed IP

Create an A record for your domain pointing to the static IP provided by Portunity. Since it's a fixed IP, no dynamic DNS is needed.

## YunoHost VPN Client App

YunoHost has a dedicated **VPN Client** app that simplifies this process:

1. In the YunoHost admin panel, install the **VPN Client** app.
2. Upload your `.ovpn` or `.cube` config file through the app interface.
3. The app manages the VPN connection and ensures it stays up.

This can be easier than manually managing OpenVPN/WireGuard, and it integrates with YunoHost's diagnostics.

## Troubleshooting

- **VPN connects but services aren't reachable**: Make sure your YunoHost firewall allows traffic on the VPN interface (usually `tun0` for OpenVPN or `portunity` for WireGuard). Check with `sudo yunohost firewall list`.
- **DNS not resolving**: After pointing your domain to the VPN IP, allow time for DNS propagation. Test with `dig yourdomain.com`.
- **VPN drops and doesn't reconnect**: The systemd service should handle reconnection. Check logs with `journalctl -u openvpn-client@portunity` or `journalctl -u wg-quick@portunity`.
- **Slow speeds**: VPN adds some overhead. If performance is an issue, WireGuard is generally faster and lighter than OpenVPN.
