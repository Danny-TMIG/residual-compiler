package runtime

import (
    "bytes"
    "compress/gzip"
    "embed"
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
    b, err := RunCapture(script, args...)
    os.Stdout.Write(b)
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
    return out.Bytes(), err
}

func ensure() (string, error) {
    root, err := cacheDir()
    if err != nil { return "", err }
    marker := filepath.Join(root, ".ready")
    if _, err := os.Stat(marker); err == nil { return root, nil }
    if err := extractPython(root); err != nil { return "", err }
    if err := extractAssets(root); err != nil { return "", err }
    py := filepath.Join(root, "python", "bin", "python3")
    fi, err := os.Stat(py)
    if err != nil || fi.Size() == 0 {
        os.RemoveAll(root)
        return "", err
    }
    return root, os.WriteFile(marker, []byte("1"), 0o644)
}

func extractPython(root string) error {
    f, err := pyFS.Open("python.tar.gz")
    if err != nil { return err }
    defer f.Close()
    gz, err := gzip.NewReader(f)
    if err != nil { return err }
    return untarStream(gz, root)
}

func extractAssets(root string) error {
    return fs.WalkDir(assets, "repo", func(p string, d fs.DirEntry, err error) error {
        if err != nil || d.IsDir() { return err }
        b, err := assets.ReadFile(p)
        if err != nil { return err }
        rel, _ := filepath.Rel("repo", p)
        dst := filepath.Join(root, rel)
        if err := os.MkdirAll(filepath.Dir(dst), 0o755); err != nil { return err }
        return os.WriteFile(dst, b, 0o644)
    })
}
