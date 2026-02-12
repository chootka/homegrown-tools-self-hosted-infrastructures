package main

import (
	"fmt"
	"strings"
)

// ANSI color codes
const (
	colorReset  = "\033[0m"
	colorGreen  = "\033[32m"
	colorYellow = "\033[33m"
	colorRed    = "\033[31m"
	colorCyan   = "\033[36m"
	colorBold   = "\033[1m"
	colorDim    = "\033[2m"
)

// colorEnabled controls whether ANSI codes are emitted.
var colorEnabled = true

func colorize(color, text string) string {
	if !colorEnabled {
		return text
	}
	return color + text + colorReset
}

func latencyColor(ms float64, timeout bool) string {
	if timeout {
		return colorRed
	}
	if ms < 50 {
		return colorGreen
	}
	if ms < 200 {
		return colorYellow
	}
	return colorRed
}

func printBanner(version string) {
	fmt.Println()
	fmt.Printf("  %s — Local Network Scanner\n", colorize(colorBold+colorCyan, "pinguin "+version))
	fmt.Println()
}

func printScanStart(subnet, iface string) {
	fmt.Printf("  Scanning %s via %s...\n\n", colorize(colorBold, subnet), colorize(colorBold, iface))
}

func printResultsTable(results []PingResult) {
	// Header
	header := fmt.Sprintf("  %-17s %-20s %-22s %s", "IP ADDRESS", "MAC ADDRESS", "HOSTNAME", "LATENCY")
	fmt.Println(colorize(colorBold, header))
	fmt.Printf("  %s\n", strings.Repeat("─", 69))

	var reachable int
	var totalLatency float64

	for _, r := range results {
		ip := fmt.Sprintf("%-17s", r.IP)
		mac := fmt.Sprintf("%-20s", r.MAC)

		hostname := r.Hostname
		if hostname == "" {
			hostname = "—"
		}
		hostname = fmt.Sprintf("%-22s", hostname)

		var latency string
		if r.Timeout {
			latency = colorize(colorRed, "TIMEOUT")
		} else {
			color := latencyColor(r.LatencyMs, false)
			latency = colorize(color, fmt.Sprintf("%.1fms", r.LatencyMs))
			reachable++
			totalLatency += r.LatencyMs
		}

		fmt.Printf("  %s %s %s %s\n", ip, mac, hostname, latency)
	}

	// Summary
	fmt.Println()
	total := len(results)
	summary := fmt.Sprintf("  Summary: %d/%d reachable", reachable, total)
	if reachable > 0 {
		avg := totalLatency / float64(reachable)
		summary += fmt.Sprintf("  |  avg %.1fms", avg)
	}
	fmt.Println(colorize(colorBold, summary))
	fmt.Println()
}
