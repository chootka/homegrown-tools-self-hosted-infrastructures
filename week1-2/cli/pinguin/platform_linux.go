//go:build linux

package main

import (
	"os/exec"
	"regexp"
	"strings"
)

// ipNeighRegex matches lines from `ip neigh` output:
//   192.168.0.1 dev eth0 lladdr 78:6a:1f:4d:ec:ab REACHABLE
var ipNeighRegex = regexp.MustCompile(
	`^(\d+\.\d+\.\d+\.\d+)\s+dev\s+\S+\s+lladdr\s+([0-9a-fA-F:]+)`,
)

// arpLinuxRegex matches lines from `arp -a` output on Linux:
//   router (192.168.0.1) at 78:6a:1f:4d:ec:ab [ether] on eth0
var arpLinuxRegex = regexp.MustCompile(
	`^(\S+)\s+\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]+)`,
)

func parseARP() ([]Device, error) {
	// Try `ip neigh` first (modern Linux)
	devices, err := parseIPNeigh()
	if err == nil && len(devices) > 0 {
		return devices, nil
	}

	// Fall back to `arp -a`
	return parseArpCommand()
}

func parseIPNeigh() ([]Device, error) {
	out, err := exec.Command("ip", "neigh").Output()
	if err != nil {
		return nil, err
	}

	var devices []Device
	for _, line := range strings.Split(string(out), "\n") {
		matches := ipNeighRegex.FindStringSubmatch(line)
		if matches == nil {
			continue
		}

		devices = append(devices, Device{
			IP:  matches[1],
			MAC: normalizeMAC(matches[2]),
		})
	}

	return devices, nil
}

func parseArpCommand() ([]Device, error) {
	out, err := exec.Command("arp", "-a").Output()
	if err != nil {
		return nil, err
	}

	var devices []Device
	for _, line := range strings.Split(string(out), "\n") {
		matches := arpLinuxRegex.FindStringSubmatch(line)
		if matches == nil {
			continue
		}

		hostname := matches[1]
		if hostname == "?" {
			hostname = ""
		}

		devices = append(devices, Device{
			IP:       matches[2],
			MAC:      normalizeMAC(matches[3]),
			Hostname: hostname,
		})
	}

	return devices, nil
}
