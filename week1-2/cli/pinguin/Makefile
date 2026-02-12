VERSION ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
LDFLAGS := -ldflags "-s -w -X main.version=$(VERSION)"
DIST    := dist
DEB_TMP := $(DIST)/deb-staging

PLATFORMS := darwin/amd64 darwin/arm64 linux/amd64 linux/arm64

.PHONY: all clean build-all tarballs deb

all: tarballs deb

# Build a single binary for the current platform
build:
	go build $(LDFLAGS) -o $(DIST)/pinguin .

# Cross-compile for all platforms
build-all:
	@for platform in $(PLATFORMS); do \
		os=$${platform%/*}; \
		arch=$${platform#*/}; \
		output=$(DIST)/pinguin-$${os}-$${arch}; \
		echo "Building $$os/$$arch..."; \
		GOOS=$$os GOARCH=$$arch go build $(LDFLAGS) -o $$output . || exit 1; \
	done

# Create tarballs for each platform
tarballs: build-all
	@for platform in $(PLATFORMS); do \
		os=$${platform%/*}; \
		arch=$${platform#*/}; \
		tarname=pinguin-$(VERSION)-$${os}-$${arch}.tar.gz; \
		echo "Packaging $$tarname..."; \
		tar -czf $(DIST)/$$tarname -C $(DIST) pinguin-$${os}-$${arch}; \
	done

# Build .deb packages for linux/amd64 and linux/arm64
deb: build-all
	@for arch in amd64 arm64; do \
		deb_arch=$$arch; \
		staging=$(DEB_TMP)/pinguin-$$arch; \
		echo "Packaging .deb for $$arch..."; \
		mkdir -p $$staging/DEBIAN; \
		mkdir -p $$staging/usr/local/bin; \
		cp $(DIST)/pinguin-linux-$$arch $$staging/usr/local/bin/pinguin; \
		chmod 755 $$staging/usr/local/bin/pinguin; \
		sed "s/{{VERSION}}/$(VERSION)/g; s/{{ARCH}}/$$deb_arch/g" \
			packaging/deb/control > $$staging/DEBIAN/control; \
		dpkg-deb --build $$staging $(DIST)/pinguin_$(VERSION)_$$deb_arch.deb; \
	done

clean:
	rm -rf $(DIST)
