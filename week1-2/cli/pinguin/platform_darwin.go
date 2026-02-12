//go:build darwin

package main

import (
	"os/exec"
	"regexp"
	"strings"
)

// arpRegex matches lines from macOS `arp -a` output:
//   router.local (192.168.0.1) at 78:6a:1f:4d:ec:ab on en0 ifscope [ethernet]
//   ? (192.168.0.42) at aa:bb:cc:dd:ee:ff on en0 ifscope [ethernet]
var arpRegex = regexp.MustCompile(
	`^(\S+)\s+\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]+)`,
)

func parseARP() ([]Device, error) {
	out, err := exec.Command("arp", "-a").Output()
	if err != nil {
		return nil, err
	}

	var devices []Device
	for _, line := range strings.Split(string(out), "\n") {
		matches := arpRegex.FindStringSubmatch(line)
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
