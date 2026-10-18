package main

import (
    "encoding/json"
    "fmt"
    "os"
)

type Expansion struct {
    Operators     []string          `json:"operators"`
    Constraints   map[string]any    `json:"constraints"`
    DefaultParams map[string]any    `json:"default_params"`
}

type Symbol struct {
    ID        string    `json:"id"`
    Embedding []float64 `json:"embedding"`
    ExpandsTo Expansion `json:"expands_to"`
    Aliases   []string  `json:"aliases"`
}

type ExecNode struct {
    ID       string         `json:"id"`
    Operator string         `json:"operator"`
    Inputs   map[string]any `json:"inputs"`
    Outputs  map[string]any `json:"outputs"`
    Status   string         `json:"status"`
}

type ExecGraph struct {
    Nodes []ExecNode `json:"nodes"`
    Edges []any      `json:"edges"`
}

func compile(symbols []Symbol) ExecGraph {
    var ops []string
    for _, s := range symbols {
        ops = append(ops, s.ExpandsTo.Operators...)
    }
    var nodes []ExecNode
    for i, op := range ops {
        nodes = append(nodes, ExecNode{
            ID:       fmt.Sprintf("n-%d", i),
            Operator: op,
            Status:   "PENDING",
        })
    }
    return ExecGraph{Nodes: nodes}
}

func main() {
    data, _ := os.ReadFile("symbols.json")
    var table map[string]Symbol
    json.Unmarshal(data, &table)

    data, _ = os.ReadFile("intent.json")
    var intent struct {
        Symbols []string `json:"symbols"`
    }
    json.Unmarshal(data, &intent)

    var resolved []Symbol
    for _, sid := range intent.Symbols {
        if s, ok := table[sid]; ok {
            resolved = append(resolved, s)
        }
    }

    g := compile(resolved)
    out, _ := json.MarshalIndent(g, "", "  ")
    fmt.Println(string(out))
    _ = os.WriteFile("graph-go.json", out, 0644)
}
