package main

import (
    "fmt"
    "os"

    "github.com/you/residual/internal/license"
    "github.com/you/residual/internal/runtime"
    "github.com/you/residual/internal/server"
    "github.com/spf13/cobra"
)

func main() {
    root := &cobra.Command{Use: "residual", Short: "Sovereign intent verification"}

    root.AddCommand(&cobra.Command{
        Use: "activate <jwt>", Short: "Store a license token", Args: cobra.ExactArgs(1),
        RunE: func(_ *cobra.Command, a []string) error { return license.Store(a[0]) },
    })

    root.AddCommand(&cobra.Command{
        Use: "verify", Short: "Verify against an intent file",
        RunE: func(_ *cobra.Command, a []string) error { return runtime.Run("scripts/intent_verify.py", a...) },
    })

    root.AddCommand(&cobra.Command{
        Use: "conform", Short: "Check record chain + conformance",
        RunE: func(_ *cobra.Command, _ []string) error { return runtime.Run("scripts/conform.py") },
    })

    root.AddCommand(&cobra.Command{
        Use: "serve", Short: "Local API on :7180",
        RunE: func(_ *cobra.Command, _ []string) error { return server.Run(":7180") },
    })

    root.AddCommand(&cobra.Command{
        Use: "status", Short: "Show license + install status",
        RunE: func(_ *cobra.Command, _ []string) error {
            l, err := license.Load()
            if err != nil { fmt.Println("license: none"); return nil }
            fmt.Printf("license: %s (%s), expires %s\n", l.Email, l.Tier, l.Expires.Format("2006-01-02"))
            return nil
        },
    })

    if err := root.Execute(); err != nil { os.Exit(1) }
}
