package server

import (
    "embed"
    "encoding/json"
    "io"
    "io/fs"
    "net/http"
    "os"
    "path/filepath"

    "github.com/you/residual/internal/license"
    "github.com/you/residual/internal/runtime"
)

//go:embed all:web
var webFS embed.FS

func Run(addr string) error {
    mux := http.NewServeMux()

    mux.HandleFunc("GET /api/healthz", func(w http.ResponseWriter, _ *http.Request) {
        w.Write([]byte("ok"))
    })
    mux.HandleFunc("GET /api/status",  handleStatus)
    mux.HandleFunc("GET /api/verify",  handleVerify)
    mux.HandleFunc("POST /api/verify", handleVerifyPOST)
    mux.HandleFunc("GET /api/conform", handleConform)

    sub, _ := fs.Sub(webFS, "web")
    mux.Handle("/", http.FileServer(http.FS(sub)))

    return http.ListenAndServe(addr, mux)
}

func handleStatus(w http.ResponseWriter, _ *http.Request) {
    l, err := license.Load()
    if err != nil {
        writeJSON(w, 200, map[string]any{"licensed": false})
        return
    }
    writeJSON(w, 200, map[string]any{
        "licensed": true,
        "license": map[string]any{
            "email":   l.Email,
            "tier":    l.Tier,
            "expires": l.Expires.Format("2006-01-02"),
        },
    })
}

func handleVerify(w http.ResponseWriter, r *http.Request) {
    intent := r.URL.Query().Get("intent")
    if intent == "" {
        writeErr(w, 400, "missing ?intent=<path>")
        return
    }
    b, err := runtime.RunCapture("scripts/intent_verify.py", "--intent", intent)
    writeResult(w, b, err)
}

// POST /api/verify — body is the intent JSON; we write it to a temp file and run.
func handleVerifyPOST(w http.ResponseWriter, r *http.Request) {
    body, err := io.ReadAll(r.Body)
    if err != nil {
        writeErr(w, 400, "read body: "+err.Error())
        return
    }
    tmp, err := os.CreateTemp("", "intent-*.json")
    if err != nil {
        writeErr(w, 500, err.Error())
        return
    }
    defer os.Remove(tmp.Name())
    if _, err := tmp.Write(body); err != nil {
        writeErr(w, 500, err.Error())
        return
    }
    tmp.Close()
    b, err := runtime.RunCapture("scripts/intent_verify.py", "--intent", tmp.Name())
    writeResult(w, b, err)
}

func handleConform(w http.ResponseWriter, _ *http.Request) {
    b, err := runtime.RunCapture("scripts/conform.py")
    writeResult(w, b, err)
}

func writeResult(w http.ResponseWriter, b []byte, err error) {
    if err != nil {
        writeJSON(w, 500, map[string]any{"error": err.Error(), "output": string(b)})
        return
    }
    w.Header().Set("Content-Type", "application/json")
    w.Write(b)
}

func writeErr(w http.ResponseWriter, code int, msg string) {
    writeJSON(w, code, map[string]string{"error": msg})
}

func writeJSON(w http.ResponseWriter, code int, v any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(code)
    json.NewEncoder(w).Encode(v)
}

// defaultIntentPath is only used by cmd/residual to print a helpful default.
func DefaultIntentPath() string {
    home, _ := os.UserHomeDir()
    return filepath.Join(home, ".residual", "intent.json")
}

var _ = DefaultIntentPath
