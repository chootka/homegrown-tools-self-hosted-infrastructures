package main

import (
	"flag"
	"fmt"
	"os"
)

var version = "dev"

func main() {
	iface := flag.String("i", "", "network interface to use (e.g. en0)")
	timeoutMs := flag.Int("t", 1000, "ping timeout in milliseconds")
	noColor := flag.Bool("no-color", false, "disable colored output")
	showVersion := flag.Bool("version", false, "print version and exit")
	flag.Parse()

	if *showVersion {
		fmt.Printf("pinguin %s\n", version)
		os.Exit(0)
	}

	if *noColor {
		colorEnabled = false
	}

	printBanner(version)

	// Detect local subnet
	subnet, ifaceName, err := detectSubnet(*iface)
	if err != nil {
		fmt.Fprintf(os.Stderr, "  Error: %v\n\n", err)
		os.Exit(1)
	}

	printScanStart(subnet, ifaceName)

	// Discover devices via ARP table
	devices, err := discoverDevices()
	if err != nil {
		fmt.Fprintf(os.Stderr, "  Error discovering devices: %v\n\n", err)
		os.Exit(1)
	}

	if len(devices) == 0 {
		fmt.Println("  No devices found in ARP table.")
		fmt.Println("  Try pinging a known host first to populate the table.")
		fmt.Println()
		os.Exit(0)
	}

	// Ping all discovered devices concurrently
	results := pingDevices(devices, *timeoutMs)

	// Display results
	printResultsTable(results)
}
