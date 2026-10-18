package main

import (
    "encoding/json"
    "io"
    "log"
    "net/http"
    "os"
    "time"

    "github.com/golang-jwt/jwt/v5"
    "github.com/stripe/stripe-go/v78/webhook"
)

func main() {
    pem, err := os.ReadFile(os.Getenv("RESIDUAL_SIGNING_KEY"))
    if err != nil { log.Fatal(err) }
    key, err := jwt.ParseEdPrivateKeyFromPEM(pem)
    if err != nil { log.Fatal(err) }

    http.HandleFunc("/stripe", func(w http.ResponseWriter, r *http.Request) {
        body, _ := io.ReadAll(r.Body)
        ev, err := webhook.ConstructEvent(body, r.Header.Get("Stripe-Signature"),
            os.Getenv("STRIPE_WEBHOOK_SECRET"))
        if err != nil { http.Error(w, err.Error(), 400); return }
        if ev.Type == "checkout.session.completed" {
            var s struct {
                CustomerDetails struct{ Email string } `json:"customer_details"`
                Metadata        map[string]string      `json:"metadata"`
            }
            json.Unmarshal(ev.Data.Raw, &s)
            tok := jwt.NewWithClaims(jwt.SigningMethodEdDSA, jwt.MapClaims{
                "sub":  s.CustomerDetails.Email,
                "tier": s.Metadata["tier"],
                "exp":  time.Now().Add(365 * 24 * time.Hour).Unix(),
                "iss":  "residual.dev",
            })
            signed, _ := tok.SignedString(key)
            log.Printf("license → %s : %s", s.CustomerDetails.Email, signed)
            // wire Resend/Postmark here; do not block the webhook on email success
        }
        w.WriteHeader(200)
    })
    log.Fatal(http.ListenAndServe(":"+os.Getenv("PORT"), nil))
}
