package server

import (
    "net/http"

    "github.com/you/residual/internal/runtime"
)

func Run(addr string) error {
    mux := http.NewServeMux()
    mux.HandleFunc("/verify", func(w http.ResponseWriter, r *http.Request) {
        b, err := runtime.RunCapture("scripts/intent_verify.py", "--intent", r.URL.Query().Get("intent"))
        if err != nil { http.Error(w, err.Error(), 500); return }
        w.Header().Set("Content-Type", "application/json")
        w.Write(b)
    })
    mux.HandleFunc("/conform", func(w http.ResponseWriter, _ *http.Request) {
        b, err := runtime.RunCapture("scripts/conform.py")
        if err != nil { http.Error(w, err.Error(), 500); return }
        w.Header().Set("Content-Type", "application/json")
        w.Write(b)
    })
    mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
        w.Write([]byte("ok"))
    })
    return http.ListenAndServe(addr, mux)
}

var _ = json.Marshal
