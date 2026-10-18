package runtime

import (
    "archive/tar"
    "fmt"
    "io"
    "os"
    "path/filepath"
    "strings"
)

func untarStream(r io.Reader, dst string) error {
    return untar(tar.NewReader(r), dst)
}

func untar(tr *tar.Reader, dst string) error {
    cleanDst := filepath.Clean(dst)
    for {
        h, err := tr.Next()
        if err == io.EOF { return nil }
        if err != nil { return err }
        p := filepath.Join(dst, h.Name)
        if p != cleanDst && !strings.HasPrefix(p, cleanDst+string(os.PathSeparator)) {
            return fmt.Errorf("tar entry escapes root: %s", h.Name)
        }
        switch h.Typeflag {
        case tar.TypeDir:
            if err := os.MkdirAll(p, 0o755); err != nil { return err }
        case tar.TypeSymlink:
            if err := os.MkdirAll(filepath.Dir(p), 0o755); err != nil { return err }
            _ = os.Remove(p)
            if err := os.Symlink(h.Linkname, p); err != nil { return err }
        case tar.TypeLink:
            if err := os.MkdirAll(filepath.Dir(p), 0o755); err != nil { return err }
            _ = os.Remove(p)
            if err := os.Link(filepath.Join(dst, h.Linkname), p); err != nil { return err }
        case tar.TypeReg, tar.TypeRegA:
            if err := os.MkdirAll(filepath.Dir(p), 0o755); err != nil { return err }
            w, err := os.OpenFile(p, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, os.FileMode(h.Mode))
            if err != nil { return err }
            if _, err := io.Copy(w, tr); err != nil { w.Close(); return err }
            w.Close()
        }
    }
}
