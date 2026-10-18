package services

import (
	"context"
	"strings"
	"testing"
)

func TestEmbeddedRepoVerify(t *testing.T) {
	svc, err := NewAutomationService()
	if err != nil {
		t.Fatal(err)
	}
	defer svc.Close()
	out, err := svc.Verify(context.Background())
	if err != nil {
		t.Fatalf("verify failed: %v\n%s", err, out)
	}
	if !strings.Contains(out, `"verdict": "COVERED"`) {
		t.Fatalf("unexpected output:\n%s", out)
	}
}
