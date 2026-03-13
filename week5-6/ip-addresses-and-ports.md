# IP Addresses & Ports

## The Analogy

Think of it like an apartment building:

- The **IP address** is the building's street address — it identifies *which computer* on the network
- A **port** is an apartment number — it identifies *which application* on that computer

Every networked computer has one IP address but **65,535 available ports**.

## The Diagram

```
                        ┌─────────────────────────────────────────────┐
                        │                                             │
                        │           YOUR COMPUTER                     │
                        │           IP: 192.168.1.42                  │
                        │                                             │
        ╔═══════════════╪═════════════════════════════════════════════╪══╗
        ║               │          PORTS                              │  ║
        ║               │                                             │  ║
        ║   ┌───────────┴───────────┐                                 │  ║
        ║   │                       │                                 │  ║
        ║   │   :22  ── SSH         │   secure remote terminal access │  ║
        ║   │                       │                                 │  ║
        ║   ├───────────────────────┤                                 │  ║
        ║   │                       │                                 │  ║
        ║   │   :53  ── DNS         │   domain name lookups           │  ║
        ║   │                       │                                 │  ║
        ║   ├───────────────────────┤                                 │  ║
        ║   │                       │                                 │  ║
        ║   │   :80  ── HTTP        │   web traffic (unencrypted)     │  ║
        ║   │                       │                                 │  ║
        ║   ├───────────────────────┤                                 │  ║
        ║   │                       │                                 │  ║
        ║   │   :443 ── HTTPS       │   web traffic (encrypted)      │  ║
        ║   │                       │                                 │  ║
        ║   ├───────────────────────┤                                 │  ║
        ║   │                       │                                 │  ║
        ║   │   :993 ── IMAP        │   receiving email               │  ║
        ║   │                       │                                 │  ║
        ║   ├───────────────────────┤                                 │  ║
        ║   │                       │                                 │  ║
        ║   │   :3000 ── some app    │   could be any application      │  ║
        ║   │                       │                                 │  ║
        ║   ├───────────────────────┤                                 │  ║
        ║   │                       │                                 │  ║
        ║   │   :8080 ── YunoHost   │   admin panel                   │  ║
        ║   │                       │                                 │  ║
        ║   └───────────────────────┘                                 │  ║
        ║                                                             │  ║
        ╚═════════════════════════════════════════════════════════════╪══╝
                                                                      │
                                                                      │
                        to the network ◄──────────────────────────────┘
```

## How It Works Together

When you type `http://192.168.1.42:3000` in a browser, you're saying:

```
  http://  192.168.1.42  :  3000
    │          │            │
    │          │            └── go to port 3000 (some app)
    │          └─────────────── on this computer
    └────────────────────────── using this protocol
```

If you leave out the port, your browser assumes a default:
- `http://` → port **80**
- `https://` → port **443**

## Common Ports to Know

| Port | Service | What it does |
|------|---------|-------------|
| 22   | SSH     | Remote terminal access (encrypted) |
| 25   | SMTP    | Sending email |
| 53   | DNS     | Translating domain names to IP addresses |
| 80   | HTTP    | Web (unencrypted) |
| 443  | HTTPS   | Web (encrypted, the default today) |
| 587  | SMTP    | Sending email (encrypted) |
| 993  | IMAP    | Receiving email (encrypted) |

## Port Ranges

- **0–1023** → "well-known" ports, reserved for standard services (HTTP, SSH, etc.)
- **1024–49151** → registered ports, used by applications like databases, game servers, etc.
- **49152–65535** → ephemeral/dynamic ports, used temporarily by your OS for outgoing connections

## Why This Matters for Self-Hosting

When you self-host services on a Raspberry Pi or server, each application listens on its own port. If you want people outside your local network to reach a service, you need to **open that port** on your router (port forwarding) or use a reverse proxy that routes traffic from ports 80/443 to the right internal port based on the domain name.
