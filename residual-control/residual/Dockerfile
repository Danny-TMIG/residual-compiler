FROM golang:1.23 AS build
WORKDIR /src
COPY . .
RUN go build -trimpath -ldflags="-s -w" -o /residual ./cmd/residual

FROM gcr.io/distroless/static
COPY --from=build /residual /residual
ENTRYPOINT ["/residual"]
CMD ["serve"]
