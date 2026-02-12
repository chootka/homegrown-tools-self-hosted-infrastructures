package main

import (
	"fmt"
	"net"
	"strings"
)

// Device represents a host found in the ARP table.
type Device struct {
	IP       string
	MAC      string
	Hostname string
}

// PingResult holds the outcome of pinging a single device.
type PingResult struct {
	IP        string
	MAC       string
	Hostname  string
	LatencyMs float64
	Timeout   bool
}

// detectSubnet picks the first non-loopback, up interface that has an IPv4
// address and returns the subnet in CIDR notation plus the interface name.
// If ifaceName is non-empty, only that interface is considered.
func detectSubnet(ifaceName string) (subnet string, iface string, err error) {
	ifaces, err := net.Interfaces()
	if err != nil {
		return "", "", fmt.Errorf("listing interfaces: %w", err)
	}

	for _, i := range ifaces {
		// Skip loopback and down interfaces
		if i.Flags&net.FlagLoopback != 0 || i.Flags&net.FlagUp == 0 {
			continue
		}

		// If user specified an interface, skip others
		if ifaceName != "" && i.Name != ifaceName {
			continue
		}

		addrs, err := i.Addrs()
		if err != nil {
			continue
		}

		for _, addr := range addrs {
			ipNet, ok := addr.(*net.IPNet)
			if !ok {
				continue
			}

			// Only IPv4
			ip4 := ipNet.IP.To4()
			if ip4 == nil {
				continue
			}

			// Skip link-local (169.254.x.x)
			if ip4[0] == 169 && ip4[1] == 254 {
				continue
			}

			// Build CIDR from network address
			ones, _ := ipNet.Mask.Size()
			network := ip4.Mask(ipNet.Mask)
			subnet = fmt.Sprintf("%s/%d", network.String(), ones)
			return subnet, i.Name, nil
		}
	}

	if ifaceName != "" {
		return "", "", fmt.Errorf("interface %q not found or has no IPv4 address", ifaceName)
	}
	return "", "", fmt.Errorf("no suitable network interface found")
}

// discoverDevices calls the platform-specific ARP parser to find local hosts.
func discoverDevices() ([]Device, error) {
	return parseARP()
}

// normalizeMAC lowercases and trims a MAC address string.
func normalizeMAC(mac string) string {
	return strings.ToLower(strings.TrimSpace(mac))
}
