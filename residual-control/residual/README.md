# residual

Sovereign intent verification. Single binary. No server. No dashboard. No telemetry.

## Install
    curl -fsSL https://github.com/you/residual/releases/latest/download/install.sh | sh

## Activate
    residual activate <jwt-from-email>

## Use
    residual verify --intent ./intent.json
    residual conform
    residual status
    residual serve          # localhost:7180

## Build
    make fetch-py GOOS=darwin GOARCH=arm64
    goreleaser release --snapshot --clean

## License
Commercial. See LICENSE.
