package services

import (
	"context"
	"embed"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
)

//go:embed all:repo
var repoFS embed.FS

type AutomationService struct {
	root    string
	binPath string
}

func NewAutomationService() (*AutomationService, error) {
	dir, err := os.MkdirTemp("", "residual-root-*")
	if err != nil {
		return nil, err
	}
	if err := extractRepo(dir); err != nil {
		os.RemoveAll(dir)
		return nil, err
	}
	bin := filepath.Join(dir, "residual")
	if err := os.Chmod(bin, 0o755); err != nil {
		os.RemoveAll(dir)
		return nil, err
	}
	return &AutomationService{root: dir, binPath: bin}, nil
}

func extractRepo(dst string) error {
	return fs.WalkDir(repoFS, "repo", func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		rel, _ := filepath.Rel("repo", path)
		if rel == "." {
			return nil
		}
		target := filepath.Join(dst, rel)
		if d.IsDir() {
			return os.MkdirAll(target, 0o755)
		}
		data, err := repoFS.ReadFile(path)
		if err != nil {
			return err
		}
		mode := fs.FileMode(0o644)
		if filepath.Base(rel) == "residual" {
			mode = 0o755
		}
		return os.WriteFile(target, data, mode)
	})
}

func (a *AutomationService) Close() error { return os.RemoveAll(a.root) }

func (a *AutomationService) run(ctx context.Context, cmd string) (string, error) {
	c := exec.CommandContext(ctx, a.binPath, cmd)
	c.Env = append(os.Environ(), "RESIDUAL_ROOT="+a.root)
	out, err := c.CombinedOutput()
	return string(out), err
}

func (a *AutomationService) Verify(ctx context.Context) (string, error)  { return a.run(ctx, "verify") }
func (a *AutomationService) Org(ctx context.Context) (string, error)     { return a.run(ctx, "org") }
func (a *AutomationService) Const(ctx context.Context) (string, error)   { return a.run(ctx, "const") }
func (a *AutomationService) Conform(ctx context.Context) (string, error) { return a.run(ctx, "conform") }
