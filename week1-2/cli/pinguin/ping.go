package main

import (
	"fmt"
	"os/exec"
	"regexp"
	"runtime"
	"strconv"
	"sync"
)

// maxConcurrentPings limits goroutines to avoid flooding the network.
const maxConcurrentPings = 50

// latencyRegex extracts the round-trip time from ping output.
// macOS: "round-trip min/avg/max/stddev = 1.234/1.234/1.234/0.000 ms"
// Linux: "rtt min/avg/max/mdev = 1.234/1.234/1.234/0.000 ms"
var latencyRegex = regexp.MustCompile(`[\d.]+/([\d.]+)/[\d.]+/[\d.]+ ms`)

// pingDevices pings all devices concurrently and returns results.
func pingDevices(devices []Device, timeoutMs int) []PingResult {
	results := make([]PingResult, len(devices))
	sem := make(chan struct{}, maxConcurrentPings)
	var wg sync.WaitGroup

	for i, d := range devices {
		wg.Add(1)
		go func(idx int, dev Device) {
			defer wg.Done()
			sem <- struct{}{}        // acquire
			defer func() { <-sem }() // release

			ms, timeout := pingHost(dev.IP, timeoutMs)
			results[idx] = PingResult{
				IP:        dev.IP,
				MAC:       dev.MAC,
				Hostname:  dev.Hostname,
				LatencyMs: ms,
				Timeout:   timeout,
			}
		}(i, d)
	}

	wg.Wait()
	return results
}

// pingHost sends a single ping and returns latency in ms.
func pingHost(ip string, timeoutMs int) (latencyMs float64, timedOut bool) {
	timeoutSec := fmt.Sprintf("%d", (timeoutMs+999)/1000) // ceiling division to seconds

	var cmd *exec.Cmd
	switch runtime.GOOS {
	case "darwin":
		// macOS ping: -c count, -t timeout (seconds)
		cmd = exec.Command("ping", "-c", "1", "-t", timeoutSec, ip)
	default:
		// Linux ping: -c count, -W timeout (seconds)
		cmd = exec.Command("ping", "-c", "1", "-W", timeoutSec, ip)
	}

	out, err := cmd.Output()
	if err != nil {
		return 0, true
	}

	// Parse latency from ping output
	matches := latencyRegex.FindSubmatch(out)
	if matches == nil {
		return 0, true
	}

	ms, err := strconv.ParseFloat(string(matches[1]), 64)
	if err != nil {
		return 0, true
	}

	return ms, false
}
