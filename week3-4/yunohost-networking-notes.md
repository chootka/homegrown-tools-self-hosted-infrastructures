# YunoHost Networking & the User Portal

## The Two Classroom Topologies

In this class we have two different setups. Understanding which one you're using is key to understanding how your network traffic flows.

---

### Topology A: Pi on the Switch (via Router)

Your Pi is connected via **ethernet to a switch**, which is connected to the **router**. Your laptop connects to the **router's WiFi**. Everything is on the same local network.

```
                        ┌──────────────┐
                        │   INTERNET   │
                        └──────┬───────┘
                               │
                     ┌─────────┴─────────┐
                     │      ROUTER       │
                     │  (public IP:      │
                     │   e.g. 86.5.x.x) │
                     │                   │
                     │  Has WiFi + LAN   │
                     └───┬─────────┬─────┘
                         │         │
                    WiFi │    Eth  │
                         │         │
                   ┌─────┴──┐  ┌───┴───────────┐
                   │ LAPTOP │  │    SWITCH      │
                   │  .102  │  └───┬───────┬────┘
                   └────────┘      │       │
                              ┌────┴─┐ ┌───┴──┐
                              │ Pi A │ │ Pi B │
                              │ .101 │ │ .103 │
                              └──────┘ └──────┘

         All devices are on the SAME local network
                  (e.g. 192.168.1.0/24)

     Laptop (WiFi) ◄──── same subnet ────► Pi (Ethernet)
```

**How it works:** Your laptop and your Pi are both on `192.168.1.x`. When you visit `yourdomain.noho.st`, DNS points to the router's public IP, and the router uses **NAT loopback** to send the request back to your Pi on the LAN. Everything just works.

---

### Topology B: Pi Direct to Laptop (with WiFi Bridge)

Your Pi is connected **directly to your laptop via ethernet**. Your laptop is on **WiFi** and shares its internet connection with the Pi using a **network bridge**.

```
                        ┌──────────────┐
                        │   INTERNET   │
                        └──────┬───────┘
                               │
                     ┌─────────┴─────────┐
                     │      ROUTER       │
                     │  (public IP:      │
                     │   e.g. 86.5.x.x) │
                     └─────────┬─────────┘
                               │ WiFi
                               │
                        ┌──────┴───────┐
                        │    LAPTOP    │
                        │              │
                        │  WiFi ──bridge──► Ethernet │
                        │  (internet)     (to Pi)    │
                        └──────────────┬─────────────┘
                                       │ Ethernet cable
                                       │
                                 ┌─────┴────┐
                                 │    Pi    │
                                 └──────────┘

      The Pi reaches the internet THROUGH the laptop.
      The Pi is NOT directly on the router's network.
```

**How it works:** The laptop acts as a gateway for the Pi. The Pi can reach the internet via the bridge, but the **router doesn't know the Pi exists** — it only sees the laptop. The Pi is on a different subnet (e.g. `10.x.x.x` or `169.254.x.x`) from the router's network.

---

## The Problem: Domain Access in Topology B

YunoHost has two web interfaces:

| Interface | URL | Served when... |
|---|---|---|
| **Admin panel** | `https://<ip>/yunohost/admin` | You access by IP address |
| **User portal (SSO)** | `https://yourdomain.noho.st` | You access by the domain name |

The user portal **only works when you use the domain name**, because nginx uses the domain to decide what to show you.

### Topology A: It Just Works

1. You type `https://yourdomain.noho.st` in your browser.
2. DNS resolves it to the **router's public IP** (e.g. `86.5.x.x`).
3. Your request hits the router.
4. The router uses **NAT loopback (hairpin NAT)** — it recognises this is its own public IP and forwards the request back to the Pi on the LAN.
5. Nginx sees the domain name and serves the **user portal**.

```
Laptop ──WiFi──► Router ──► recognises own IP ──► forwards to Pi ──► User Portal
```

### Topology B: It Breaks

1. You type `https://yourdomain.noho.st` in your browser.
2. DNS resolves it to the **router's public IP** (e.g. `86.5.x.x`).
3. Your request goes out over WiFi to the router's public IP.
4. The router tries to forward it... but the **Pi isn't on the router's network**. It's hanging off your laptop's ethernet port.
5. The request **fails**, times out, or falls back to the admin panel.

```
Laptop ──WiFi──► Router ──► public IP ──► ??? Pi is not here!

Meanwhile, the Pi is right there on your ethernet cable,
but your laptop doesn't know that yourdomain.noho.st = the Pi.
```

---

## The Fix for Topology B: Override DNS Locally

Tell your laptop that `yourdomain.noho.st` points to the Pi's **local ethernet IP** instead of the public IP.

### Step 1: Find the Pi's IP

On the Pi:

```bash
hostname -I
```

Or on your laptop:

```bash
arp -a
```

Look for the IP on the ethernet interface — it could be `169.254.x.x`, `10.x.x.x`, or similar depending on your bridge setup.

### Step 2: Edit Your Hosts File

On your laptop (macOS/Linux):

```bash
sudo nano /etc/hosts
```

Add a line:

```
<pi-ethernet-ip>   yourdomain.noho.st
```

For example:

```
169.254.1.10   eme.noho.st
```

On Windows, the file is at `C:\Windows\System32\drivers\etc\hosts` (edit with Notepad as Administrator).

### Step 3: Access the Portal

Now `https://yourdomain.noho.st` will go directly to the Pi over the ethernet cable. Nginx sees the correct domain name and serves the **user portal**.

### Step 4: Clean Up Later

**Remove the hosts entry** if you move your Pi to the switch/router setup (Topology A), otherwise your laptop will keep trying to reach the Pi locally even when it's elsewhere on the network.

---

## Key Concepts

- **DNS** — translates domain names (like `eme.noho.st`) to IP addresses. YunoHost's `.noho.st` domains point to a public IP.
- **NAT (Network Address Translation)** — the router translates between its public IP and private local IPs.
- **NAT Loopback / Hairpin NAT** — when a device inside the network accesses the router's own public IP, the router is smart enough to send the traffic back inside instead of out to the internet. This is why Topology A works.
- **Network Bridge** — your laptop forwards traffic between its WiFi (internet) and its ethernet (Pi), letting the Pi access the internet through the laptop.
- **Hosts file** — a local file that overrides DNS. Entries here are checked before any internet DNS lookup. This is the fix for Topology B.
- **SSO (Single Sign-On)** — YunoHost's user portal that authenticates users and gives access to installed apps. Only served when accessed via the domain name.
- **Subnet** — a range of IP addresses that form a local network. Devices on the same subnet can talk directly; devices on different subnets need a router between them.
