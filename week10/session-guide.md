# Week 10: IPFS, Content Addressing, and Local-First Knowledge

## What We're Doing

Building a personal knowledge base that doesn't depend on any cloud service. We'll use Obsidian for writing and organizing, Syncthing for automatic sync to your Pi, and IPFS for publishing — so every time you save a note, it gets published to the decentralized web automatically.

By the end of this session you'll have:
- A personal knowledge base in Obsidian
- Automatic sync from your laptop to your Pi via Syncthing
- A file watcher that auto-publishes changes to IPFS
- Content accessible to anyone via a content hash

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE FULL PIPELINE                             │
│                                                                 │
│  ┌──────────┐  auto-sync  ┌──────────┐  auto-publish  ┌──────┐│
│  │ Obsidian │ ──────────► │ Your Pi  │ ─────────────► │ IPFS ││
│  │ (laptop) │  Syncthing  │          │  file watcher  │      ││
│  │          │             │          │                │      ││
│  │ Write.   │  no manual  │ Receives │  Detects       │Anyone││
│  │ Save.    │  steps.     │ changes  │  changes,      │can   ││
│  │ Done.    │             │ auto.    │  runs          │access││
│  └──────────┘             └──────────┘  ipfs add -r   └──────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts

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
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Traditional web (location-based):                              │
│                                                                 │
│    https://example.com/my-document.pdf                          │
│    → "Go to THIS SERVER, at THIS PATH"                          │
│    → If the server goes down, the file is gone                  │
│                                                                 │
│  ┌────────┐         request          ┌────────────────┐        │
│  │ You    │ ───────────────────────► │ example.com    │        │
│  │        │ ◄─────────────────────── │ (one server)   │        │
│  └────────┘         response         └────────────────┘        │
│                                       Server dies? File gone.   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  IPFS (content-based):                                          │
│                                                                 │
│    ipfs://QmT78zSuBmuS4z925WZfrq...                             │
│    → "Give me the file with THIS FINGERPRINT"                   │
│    → Anyone who has the file can serve it                       │
│                                                                 │
│  ┌────────┐      "who has QmT78?"     ┌────────┐              │
│  │ You    │ ────────────────────────► │ Node A │ has it!      │
│  │        │                           └────────┘              │
│  │        │ ────────────────────────► ┌────────┐              │
│  │        │ ◄──────────────────────── │ Node B │ also has it! │
│  └────────┘      here's the file      └────────┘              │
│                                       No single point of       │
│                                       failure.                  │
└─────────────────────────────────────────────────────────────────┘
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

```
┌──────────────────────────────────────────────────────────────────┐
│                     CONTENT ADDRESSING                           │
│                                                                  │
│  ┌──────────────┐        hash         ┌────────────────────────┐│
│  │ my-essay.md  │ ──────────────────► │ QmT78zSuBmuS4z925WZ.. ││
│  │ "IPFS is..." │        function     │                        ││
│  └──────────────┘                     │  This IS the address.  ││
│                                       │  It never changes for  ││
│  Same file, same hash.               │  this exact content.   ││
│  Different file, different hash.      └────────────────────────┘│
│                                                                  │
│  ┌──────────────┐        hash         ┌────────────────────────┐│
│  │ my-essay.md  │ ──────────────────► │ QmfM2r8seH2GiRaC4es.. ││
│  │ "IPFS is!!"  │  ← changed a       │                        ││
│  └──────────────┘    character        │  Different content =   ││
│                                       │  completely new hash   ││
│                                       └────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
```

### How Does IPFS Find and Connect to Peers?

Your Pi is probably behind a router on a home or school network. Normally, devices behind a router can't accept incoming connections — that's NAT (Network Address Translation). So how does IPFS work?

IPFS uses several techniques to connect peers:

**1. DHT (Distributed Hash Table)** — a shared directory across the network. When you add a file, your node announces "I have CID QmXYZ..." to the DHT. When someone wants that file, they look it up in the DHT to find which nodes have it.

```
You add a file:
  Your node → tells the DHT → "I have QmXYZ at this address"

Someone requests it:
  Their node → asks the DHT → "Who has QmXYZ?"
  DHT responds → "Node X has it, here's how to reach them"
```

**2. Hole Punching** — when two nodes are both behind NAT, IPFS tries to "punch" through by coordinating via a third node that both can reach. Both nodes send outbound packets at the same time, creating temporary holes in their NAT that allow direct communication.

```
Your Pi (behind NAT) ←──✗──→ Their laptop (behind NAT)
         │                            │
         └──→ Relay node ←──┘
              "Hey, both of you
               send packets NOW"
         │                            │
         └──── hole punched ──────────┘
              direct connection!
```

**3. Relay Nodes** — if hole punching fails, IPFS falls back to relay nodes. These are public IPFS nodes that forward traffic between peers who can't connect directly. It's slower but it works.

```
Your Pi → relay node → their laptop
         (public node forwards traffic)
```

**4. Bootstrap Nodes** — when your IPFS daemon starts, it connects to a set of well-known public nodes (bootstrap nodes) to join the network and discover other peers. These are the entry point into the IPFS swarm.

**In practice, this means:**
- Your Pi doesn't need port forwarding or a VPN
- It doesn't need a public IP address
- It works behind home routers, school networks, coffee shop WiFi
- The IPFS daemon handles all of this automatically when you run `ipfs daemon`
- Port 4001 is used for swarm connections — if your network is very restrictive, IPFS will fall back to relays

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

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUD-FIRST (typical)                     │
│                                                             │
│  You write a note                                           │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────┐     internet      ┌──────────────────┐        │
│  │ Your    │ ────────────────► │  Their Server    │        │
│  │ Device  │ ◄──────────────── │  (Google, Notion)│        │
│  └─────────┘                   └──────────────────┘        │
│                                  │                          │
│  • Need internet to write       │ They store it            │
│  • They own the copy            │ They control access      │
│  • They can read it             │ They can delete it       │
│  • Service shuts down = gone    │ They charge you          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    LOCAL-FIRST (what we do)                  │
│                                                             │
│  You write a note                                           │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────┐                        │
│  │  Your Device                    │                        │
│  │  ┌───────────┐  ┌───────────┐  │                        │
│  │  │ Obsidian  │  │ IPFS node │  │                        │
│  │  │ (write)   │→ │ (publish) │──┼──► share when ready    │
│  │  └───────────┘  └───────────┘  │                        │
│  │                                 │                        │
│  │  Your files. Your rules.       │                        │
│  └─────────────────────────────────┘                        │
│                                                             │
│  • Works offline                                            │
│  • You own every copy                                       │
│  • No one can read it unless you share                      │
│  • No service to shut down                                  │
│  • Free forever                                             │
└─────────────────────────────────────────────────────────────┘
```

Obsidian + Syncthing + IPFS embodies this: write locally in Obsidian, auto-sync to your Pi, auto-publish to the decentralized web.

---

## Part 1: Install IPFS on Your Pi

### 1. Download and install Kubo (the IPFS implementation)

```bash
wget https://dist.ipfs.tech/kubo/v0.40.1/kubo_v0.40.1_linux-arm64.tar.gz
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

## Part 2: Obsidian for Knowledge Management

### What is Obsidian?

Obsidian is a note-taking app that stores everything as plain Markdown files in a folder on your computer. No cloud account required. No proprietary format. Just `.md` files you own.

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR OBSIDIAN VAULT                       │
│                    (just a folder)                           │
│                                                             │
│  my-knowledge-base/                                         │
│  ├── ipfs-notes.md          ← plain text file               │
│  ├── decentralization.md    ← plain text file               │
│  ├── local-first.md         ← plain text file               │
│  └── ...                                                    │
│                                                             │
│  ┌──────────┐      [[link]]      ┌──────────────────┐      │
│  │ ipfs-    │ ◄────────────────► │ decentralization │      │
│  │ notes    │                    │                  │      │
│  └──────────┘                    └────────┬─────────┘      │
│       ▲                                   │                 │
│       │             [[link]]              │                 │
│       │         ┌─────────────────────────┘                 │
│       │         ▼                                           │
│       │    ┌─────────────┐                                  │
│       └───►│ local-first │                                  │
│   [[link]] │             │                                  │
│            └─────────────┘                                  │
│                                                             │
│  Notes link to each other with [[double brackets]].         │
│  Obsidian shows these as a visual graph.                    │
└─────────────────────────────────────────────────────────────┘
```

### 7. Install Obsidian

On your laptop (not the Pi):
- Download from https://obsidian.md (free for personal use, no account needed)
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

## Part 3: Auto-Sync with Syncthing

Syncthing syncs folders directly between devices — no cloud, no account, no server. We'll use it to keep your Obsidian vault in sync between your laptop and Pi automatically.

```
┌─────────────────────────────────────────────────────────────┐
│                    SYNCTHING                                 │
│                                                             │
│  ┌──────────┐                         ┌──────────┐         │
│  │ Laptop   │  ◄─── encrypted ────►   │ Pi       │         │
│  │          │       peer-to-peer      │          │         │
│  │ Obsidian │       sync              │ ~/my-    │         │
│  │ vault    │                         │ knowledge│         │
│  │          │  No cloud. No account.  │ -base    │         │
│  └──────────┘  Just two devices.      └──────────┘         │
│                                                             │
│  Save a file on your laptop → appears on Pi in seconds.    │
└─────────────────────────────────────────────────────────────┘
```

### 11. Install Syncthing on the Pi

```bash
sudo apt install syncthing
```

Start it:

```bash
syncthing --no-browser &
```

Syncthing runs a web UI on port 8384. From your laptop, open an SSH tunnel to access it:

```bash
ssh -L 8384:localhost:8384 username@your-pi-address
```

Then open `http://localhost:8384` in your browser to see the Pi's Syncthing dashboard.

### 12. Install Syncthing on your laptop

- **Mac:** `brew install syncthing` then `syncthing`
- **Windows:** Download from https://syncthing.net
- **Linux:** `sudo apt install syncthing`

Open `http://localhost:8384` (or `http://127.0.0.1:8384`) to see your laptop's Syncthing dashboard.

Note: if your Pi's tunnel is also on port 8384, use a different local port for the tunnel:

```bash
ssh -L 8385:localhost:8384 username@your-pi-address
```

Then the Pi's dashboard is at `http://localhost:8385`.

### 13. Connect the two devices

You need to add Device IDs in **both directions**:

1. On your **Pi's** Syncthing dashboard, go to **Actions → Show ID** and copy the Device ID
2. On your **laptop's** Syncthing dashboard, click **Add Remote Device** and paste the Pi's Device ID. Save.
3. On your **laptop's** Syncthing dashboard, go to **Actions → Show ID** and copy your laptop's Device ID
4. On the **Pi's** Syncthing dashboard, click **Add Remote Device** and paste your laptop's Device ID. Save.

Both sides need to know about each other. After a few seconds, they should show as "Connected" in both dashboards.

**Before moving on, confirm:** Both dashboards show the other device as connected.

### 14. Share your Obsidian vault

1. On your **laptop's** Syncthing dashboard, click **Add Folder**
2. Set the **Folder Path** to your Obsidian vault (e.g. `~/Documents/my-knowledge-base`)
3. Under **Sharing**, check the Pi device — if you don't see it listed, the devices aren't connected yet (go back to step 13)
4. Save
5. On the **Pi's** Syncthing dashboard, you'll see a prompt to accept the shared folder
6. Accept it and set the path to `~/my-knowledge-base`

Now any time you save a note in Obsidian, it automatically syncs to the Pi.

**Before moving on, confirm:** Create or edit a note in Obsidian, then check `ls ~/my-knowledge-base` on the Pi — the file should appear within a few seconds. Syncthing can take 5-10 seconds to sync.

---

## Part 4: Auto-Publish to IPFS

Now we wire up the last piece — a file watcher on the Pi that automatically publishes to IPFS whenever your vault changes.

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTO-PUBLISH PIPELINE                     │
│                                                             │
│  You save a note in Obsidian                                │
│       │                                                     │
│       ▼                                                     │
│  Syncthing syncs to Pi (seconds)                            │
│       │                                                     │
│       ▼                                                     │
│  File watcher detects the change                            │
│       │                                                     │
│       ▼                                                     │
│  ipfs add -r ~/my-knowledge-base                            │
│       │                                                     │
│       ▼                                                     │
│  New CID printed — your content is live on IPFS             │
│                                                             │
│  No manual steps after setup.                               │
└─────────────────────────────────────────────────────────────┘
```

### 15. Set up the auto-publish watcher

On the Pi, if you haven't already, clone the course repo:

```bash
cd ~
git clone https://github.com/chootka/homegrown-tools-self-hosted-infrastructures.git
```

Or if you already have it, pull the latest:

```bash
cd ~/homegrown-tools-self-hosted-infrastructures
git pull
```

Set up and run the watcher:

```bash
cd ~/homegrown-tools-self-hosted-infrastructures/week10
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 ipfs-autopublish.py ~/my-knowledge-base
```

You should see:

```
Watching ~/my-knowledge-base for changes...
```

### 16. Test the full pipeline

1. Open Obsidian on your laptop
2. Edit a note or create a new one
3. Save it
4. Watch the Pi terminal — within a few seconds you should see:
   ```
   Change detected, publishing to IPFS...
   Published: QmNewCID...
   Gateway: https://ipfs.io/ipfs/QmNewCID...
   ```
5. Open the gateway URL in your browser — your updated knowledge base is live

### 17. Optional: Stable address with IPNS

Run the watcher with the `--ipns` flag to also update your IPNS name on each publish:

```bash
python3 ipfs-autopublish.py ~/my-knowledge-base --ipns
```

This gives you a stable address that always points to the latest version. The first IPNS publish takes a minute or two, but after that it's faster.

---

## Part 5: Publish Your Knowledge Base Manually

If you don't want to use Syncthing, you can always do it manually:

### Copy your vault to the Pi

```
┌─────────────────┐                    ┌─────────────────┐
│  YOUR LAPTOP    │     scp -r         │  YOUR PI        │
│                 │ ─────────────────► │                 │
│  Obsidian vault │   (secure copy     │  ~/my-knowledge │
│  ~/my-knowledge │    over SSH)       │  -base/         │
│  -base/         │                    │                 │
│                 │                    │  Then:          │
│  Write here.    │                    │  ipfs add -r    │
│  Edit here.     │                    │  → publish!     │
└─────────────────┘                    └─────────────────┘
```

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

### Add the entire folder to IPFS

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

### Access your knowledge base via a gateway

Open in a browser:

```
https://ipfs.io/ipfs/<your-folder-CID>
```

You should see a file listing of your vault. Click any `.md` file to view it.

### Pin the folder

```bash
ipfs pin add <your-folder-CID>
```

### Share it

Give the CID to someone else. They can access your knowledge base from any IPFS gateway or their own IPFS node:

```bash
# On someone else's machine with IPFS:
ipfs cat <your-folder-CID>/ipfs-notes.md
```

```
┌──────────────────────────────────────────────────────────────┐
│                    SHARING VIA IPFS                           │
│                                                              │
│  You share a CID: QmXYZ...                                  │
│                                                              │
│  ┌─────────┐                           ┌─────────────────┐  │
│  │  Your   │    IPFS network           │  Anyone with    │  │
│  │  Pi     │ ◄───────────────────────► │  the CID        │  │
│  │  (has   │                           │                 │  │
│  │  the    │   "Who has QmXYZ?"        │  Browser:       │  │
│  │  files) │   "I do!" ────────────►   │  ipfs.io/ipfs/  │  │
│  └─────────┘                           │  QmXYZ...       │  │
│                                        │                 │  │
│  ┌─────────┐                           │  CLI:           │  │
│  │ Friend's│   also has the files      │  ipfs cat       │  │
│  │ Pi      │ ◄───────────────────────► │  QmXYZ...       │  │
│  │ (pinned │   "I also have QmXYZ!"   └─────────────────┘  │
│  │  it)    │                                                 │
│  └─────────┘   More pins = more resilient                    │
└──────────────────────────────────────────────────────────────┘
```

No server needed. No URL that can break. Just the content hash.

---

## IPNS and Human-Readable Names

### IPNS (IPFS Name System)

Every time you update and re-add your vault, you get a new CID (because the content changed). IPNS gives you a stable address that you can update to point to the latest version:

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

---

## Discussion

### What we built

```
┌────────────────────────────────────────────────────────────────┐
│                    THE LOCAL-FIRST STACK                        │
│                                                                │
│  ┌────────────────────────────────────────┐                    │
│  │  Obsidian (writing, thinking, linking) │                    │
│  │  → Plain Markdown files on YOUR device │                    │
│  └──────────────────┬─────────────────────┘                    │
│                     │ auto-sync                                │
│                     ▼                                          │
│  ┌────────────────────────────────────────┐                    │
│  │  Syncthing (laptop ↔ Pi)              │                    │
│  │  → Device-to-device, no cloud          │                    │
│  └──────────────────┬─────────────────────┘                    │
│                     │ auto-publish                             │
│                     ▼                                          │
│  ┌────────────────────────────────────────┐                    │
│  │  IPFS (publishing, sharing)            │                    │
│  │  → Content-addressed, peer-to-peer     │                    │
│  │  → No server needed                    │                    │
│  └────────────────────────────────────────┘                    │
│                                                                │
│  Everything runs on hardware you own.                          │
│  No accounts. No subscriptions. No lock-in.                    │
└────────────────────────────────────────────────────────────────┘
```

- A personal knowledge base in Obsidian (plain Markdown, no lock-in)
- Auto-synced to your Pi via Syncthing (no cloud, no account)
- Auto-published to IPFS (content-addressed, decentralized)
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

# Syncthing
syncthing --no-browser &          # Start Syncthing on Pi
ssh -L 8384:localhost:8384 pi     # Tunnel to access Pi's Syncthing UI

# Auto-publish watcher
python3 ipfs-autopublish.py ~/my-knowledge-base         # Watch and publish
python3 ipfs-autopublish.py ~/my-knowledge-base --ipns   # Watch, publish, and update IPNS

# Reset everything (clean slate) — run on the Pi
kill $(pgrep ipfs)
kill $(pgrep syncthing)
rm -rf ~/.ipfs ~/my-knowledge-base ~/hello.txt ~/kubo
rm -rf ~/.local/state/syncthing ~/.config/syncthing
ipfs init
ipfs daemon &

# Reset Syncthing on your laptop
kill $(pgrep syncthing)
rm -rf ~/.local/state/syncthing ~/.config/syncthing
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `ipfs: command not found` | Re-run the install steps |
| Daemon won't start | Check if another instance is running: `ps aux \| grep ipfs` |
| Port 5001 in use | `ipfs config Addresses.API /ip4/127.0.0.1/tcp/5003` |
| File not accessible via gateway | Is your daemon running? Is the file pinned? |
| Gateway is slow | Public gateways can be slow — use your local gateway at `localhost:8080` |
| IPNS publish is slow | Normal — IPNS propagation takes 1-2 minutes |
| Can't reach Pi's IPFS from laptop | Check firewall, ports 4001 (swarm) and 8080 (gateway) need to be open |
| Syncthing devices don't see each other | Make sure both are on the same network, check Device IDs are correct |
| Auto-publish not triggering | Check the watcher is running, check Syncthing is actually syncing |
| Syncthing sync is slow | Normal — it polls every few seconds. Give it 5-10 seconds |
| Pi can't resolve DNS (e.g. `ping google.com` fails but `ping 8.8.8.8` works) | Run: `echo "nameserver 8.8.8.8" \| sudo tee /etc/resolv.conf` |
| Deleted files but gateway still shows them | The gateway cached them. Caches expire eventually. You can't force-delete content from IPFS once others have accessed it — this is a feature of content addressing |
| Obsidian vault deleted but still in Obsidian app | Dismiss the "vault not found" message or remove it from the vault list in Obsidian |
