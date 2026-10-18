package runtime

import (
    "archive/tar"
    "bytes"
    "compress/gzip"
    "embed"
    "io"
    "io/fs"
    "os"
    "os/exec"
    "path/filepath"
)

//go:embed python.tar.gz
var pyFS embed.FS

//go:embed all:repo
var assets embed.FS

func cacheDir() (string, error) {
    d, err := os.UserCacheDir()
    if err != nil { return "", err }
    p := filepath.Join(d, "residual")
    return p, os.MkdirAll(p, 0o755)
}

func Run(script string, args ...string) error {
    _, err := RunCapture(script, args...)
    return err
}

func RunCapture(script string, args ...string) ([]byte, error) {
    root, err := ensure()
    if err != nil { return nil, err }
    py := filepath.Join(root, "python", "bin", "python3")
    sp := filepath.Join(root, script)
    cmd := exec.Command(py, append([]string{sp}, args...)...)
    cmd.Dir = root
    cmd.Env = append(os.Environ(), "RESIDUAL_ROOT="+root)
    var out, errb bytes.Buffer
    cmd.Stdout, cmd.Stderr, cmd.Stdin = &out, &errb, os.Stdin
    err = cmd.Run()
    if err != nil { return out.Bytes(), err }
    return out.Bytes(), nil
}

func ensure() (string, error) {
    root, err := cacheDir()
    if err != nil { return "", err }
    marker := filepath.Join(root, ".ready")
    if _, err := os.Stat(marker); err == nil { return root, nil }
    if err := extractPython(root); err != nil { return "", err }
    if err := extractAssets(root); err != nil { return "", err }
    return root, os.WriteFile(marker, []byte("1"), 0o644)
}

func extractPython(root string) error {
    f, err := pyFS.Open("python.tar.gz")
    if err != nil { return err }
    defer f.Close()
    gz, err := gzip.NewReader(f)
    if err != nil { return err }
    return untar(tar.NewReader(gz), root)
}

func extractAssets(root string) error {
    return fs.WalkDir(assets, "repo", func(p string, d fs.DirEntry, err error) error {
        if err != nil { return err }
        if d.IsDir() { return nil }
        b, err := assets.ReadFile(p)
        if err != nil { return err }
        rel, _ := filepath.Rel("repo", p)
        dst := filepath.Join(root, rel)
        if err := os.MkdirAll(filepath.Dir(dst), 0o755); err != nil { return err }
        return os.WriteFile(dst, b, 0o644)
    })
}

func untar(tr *tar.Reader, dst string) error {
    for {
        h, err := tr.Next()
        if err == io.EOF { return nil }
        if err != nil { return err }
        p := filepath.Join(dst, h.Name)
        if h.Typeflag == tar.TypeDir { os.MkdirAll(p, 0o755); continue }
        if err := os.MkdirAll(filepath.Dir(p), 0o755); err != nil { return err }
        w, err := os.OpenFile(p, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, os.FileMode(h.Mode))
        if err != nil { return err }
        io.Copy(w, tr); w.Close()
    }
}
