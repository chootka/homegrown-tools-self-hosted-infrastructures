# Configuring Port Forwarding for YunoHost

YunoHost needs certain ports forwarded from your router to the machine running YunoHost so that external traffic can reach your self-hosted services.

## Required ports

| Port | Protocol | Service |
|------|----------|---------|
| 80   | TCP      | HTTP (web, Let's Encrypt certificate renewal) |
| 443  | TCP      | HTTPS (web apps, admin panel) |
| 22   | TCP      | SSH (remote access) |
| 25   | TCP      | SMTP (incoming email) |
| 587  | TCP      | SMTP submission (outgoing email) |
| 993  | TCP      | IMAP (email clients) |
| 5222 | TCP      | XMPP client (if using XMPP chat) |
| 5269 | TCP      | XMPP server-to-server (if using XMPP chat) |

At minimum, forward **80** and **443** for web services. Add the mail ports if you plan to self-host email, and XMPP ports if you plan to use chat.

## Steps

### 1. Give YunoHost a static IP on your local network

Port forwarding rules point to a specific local IP, so your YunoHost server needs a fixed one.

**Option A — Set it on the server itself:**

Edit `/etc/network/interfaces` or use `nmtui` / `nmcli` to assign a static IP (e.g., `192.168.1.100`).

**Option B — Reserve it on the router (DHCP reservation):**

In your router's admin panel, find the DHCP settings and bind the server's MAC address to a fixed IP. This is often easier and keeps network config centralized.

### 2. Access your router's admin panel

Open a browser and go to your router's gateway address, typically:

- `192.168.1.1`
- `192.168.0.1`
- `10.0.0.1`

You can find it by running:

```bash
ip route | grep default
# or on macOS
netstat -nr | grep default
```

Log in with your router's admin credentials (check the sticker on the router if you haven't changed them).

### 3. Find the port forwarding settings

This varies by router brand, but it's usually under:

- **Port Forwarding**
- **NAT / Virtual Servers**
- **Firewall > Port Forwarding**
- **Advanced > Port Forwarding**

### 4. Create forwarding rules

For each port, create a rule:

- **External/WAN port**: the port number (e.g., 443)
- **Internal/LAN port**: same port number (e.g., 443)
- **Internal IP**: your YunoHost server's static IP (e.g., 192.168.1.100)
- **Protocol**: TCP
- **Enable**: Yes

Some routers let you specify a range (e.g., 80–443) to combine rules.

### 5. Save and test

After saving, verify from outside your network:

```bash
# From another network or a VPS, test if a port is open
nc -zv your-public-ip 443
# or
curl -I https://your-domain.com
```

You can also use an online port checker like `portchecker.co`.

## Getting a domain to point to your home IP

Port forwarding gets traffic to your server, but you also need a domain name pointing to your public IP.

- **Static IP**: Create an A record pointing your domain to your public IP.
- **Dynamic IP** (most home connections): Use a dynamic DNS service (e.g., `noip.com`, `duckdns.org`, or YunoHost's built-in DynDNS at `nohost.me` / `noho.st` / `ynh.fr`). YunoHost can manage this automatically via the admin panel under **Domains > your domain > DNS**.

## Troubleshooting

- **ISP blocking port 25**: Many residential ISPs block inbound port 25 to prevent spam. You may need to call your ISP to unblock it, or use a mail relay service.
- **Double NAT**: If your ISP uses carrier-grade NAT (CGNAT), port forwarding on your router alone won't work. Check by comparing your router's WAN IP with your public IP (from `curl ifconfig.me`). If they differ, contact your ISP to request a public IP or use a tunnel (e.g., Cloudflare Tunnel, WireGuard VPN to a VPS).
- **Firewall on the server**: Make sure the YunoHost server's firewall allows the ports too. YunoHost manages this automatically, but you can check with `sudo yunohost firewall list`.
- **Let's Encrypt failing**: If certificate renewal fails, make sure port 80 is forwarded — Let's Encrypt uses HTTP-01 challenges on port 80.
