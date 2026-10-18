package license

import (
    _ "embed"
    "errors"
    "os"
    "path/filepath"
    "time"

    "github.com/golang-jwt/jwt/v5"
)

//go:embed public.pem
var pubPEM []byte

type License struct {
    Email   string
    Tier    string
    Expires time.Time
}

func Store(token string) error {
    p, err := path()
    if err != nil { return err }
    if err := os.MkdirAll(filepath.Dir(p), 0o755); err != nil { return err }
    return os.WriteFile(p, []byte(token), 0o600)
}

func Load() (*License, error) {
    tok := os.Getenv("RESIDUAL_LICENSE")
    if tok == "" {
        p, err := path()
        if err != nil { return nil, err }
        b, err := os.ReadFile(p)
        if err != nil { return nil, errors.New("no license installed") }
        tok = string(b)
    }
    return verify(tok)
}

func verify(token string) (*License, error) {
    key, err := jwt.ParseEdPublicKeyFromPEM(pubPEM)
    if err != nil { return nil, err }
    t, err := jwt.Parse(token, func(t *jwt.Token) (any, error) {
        if _, ok := t.Method.(*jwt.SigningMethodEd25519); !ok {
            return nil, errors.New("bad alg")
        }
        return key, nil
    })
    if err != nil || !t.Valid { return nil, errors.New("invalid license") }
    c := t.Claims.(jwt.MapClaims)
    exp := time.Unix(int64(c["exp"].(float64)), 0)
    if time.Now().After(exp) { return nil, errors.New("license expired") }
    return &License{Email: c["sub"].(string), Tier: c["tier"].(string), Expires: exp}, nil
}

func path() (string, error) {
    home, err := os.UserHomeDir()
    if err != nil { return "", err }
    return filepath.Join(home, ".residual", "license.jwt"), nil
}
