# Week 10: IPFS, Content Addressing, and Local-First Knowledge

## What We're Doing

Building a personal knowledge base that doesn't depend on any cloud service. We'll use Obsidian for writing and organizing, and IPFS for publishing and sharing all from your Raspberry Pi.

By the end of this session you'll have:
- A personal knowledge base in Obsidian
- Content published and accessible via IPFS
- An understanding of how content addressing works
- A workflow for syncing and sharing without centralized platforms

---

## Core Concepts (30 min)

### What is Decentralization?

```
Centralized:
  You → Google Drive → your files
  You → Notion → your notes
  You → Dropbox → your documents

  Problem: They own the server. They can shut down, change terms,
  read your data, charge you more, or disappear.

Decentralized:
  You → your Pi → IPFS network → anyone can access
  You → your Pi → Obsidian vault → your files, your rules

  No single point of failure. No one controls your content.
```

### What is IPFS?

IPFS (InterPlanetary File System) is a peer-to-peer protocol for storing and sharing files. Instead of asking a server "give me the file at this URL," you ask the network "give me the file with this content hash."

```
Traditional web (location-based):
  https://example.com/my-document.pdf
  → "Go to this server, at this path"
  → If the server goes down, the file is gone

IPFS (content-based):
  ipfs://QmT78zSuBmuS4z925WZfrqQ1qHaJ56DQaTfyMUF7F8ff5o
  → "Give me the file with this fingerprint"
  → Anyone who has the file can serve it
  → The hash IS the address — if the content changes, the hash changes
```

### Content Addressing

Every file on IPFS gets a unique hash (called a CID — Content Identifier) based on its contents:

```
"Hello World" → QmWATWQ7fVPP2EFGu71UkfnqhYXDYH566qy47CnJDgvs8u
"Hello World!" → QmfM2r8seH2GiRaC4esTjeraXEachRt8ZsSeGaWTPLyMoG  ← different!
```

Same content = same hash, always. Different content = different hash. This means:
- You can verify a file hasn't been tampered with
- Duplicate files are automatically deduplicated
- The address tells you nothing about where the file is — just what it is

### Pinning and Persistence

IPFS is not permanent storage by default. Files are cached temporarily by nodes that access them, but they can be garbage collected. To keep content available:

- **Pin locally** — tell your IPFS node to keep specific files: `ipfs pin add <CID>`
- **Pin remotely** — use a pinning service (Pinata, web3.storage) to keep files available even when your Pi is off
- **Multiple pins** — the more nodes that pin your content, the more resilient it is

```
No pin:
  You add a file → your node has it → other nodes cache it temporarily
  → eventually garbage collected → gone

Pinned:
  You add a file → you pin it → your node keeps it forever (until you unpin)
  → anyone can still access it as long as your node is online

Multiple pins:
  You pin it + a friend pins it + a pinning service pins it
  → available even if any one node goes offline
```

### Local-First Philosophy

Local-first means:
1. Your data lives on YOUR device first
2. It works offline — no internet required to read/write
3. Sync is optional and on your terms
4. No account, no subscription, no terms of service
5. You can share when you choose to, not because a service forces you

Obsidian + IPFS embodies this: write locally in Obsidian, publish when ready via IPFS.

---

## Part 1: Install IPFS on Your Pi (30 min)

### 1. Download and install Kubo (the IPFS implementation)

```bash
wget https://dist.ipfs.tech/kubo/v0.32.1/kubo_v0.40.1_linux-arm64.tar.gz
tar xvfz kubo_v0.40.1_linux-arm64.tar.gz
cd kubo
sudo bash install.sh
```

Verify:

```bash
ipfs --version
```

**Before moving on, confirm:** `ipfs --version` shows a version number.

### 2. Initialize your IPFS node

```bash
ipfs init
```

This creates your node's identity and a local repository at `~/.ipfs/`.

### 3. Start the IPFS daemon

```bash
ipfs daemon &
```

This connects your Pi to the IPFS network. Leave it running.

If you get an error like `address already in use` on port 5001, another service is using that port. Change the IPFS API port:

```bash
ipfs config Addresses.API /ip4/127.0.0.1/tcp/5003
ipfs daemon &
```

**Before moving on, confirm:** You see "Daemon is ready" in the output.

### 4. Test it — add a file

```bash
echo "Hello from my Pi" > hello.txt
ipfs add hello.txt
```

You'll see output like:

```
added QmXgZAUWd8yo4tvjBETnzRg328i1YsLYHGkGKtHr1RZqK8 hello.txt
```

That hash (CID) is your file's address on IPFS. Anyone on the network can access it:

```bash
ipfs cat QmXgZAUWd8yo4tvjBETnzRg328i1YsLYHGkGKtHr1RZqK8
```

### 5. Access it from a gateway

Open this in a browser (replace the CID with yours):

```
https://ipfs.io/ipfs/QmXgZAUWd8yo4tvjBETnzRg328i1YsLYHGkGKtHr1RZqK8
```

Your file is now accessible to anyone on the internet — served from your Pi via the IPFS network.

### How does this work?

Right now, your Pi is the only node that has this file. When someone opens the gateway link:

1. The `ipfs.io` gateway asks the IPFS network "who has this CID?"
2. Your Pi's IPFS daemon responds "I have it"
3. The gateway fetches the content directly from your Pi and serves it to the browser
4. The gateway may cache it temporarily

```
Browser → ipfs.io gateway → "who has QmXYZ?" → IPFS network → your Pi
                                                                  │
                                          your Pi sends the file ◄┘
                                                  │
                              gateway serves it ◄──┘
                                      │
                      browser shows it ◄┘
```

If you stopped your IPFS daemon right now, the file would become unavailable (unless the gateway cached it). That's why pinning and having multiple nodes matters — if you want content to survive your Pi going offline, other nodes need to pin it too.

### 6. Pin it

```bash
ipfs pin add QmXgZAUWd8yo4tvjBETnzRg328i1YsLYHGkGKtHr1RZqK8
```

This tells your node to keep this file permanently (until you unpin it).

List your pinned content:

```bash
ipfs pin ls --type=recursive
```

---

## Part 2: Obsidian for Knowledge Management (30 min)

### What is Obsidian?

Obsidian is a note-taking app that stores everything as plain Markdown files in a folder on your computer. No cloud account required. No proprietary format. Just `.md` files you own.

### 7. Install Obsidian

On your laptop (not the Pi):
- Download from https://obsidian.md
- Install and open it

### 8. Create a vault

A vault is just a folder. Create one:

1. Open Obsidian → "Create new vault"
2. Name it something like `my-knowledge-base`
3. Choose a location on your laptop

### 9. Write some notes

Create a few notes to work with. For example:

**`ipfs-notes.md`:**
```markdown
# IPFS Notes

IPFS uses content addressing instead of location addressing.
Every file gets a unique hash (CID) based on its contents.
Same content = same hash, always.

## Key Commands
- `ipfs add <file>` — add a file to IPFS
- `ipfs cat <CID>` — retrieve a file by its hash
- `ipfs pin add <CID>` — pin a file so it's kept permanently
```

**`decentralization.md`:**
```markdown
# Decentralization

The idea that no single entity controls the system.
Instead of one server holding everything, many peers share the load.

Related: [[ipfs-notes]], [[local-first]]
```

**`local-first.md`:**
```markdown
# Local-First

Your data lives on your device first.
It works offline. Sync is optional.
No account, no subscription, no terms of service.
```

Notice the `[[double brackets]]` — that's how Obsidian links notes together. This creates a knowledge graph.

### 10. Explore the graph view

In Obsidian, click the graph icon (or press `Ctrl+G` / `Cmd+G`). You'll see your notes as nodes and their links as connections. This is your personal knowledge graph — entirely local.

---

## Part 3: Publish Your Knowledge Base via IPFS (45 min)

### 11. Copy your vault to the Pi

From your laptop, copy your Obsidian vault to the Pi:

```bash
scp -r ~/path/to/my-knowledge-base username@your-pi-address:~/my-knowledge-base
```

Or create the files directly on the Pi:

```bash
mkdir ~/my-knowledge-base

echo '# IPFS Notes

IPFS uses content addressing instead of location addressing.
Every file gets a unique hash (CID) based on its contents.
Same content = same hash, always.' > ~/my-knowledge-base/ipfs-notes.md

echo '# Local-First

Your data lives on your device first.
It works offline. Sync is optional.
No account, no subscription, no terms of service.' > ~/my-knowledge-base/local-first.md
```

### 12. Add the entire folder to IPFS

On the Pi:

```bash
ipfs add -r ~/my-knowledge-base
```

The `-r` flag adds the folder recursively. You'll see each file get its own CID, plus a CID for the entire folder:

```
added QmABC... my-knowledge-base/ipfs-notes.md
added QmDEF... my-knowledge-base/decentralization.md
added QmGHI... my-knowledge-base/local-first.md
added QmXYZ... my-knowledge-base
```

The last CID is the folder — it's a directory you can browse.

### 13. Access your knowledge base via a gateway

Open in a browser:

```
https://ipfs.io/ipfs/<your-folder-CID>
```

You should see a file listing of your vault. Click any `.md` file to view it.

### 14. Pin the folder

```bash
ipfs pin add <your-folder-CID>
```

Now your knowledge base is pinned on your Pi and accessible via IPFS.

### 15. Share it

Give the CID to someone else. They can access your knowledge base from any IPFS gateway or their own IPFS node:

```bash
# On someone else's machine with IPFS:
ipfs cat <your-folder-CID>/ipfs-notes.md
```

No server needed. No URL that can break. Just the content hash.

---

## Part 4: Sync Without Cloud Services (30 min)

### The Problem

Obsidian Sync costs money. Google Drive, Dropbox, iCloud — all centralized. How do you sync between devices without a cloud service?

### Option A: IPFS as a publishing mechanism

This isn't real-time sync, but it's a publish/retrieve workflow:

1. Write notes in Obsidian on your laptop
2. Copy to Pi: `scp -r ~/my-knowledge-base pi:~/my-knowledge-base`
3. Publish to IPFS: `ipfs add -r ~/my-knowledge-base`
4. Share the new CID
5. Someone else retrieves: `ipfs get <CID>`

Every time you update and re-add, you get a new CID (because the content changed). You can use **IPNS** (IPFS Name System) to have a stable address that points to the latest version:

```bash
ipfs name publish <your-folder-CID>
```

This gives you a stable IPNS address (your node's peer ID, like `k51qzi5uqu5d...`) that you can update whenever your content changes. Access it at:

```
https://ipfs.io/ipns/<your-peer-id>
```

The IPNS name stays the same forever — when your content changes, you just run `ipfs name publish <new-CID>` and the same address points to the updated version.

### Making it human-readable with DNSLink

IPNS addresses are long hashes — not easy to remember or share. If you own a domain, you can link it to your IPFS content using a DNS TXT record.

For example, to make your knowledge base available at `notes.yourdomain.com`:

1. First publish to IPNS:
   ```bash
   ipfs name publish <your-folder-CID>
   ```
   Note the peer ID it returns (the `k51...` string).

2. Add a TXT record to your DNS:
   ```
   Host: _dnslink.notes
   Type: TXT
   Value: dnslink=/ipns/<your-peer-id>
   ```

   Or point directly to a CID (no IPNS, but changes every update):
   ```
   Value: dnslink=/ipfs/<your-folder-CID>
   ```

3. Access it via any IPFS gateway:
   ```
   https://ipfs.io/ipns/notes.yourdomain.com
   ```

Now you have a human-readable URL that resolves through IPFS — no server needed, just a DNS record pointing at your content.

```
Traditional:
  notes.example.com → a specific server → serves files

DNSLink + IPFS:
  notes.example.com → DNS TXT record → IPNS peer ID → IPFS network → your Pi serves files
```

This is optional — most students won't have a domain to test with, but it's good to understand how the pieces connect.

### Option B: Syncthing (peer-to-peer sync)

For real-time sync between devices without any cloud:

```bash
sudo apt install syncthing
```

Syncthing syncs folders directly between your devices over the local network (or internet). No server, no account. Your Obsidian vault stays in sync across laptop and Pi automatically.

### Option C: Git

Your vault is just Markdown files — you can use git:

```bash
cd ~/my-knowledge-base
git init
git add .
git commit -m "initial notes"
```

Push to a self-hosted Gitea, or even just sync between devices with `git push`/`pull`.

---

## Discussion (15 min)

### What we built

- A personal knowledge base in Obsidian (plain Markdown, no lock-in)
- Content published on IPFS (content-addressed, decentralized)
- No cloud accounts, no subscriptions, no terms of service
- Accessible to anyone with the CID
- Persistent as long as at least one node pins it

### Content addressing vs location addressing

| | Traditional Web | IPFS |
|---|---|---|
| Address | `https://server.com/file.pdf` | `ipfs://QmABC...` |
| Depends on | A specific server being online | Any node having the content |
| Can break? | Yes — server goes down, link dies | No — hash is permanent |
| Verifiable? | No — server could change the file | Yes — hash proves integrity |
| Censorship | Block the server, block the content | Content lives on many nodes |

### The local-first stack

```
┌────────────────────────────────────────┐
│  Obsidian (writing, thinking, linking) │
│  → Plain Markdown files on YOUR device │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│  IPFS (publishing, sharing)            │
│  → Content-addressed, peer-to-peer     │
│  → No server needed                    │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│  Syncthing / Git (syncing)             │
│  → Device-to-device, no cloud          │
└────────────────────────────────────────┘

Everything runs on hardware you own.
No accounts. No subscriptions. No lock-in.
```

---

## Quick Reference

```
# IPFS Commands
ipfs init                          # Initialize node (once)
ipfs daemon &                      # Start the daemon
ipfs add <file>                    # Add a file, get CID
ipfs add -r <folder>              # Add a folder recursively
ipfs cat <CID>                    # View a file by CID
ipfs get <CID>                    # Download a file/folder by CID
ipfs pin add <CID>                # Pin content (keep permanently)
ipfs pin ls --type=recursive      # List pinned content
ipfs pin rm <CID>                 # Unpin content
ipfs name publish <CID>           # Publish CID to your IPNS name

# Gateway access (browser)
https://ipfs.io/ipfs/<CID>        # Public gateway
http://localhost:8080/ipfs/<CID>  # Your local gateway (if daemon is running)
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `ipfs: command not found` | Re-run the install steps |
| Daemon won't start | Check if another instance is running: `ps aux \| grep ipfs` |
| File not accessible via gateway | Is your daemon running? Is the file pinned? |
| Gateway is slow | Public gateways can be slow — use your local gateway at `localhost:8080` |
| IPNS publish is slow | Normal — IPNS propagation takes 1-2 minutes |
| Can't reach Pi's IPFS from laptop | Check firewall, ports 4001 (swarm) and 8080 (gateway) need to be open |
