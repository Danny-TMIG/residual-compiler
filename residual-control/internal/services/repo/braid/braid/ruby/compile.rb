#!/usr/bin/env ruby
require 'json'
require 'securerandom'

schema = JSON.parse(File.read('schema.json'))
symbols = JSON.parse(File.read('symbols.json'))
intent = JSON.parse(File.read('intent.json'))

resolved = intent["symbols"].map { |id| symbols[id] }.compact
ops = resolved.flat_map { |s| s["expands_to"]["operators"] }

nodes = ops.each_with_index.map do |op, i|
  {
    "id"       => SecureRandom.uuid,
    "operator" => op,
    "inputs"   => {},
    "outputs"  => {},
    "status"   => "PENDING"
  }
end

edges = (0...(nodes.length - 1)).map do |i|
  { "from" => nodes[i]["id"], "to" => nodes[i+1]["id"], "condition" => {} }
end

graph = { "nodes" => nodes, "edges" => edges }
puts JSON.pretty_generate(graph)
File.write("graph-ruby.json", JSON.pretty_generate(graph))
