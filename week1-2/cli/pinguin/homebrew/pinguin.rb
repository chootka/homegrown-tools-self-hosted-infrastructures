class Pinguin < Formula
  desc "Local network scanner with color-coded ping results"
  homepage "https://github.com/chootka/pinguin"
  version "0.1.0"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/chootka/pinguin/releases/download/v#{version}/pinguin-#{version}-darwin-arm64.tar.gz"
      sha256 "PLACEHOLDER_DARWIN_ARM64"
    else
      url "https://github.com/chootka/pinguin/releases/download/v#{version}/pinguin-#{version}-darwin-amd64.tar.gz"
      sha256 "PLACEHOLDER_DARWIN_AMD64"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://github.com/chootka/pinguin/releases/download/v#{version}/pinguin-#{version}-linux-arm64.tar.gz"
      sha256 "PLACEHOLDER_LINUX_ARM64"
    else
      url "https://github.com/chootka/pinguin/releases/download/v#{version}/pinguin-#{version}-linux-amd64.tar.gz"
      sha256 "PLACEHOLDER_LINUX_AMD64"
    end
  end

  def install
    # The tarball contains a single binary named pinguin-OS-ARCH
    # Find it and install as "pinguin"
    binary = Dir.glob("pinguin-*").first || "pinguin"
    bin.install binary => "pinguin"
  end

  test do
    assert_match "pinguin", shell_output("#{bin}/pinguin -version")
  end
end
