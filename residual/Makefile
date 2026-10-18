PBS_VER=20241016
PBS_PY=3.12.7
GOOS?=darwin
GOARCH?=arm64

fetch-py:
	@case "$(GOOS)-$(GOARCH)" in \
	  darwin-arm64) T=aarch64-apple-darwin ;; \
	  darwin-amd64) T=x86_64-apple-darwin ;; \
	  linux-arm64)  T=aarch64-unknown-linux-gnu ;; \
	  linux-amd64)  T=x86_64-unknown-linux-gnu ;; \
	  windows-amd64) T=x86_64-pc-windows-msvc-shared ;; \
	  *) echo "unsupported $(GOOS)-$(GOARCH)"; exit 1 ;; \
	esac; \
	curl -fsSL -o internal/runtime/python.tar.gz \
	  "https://github.com/astral-sh/python-build-standalone/releases/download/$(PBS_VER)/cpython-$(PBS_PY)+$(PBS_VER)-$$T-install_only.tar.gz"

build:
	go build -trimpath -ldflags="-s -w" -o dist/residual ./cmd/residual

snapshot:
	goreleaser release --snapshot --clean

.PHONY: fetch-py build snapshot
