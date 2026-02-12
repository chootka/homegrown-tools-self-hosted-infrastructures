# pinguin

A local network scanner that discovers devices, pings them concurrently, and displays color-coded latency results. Built with Go — zero external dependencies.

```
  pinguin v0.1.0 — Local Network Scanner

  Scanning 192.168.0.0/24 via en0...

  IP ADDRESS       MAC ADDRESS         HOSTNAME              LATENCY
  ─────────────────────────────────────────────────────────────────────
  192.168.0.1      78:6a:1f:4d:ec:ab   router.local          1.2ms
  192.168.0.42     aa:bb:cc:dd:ee:ff   raspberrypi.local     4.8ms
  192.168.0.50     11:22:33:44:55:66   —                     87.3ms
  192.168.0.150    (unknown)           —                     TIMEOUT

  Summary: 3/4 reachable  |  avg 31.1ms
```

## Install

### From source (any platform with Go)

```bash
git clone https://github.com/chootka/pinguin.git
cd pinguin
go build -o pinguin .
./pinguin
```

### Homebrew (macOS)

```bash
brew tap chootka/tools
brew install pinguin
```

### APT (Raspberry Pi / Debian)

```bash
echo "deb [trusted=yes] https://chootka.github.io/pinguin/debs /" | \
  sudo tee /etc/apt/sources.list.d/pinguin.list
sudo apt update
sudo apt install pinguin
```

> **Note:** The APT repo uses `[trusted=yes]` to skip GPG signing. This is fine for personal/educational use but not suitable for production distribution.

## Usage

```bash
pinguin                # scan local network, ping all devices
pinguin -i en0         # use specific network interface
pinguin -t 500         # set ping timeout in milliseconds (default: 1000)
pinguin -no-color      # disable colored output
pinguin -version       # print version
```

## How it works

### 1. Device discovery (ARP table)

Instead of scanning every IP in a subnet (slow, noisy), pinguin reads the operating system's ARP table — a cache of recently-seen IP-to-MAC-address mappings.

- **macOS:** parses `arp -a` output
- **Linux:** parses `ip neigh` output (falls back to `arp -a`)

This is implemented using **build tags** — Go's mechanism for platform-specific code:

```go
//go:build darwin    // platform_darwin.go — only compiled on macOS
//go:build linux     // platform_linux.go  — only compiled on Linux
```

Both files export the same `parseARP()` function with the same signature. The Go compiler picks the right one.

### 2. Concurrent pinging (goroutines)

Each discovered device is pinged in its own **goroutine** (Go's lightweight thread). A **semaphore** (buffered channel) limits concurrency to 50 simultaneous pings to avoid flooding the network:

```go
sem := make(chan struct{}, 50)  // buffered channel = semaphore

for _, device := range devices {
    go func(d Device) {
        sem <- struct{}{}        // acquire slot
        defer func() { <-sem }() // release slot
        // ... ping the device ...
    }(device)
}
```

Pinging uses `os/exec` to call the system `ping` command. This avoids needing root/sudo (raw ICMP sockets require elevated privileges). The `os/exec` pattern is broadly useful — it's how Go programs shell out to other commands.

### 3. Display (ANSI escape codes)

Results are color-coded using ANSI escape codes — special character sequences that terminals interpret as formatting:

| Latency    | Color  | ANSI code   |
|------------|--------|-------------|
| < 50ms     | Green  | `\033[32m`  |
| 50–200ms   | Yellow | `\033[33m`  |
| > 200ms    | Red    | `\033[31m`  |
| Timeout    | Red    | `\033[31m`  |

The `-no-color` flag disables this for piping output or terminals that don't support ANSI.

## Go concepts demonstrated

| Concept | Where | What it teaches |
|---------|-------|-----------------|
| Build tags | `platform_*.go` | Platform-specific code without `if/else` |
| `os/exec` | `ping.go` | Calling external commands from Go |
| Goroutines | `ping.go` | Lightweight concurrency |
| Channels as semaphores | `ping.go` | Bounded concurrency pattern |
| `sync.WaitGroup` | `ping.go` | Waiting for goroutines to finish |
| `net.Interfaces()` | `scanner.go` | Querying network configuration |
| `regexp` | `platform_*.go`, `ping.go` | Parsing unstructured command output |
| `flag` package | `main.go` | CLI argument parsing (stdlib alternative to cobra) |
| `fmt.Fprintf` | `display.go` | Formatted output and ANSI color codes |
| Cross-compilation | `Makefile` | `GOOS`/`GOARCH` environment variables |

## Building & packaging

```bash
# Build for current platform
make build

# Cross-compile for all platforms (darwin/linux × amd64/arm64)
make all

# Output goes to dist/
ls dist/
# pinguin-darwin-amd64  pinguin-linux-arm64  ...
# pinguin-v0.1.0-darwin-amd64.tar.gz  ...
# pinguin_v0.1.0_amd64.deb  ...
```

## Project structure

```
pinguin/
├── main.go                # Entry point — flag parsing, orchestration
├── scanner.go             # Types, subnet detection via net.Interfaces()
├── platform_darwin.go     # macOS ARP table parser (build tag: darwin)
├── platform_linux.go      # Linux ARP table parser (build tag: linux)
├── ping.go                # Concurrent ping via os/exec
├── display.go             # ANSI colors, table formatting
├── Makefile               # Cross-compile, .deb packaging, tarballs
├── packaging/deb/control  # Debian package metadata template
├── homebrew/pinguin.rb    # Homebrew formula
└── .github/workflows/     # CI: build + release + update tap + APT repo
```

## Releasing a new version

1. Tag the commit: `git tag v0.1.0`
2. Push the tag: `git push origin v0.1.0`
3. GitHub Actions will:
   - Build binaries for all 4 platform/arch combinations
   - Create `.tar.gz` tarballs and `.deb` packages
   - Create a GitHub Release with all artifacts
   - Update the Homebrew tap with new checksums
   - Update the APT repository index

## License

MIT
