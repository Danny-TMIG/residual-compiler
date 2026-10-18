use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Expansion {
    operators: Vec<String>,
    #[serde(default)]
    constraints: HashMap<String, serde_json::Value>,
    #[serde(default)]
    default_params: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Symbol {
    id: String,
    #[serde(default)]
    embedding: Vec<f64>,
    expands_to: Expansion,
    #[serde(default)]
    aliases: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Intent {
    id: String,
    raw_input: String,
    symbols: Vec<String>,
    #[serde(default)]
    context: String,
    #[serde(default)]
    priority: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ExecNode {
    id: String,
    operator: String,
    #[serde(default)]
    inputs: HashMap<String, serde_json::Value>,
    #[serde(default)]
    outputs: HashMap<String, serde_json::Value>,
    status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ExecEdge {
    from: String,
    to: String,
    #[serde(default)]
    condition: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ExecGraph {
    nodes: Vec<ExecNode>,
    edges: Vec<ExecEdge>,
}

fn compile(table: &HashMap<String, Symbol>, intent: &Intent) -> ExecGraph {
    let resolved: Vec<&Symbol> = intent.symbols.iter()
        .filter_map(|id| table.get(id))
        .collect();
    let ops: Vec<String> = resolved.iter()
        .flat_map(|s| s.expands_to.operators.clone())
        .collect();
    let nodes: Vec<ExecNode> = ops.iter().enumerate()
        .map(|(i, op)| ExecNode {
            id: format!("n-{}", i),
            operator: op.clone(),
            inputs: HashMap::new(),
            outputs: HashMap::new(),
            status: "PENDING".to_string(),
        })
        .collect();
    let edges: Vec<ExecEdge> = (0..nodes.len().saturating_sub(1))
        .map(|i| ExecEdge {
            from: nodes[i].id.clone(),
            to: nodes[i+1].id.clone(),
            condition: HashMap::new(),
        })
        .collect();
    ExecGraph { nodes, edges }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).parent().unwrap();
    let table_json = fs::read_to_string(root.join("symbols.json"))?;
    let table: HashMap<String, Symbol> = serde_json::from_str(&table_json)?;
    let intent_json = fs::read_to_string(root.join("intent.json"))?;
    let intent: Intent = serde_json::from_str(&intent_json)?;
    let graph = compile(&table, &intent);
    let out = serde_json::to_string_pretty(&graph)?;
    println!("{}", out);
    fs::write(root.join("graph-rust.json"), out)?;
    Ok(())
}
