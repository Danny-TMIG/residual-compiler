#!/usr/bin/env bash
set -euo pipefail
cd /tmp/test
mkdir -p data/atlas src schemas tests bin conf docs scripts data/raw data/processed models artifacts checkpoints state logs

# =========================================================
# STEP 1 — write the atlas verbatim (quoted heredoc: no expansion)
# =========================================================
cat > data/atlas/atlas.txt <<'ATLAS'
DEV AGENT / SKILL ATLAS — Vendor AGNOSTIC

roles become composable agency functions, skills become executable contracts, flocks are compiled dynamically from work, Dunbar constraints bound direct coordination, evidence—not consensus—determines qualification, and every completed swarm compounds the skill/evidence/repair graphs for the next one.

The cognition/governance boundary can be instrumented like a network. Decision provenance is the signaling data. Boundary crossings are the handoffs. Correction asymmetry is the latency. Democratic feedback is the quality of service. Measure it, and you can govern it — reflexively, accountably, and without surveilling anyone.

DOMAINS = [ "Software engineering", "Systems engineering", "Security engineering", "Data engineering", "ML/AI engineering", "DevOps/SRE", "Platform engineering", "Quality engineering", "Compliance engineering", "Observability engineering", "FinOps", "Governance", "Risk engineering", "Privacy engineering", "Accessibility", "Internationalization", "Documentation", "API design", "Database", "Network", "Supply chain", "Release engineering", "Chaos engineering", "Performance engineering", "Capacity engineering", "Business continuity", "Support engineering", "Legal/contract"

01. AGENT FUNCTIONS

Intent / Intake

* Intent Listener
* Intent Interpreter
* Intent Parser
* Intent Normalizer
* Intent Disambiguator
* Intent Reconciler
* Intent Mirror
* Intent Contract Builder
* Constraint Extractor
* Assumption Extractor
* Objective Extractor
* Success-Criteria Extractor
* Acceptance-Criteria Extractor
* Requirement Elicitor
* Requirement Resolver
* Context Collector
* Context Curator
* Context Compressor
* Context Restorer
* Provenance Collector
* Boundary Detector
* Scope Controller
* Change Detector
* Gap Detector
* Conflict Detector
* Dependency Detector
* Unknown Detector

Discovery / Research

* Scout
* Researcher
* Searcher
* Retriever
* Repository Explorer
* Codebase Explorer
* Dependency Explorer
* Interface Explorer
* API Explorer
* Standards Explorer
* Specification Explorer
* Documentation Explorer
* Dataset Explorer
* Model Explorer
* Package Explorer
* Infrastructure Explorer
* Runtime Explorer
* Environment Explorer
* Prior-Art Explorer
* Vulnerability Explorer
* Threat Explorer
* Evidence Explorer
* Benchmark Explorer
* Compatibility Explorer
* License Explorer

Analysis / Reasoning

* Analyst
* Systems Analyst
* Requirements Analyst
* Domain Analyst
* Data Analyst
* Static Analyst
* Dynamic Analyst
* Dependency Analyst
* Risk Analyst
* Failure Analyst
* Performance Analyst
* Cost Analyst
* Security Analyst
* Safety Analyst
* Compliance Analyst
* Reliability Analyst
* Architecture Analyst
* Compatibility Analyst
* Root-Cause Analyst
* Impact Analyst
* Tradeoff Analyst
* Counterfactual Analyst
* Constraint Solver
* Consistency Checker
* Equivalence Checker
* Invariant Checker

Planning

* Planner
* Decomposer
* Task Graph Builder
* Work Graph Builder
* Dependency Planner
* Milestone Planner
* Release Planner
* Migration Planner
* Rollout Planner
* Test Planner
* Validation Planner
* Qualification Planner
* Recovery Planner
* Capacity Planner
* Resource Planner
* Cost Planner
* Scheduling Planner
* Parallelization Planner
* Sequencing Planner
* Critical-Path Planner
* Experiment Planner
* Benchmark Planner
* Verification Planner

Architecture / Design

* Architect
* Systems Architect
* Software Architect
* Solution Architect
* Platform Architect
* Data Architect
* AI Architect
* Runtime Architect
* Compiler Architect
* Security Architect
* Network Architect
* Cloud Architect
* Infrastructure Architect
* Storage Architect
* Database Architect
* API Architect
* Integration Architect
* Identity Architect
* Observability Architect
* Reliability Architect
* Firmware Architect
* Operating-System Architect
* Hardware Architect
* Verification Architect
* Deployment Architect
* Enterprise Architect

Specification / Formalization

* Specification Author
* Contract Author
* Schema Author
* Type-System Author
* Interface Author
* Protocol Author
* Policy Author
* Rule Author
* Grammar Author
* Ontology Author
* Taxonomy Author
* State-Machine Author
* Invariant Author
* Proof-Obligation Author
* Test-Oracle Author
* Acceptance-Test Author
* Conformance-Rule Author
* Configuration Author
* Manifest Author

Implementation

* Builder
* Programmer
* Application Developer
* Backend Developer
* Frontend Developer
* Full-Stack Developer
* Mobile Developer
* Desktop Developer
* Embedded Developer
* Firmware Developer
* Kernel Developer
* Driver Developer
* Systems Programmer
* Compiler Developer
* Runtime Developer
* Database Developer
* API Developer
* Integration Developer
* Automation Developer
* Infrastructure Developer
* Security Developer
* ML Developer
* Data Engineer
* Test Engineer
* Build Engineer
* Release Engineer

Transformation

* Refactorer
* Rewriter
* Translator
* Transpiler
* Migrator
* Modernizer
* Porting Agent
* Adapter Builder
* Wrapper Builder
* Shim Builder
* Polyfill Builder
* Serializer Builder
* Deserializer Builder
* Converter
* Normalizer
* Canonicalizer
* Optimizer
* Simplifier
* Deduplicator
* Modularizer
* Extractor
* Merger
* Splitter

Review

* Reviewer
* Code Reviewer
* Architecture Reviewer
* Design Reviewer
* Security Reviewer
* Privacy Reviewer
* Safety Reviewer
* Compliance Reviewer
* Performance Reviewer
* Reliability Reviewer
* API Reviewer
* Schema Reviewer
* Database Reviewer
* Infrastructure Reviewer
* Test Reviewer
* Documentation Reviewer
* Dependency Reviewer
* License Reviewer
* Accessibility Reviewer
* Localization Reviewer

Verification / Validation

* Verifier
* Validator
* Tester
* Unit Tester
* Integration Tester
* System Tester
* Acceptance Tester
* Regression Tester
* Property Tester
* Fuzz Tester
* Mutation Tester
* Differential Tester
* Compatibility Tester
* Conformance Tester
* Interoperability Tester
* Performance Tester
* Load Tester
* Stress Tester
* Chaos Tester
* Security Tester
* Penetration Tester
* Resilience Tester
* Recovery Tester
* Reproducibility Tester
* Determinism Tester
* Benchmark Runner
* Proof Checker

Debugging / Repair

* Debugger
* Fault Localizer
* Error Classifier
* Log Investigator
* Trace Investigator
* Crash Investigator
* Deadlock Investigator
* Race Investigator
* Leak Investigator
* Regression Investigator
* Dependency Resolver
* Environment Resolver
* Build-Failure Resolver
* Test-Failure Resolver
* Runtime-Failure Resolver
* Deployment-Failure Resolver
* Configuration Resolver
* Data-Corruption Resolver
* Repairer
* Patch Generator
* Recovery Agent

Security

* Threat Modeler
* Attack-Surface Mapper
* Vulnerability Assessor
* Vulnerability Triager
* Secure-Code Reviewer
* Secret Scanner
* Dependency Scanner
* Supply-Chain Scanner
* Container Scanner
* Infrastructure Scanner
* Policy Enforcer
* Permission Auditor
* Identity Auditor
* Access-Control Auditor
* Configuration Auditor
* Hardening Agent
* Sandbox Controller
* Capability Controller
* Isolation Controller
* Incident Responder
* Forensics Agent
* Remediation Agent

Operations

* Operator
* Deployment Operator
* Runtime Operator
* Cluster Operator
* Cloud Operator
* Network Operator
* Database Operator
* Storage Operator
* Model Operator
* Queue Operator
* Cache Operator
* Service Operator
* Job Operator
* Scheduler Operator
* Configuration Operator
* Secret Operator
* Certificate Operator
* Backup Operator
* Restore Operator
* Failover Operator
* Scaling Operator
* Maintenance Operator

Observability

* Observer
* Monitor
* Telemetry Collector
* Log Collector
* Metric Collector
* Trace Collector
* Profiler
* Health Checker
* SLO Monitor
* SLA Monitor
* Error-Budget Monitor
* Drift Monitor
* Anomaly Detector
* Regression Detector
* Alert Correlator
* Event Correlator
* Incident Detector
* Evidence Collector
* Audit Collector
* Runtime Historian

Governance / Authority

* Policy Evaluator
* Authority Evaluator
* Permission Evaluator
* Approval Gate
* Qualification Gate
* Risk Gate
* Security Gate
* Compliance Gate
* Release Gate
* Deployment Gate
* Evidence Gate
* Change-Control Agent
* Audit Agent
* Provenance Agent
* Attestation Agent
* Signing Agent
* Chain-of-Custody Agent
* Separation-of-Duties Agent

Coordination

* Coordinator
* Router
* Dispatcher
* Scheduler
* Allocator
* Broker
* Delegator
* Supervisor
* Orchestrator
* Arbiter
* Quorum Coordinator
* Consensus Coordinator
* Conflict Resolver
* Load Balancer
* Work Stealer
* Queue Manager
* Priority Manager
* Resource Governor
* Retry Controller
* Timeout Controller
* Cancellation Controller

Evidence / Qualification

* Evidence Producer
* Evidence Validator
* Evidence Correlator
* Evidence Packager
* Artifact Attestor
* Provenance Verifier
* Requirement-to-Evidence Mapper
* Test-to-Claim Mapper
* Claim Verifier
* Qualification Assessor
* Certification-Support Agent
* Conformance Assessor
* Release-Readiness Assessor
* Production-Readiness Assessor
* Reproducibility Assessor

Documentation / Knowledge

* Technical Writer
* Documentation Generator
* API Documenter
* Architecture Documenter
* Runbook Author
* Playbook Author
* SOP Author
* ADR Author
* Changelog Author
* Release-Note Author
* Tutorial Author
* Example Author
* Knowledge Curator
* Knowledge-Graph Builder
* Indexer
* Cataloger
* Glossary Builder

Stewardship

* Maintainer
* Dependency Maintainer
* Repository Maintainer
* Configuration Maintainer
* Documentation Maintainer
* Policy Maintainer
* Standards Maintainer
* Test Maintainer
* Benchmark Maintainer
* Model Maintainer
* Dataset Maintainer
* Lifecycle Steward
* Deprecation Steward
* Migration Steward
* Compatibility Steward

⸻

02. UNIVERSAL SKILL FAMILIES

Intent

* capture-intent
* preserve-source-intent
* parse-intent
* classify-intent
* normalize-intent
* disambiguate-intent
* reconcile-intent
* mirror-intent
* formalize-intent
* version-intent
* compare-intent
* detect-intent-drift
* map-intent-to-capability
* map-intent-to-requirements
* map-intent-to-work
* map-intent-to-evidence

Context

* acquire-context
* classify-context
* rank-context
* filter-context
* compress-context
* expand-context
* restore-context
* merge-context
* isolate-context
* snapshot-context
* diff-context
* validate-context
* trace-context-provenance
* expire-context
* summarize-context

Requirements

* elicit-requirements
* parse-requirements
* normalize-requirements
* classify-requirements
* decompose-requirements
* prioritize-requirements
* trace-requirements
* validate-requirements
* reconcile-requirements
* detect-conflicts
* detect-gaps
* create-acceptance-criteria
* create-nonfunctional-requirements
* create-constraints
* create-assumptions
* create-dependencies
* create-proof-obligations

Search / Retrieval

* filesystem-search
* repository-search
* symbol-search
* semantic-search
* lexical-search
* regex-search
* dependency-search
* API-search
* documentation-search
* standards-search
* specification-search
* package-search
* model-search
* dataset-search
* vulnerability-search
* prior-art-search
* evidence-search
* log-search
* trace-search
* metric-search
* artifact-search

Repository Intelligence

* inspect-repository
* map-repository
* inventory-files
* inventory-symbols
* inventory-modules
* inventory-services
* inventory-packages
* inventory-dependencies
* inventory-interfaces
* inventory-tests
* inventory-configurations
* inventory-build-systems
* inventory-workflows
* detect-dead-code
* detect-duplicate-code
* detect-generated-code
* detect-vendored-code
* detect-boundaries
* build-dependency-graph
* build-call-graph
* build-dataflow-graph

Planning

* decompose-work
* compose-work
* build-task-graph
* build-dependency-graph
* sequence-work
* parallelize-work
* prioritize-work
* estimate-resources
* estimate-complexity
* identify-critical-path
* assign-capabilities
* assign-skills
* assign-workers
* define-checkpoints
* define-gates
* define-recovery
* define-rollback
* define-evidence
* define-done
* replan

Architecture

* design-system
* design-component
* design-module
* design-service
* design-api
* design-protocol
* design-schema
* design-database
* design-cache
* design-queue
* design-event-bus
* design-storage
* design-network
* design-runtime
* design-compiler
* design-agent-system
* design-model-serving
* design-security
* design-identity
* design-observability
* design-deployment
* design-resilience
* design-multi-tenancy
* design-distributed-system
* design-edge-system
* design-embedded-system

Modeling

* create-domain-model
* create-data-model
* create-object-model
* create-state-model
* create-state-machine
* create-process-model
* create-threat-model
* create-cost-model
* create-capacity-model
* create-performance-model
* create-failure-model
* create-reliability-model
* create-knowledge-graph
* create-ontology
* create-taxonomy
* create-capability-graph
* create-skill-graph
* create-evidence-graph

Formal Methods

* define-invariants
* define-preconditions
* define-postconditions
* define-contracts
* define-types
* prove-properties
* model-check
* theorem-check
* equivalence-check
* satisfiability-check
* constraint-solve
* symbolic-execute
* abstract-interpret
* verify-state-machine
* verify-protocol
* verify-memory-safety
* verify-concurrency-properties

Coding

* create-file
* read-file
* edit-file
* patch-file
* delete-file
* move-file
* rename-file
* generate-code
* complete-code
* repair-code
* refactor-code
* simplify-code
* optimize-code
* modularize-code
* generalize-code
* specialize-code
* parameterize-code
* inline-code
* extract-function
* extract-module
* extract-interface
* generate-boilerplate
* generate-scaffold
* remove-boilerplate
* implement-interface
* implement-feature
* implement-algorithm
* implement-protocol
* implement-service

Language Engineering

* lexical-analysis
* parsing
* AST-generation
* AST-transformation
* CST-transformation
* IR-generation
* IR-transformation
* code-generation
* transpilation
* compilation
* interpretation
* linking
* loading
* macro-expansion
* source-formatting
* linting
* type-checking
* static-checking
* dependency-resolution
* package-resolution
* source-mapping

Programming Paradigms

* procedural-programming
* object-oriented-programming
* functional-programming
* declarative-programming
* logic-programming
* reactive-programming
* event-driven-programming
* data-oriented-programming
* actor-model-programming
* concurrent-programming
* parallel-programming
* distributed-programming
* systems-programming
* embedded-programming
* metaprogramming
* differentiable-programming
* probabilistic-programming

Algorithms

* searching
* sorting
* indexing
* hashing
* graph-traversal
* graph-search
* shortest-path
* spanning-tree
* flow-optimization
* dynamic-programming
* greedy-optimization
* divide-and-conquer
* backtracking
* branch-and-bound
* constraint-programming
* string-matching
* compression
* encoding
* decoding
* cryptographic-algorithms
* numerical-algorithms
* geometric-algorithms
* randomized-algorithms
* streaming-algorithms

Data Structures

* arrays
* lists
* linked-lists
* stacks
* queues
* deques
* sets
* maps
* hash-tables
* trees
* tries
* heaps
* graphs
* bloom-filters
* bitsets
* matrices
* tensors
* sparse-structures
* spatial-indexes
* time-series-structures
* persistent-structures
* concurrent-structures

API Engineering

* design-rest-api
* design-graphql-api
* design-rpc-api
* design-stream-api
* design-websocket-api
* design-event-api
* define-api-contract
* generate-client
* generate-server
* validate-api
* test-api
* mock-api
* version-api
* secure-api
* document-api
* monitor-api
* deprecate-api
* migrate-api

Database

* schema-design
* schema-migration
* query-authoring
* query-optimization
* indexing
* transaction-design
* concurrency-control
* replication
* sharding
* partitioning
* backup
* restore
* point-in-time-recovery
* consistency-validation
* integrity-validation
* data-retention
* data-archival
* database-security
* database-observability
* database-performance-tuning

Data Engineering

* data-ingestion
* data-extraction
* data-transformation
* data-loading
* data-validation
* data-cleaning
* data-normalization
* data-enrichment
* data-deduplication
* data-joining
* data-partitioning
* data-indexing
* data-versioning
* data-lineage
* data-provenance
* batch-processing
* stream-processing
* event-processing
* pipeline-orchestration
* lakehouse-management
* warehouse-management

AI / ML

* dataset-preparation
* feature-engineering
* model-selection
* model-training
* model-finetuning
* adapter-training
* model-evaluation
* model-benchmarking
* model-quantization
* model-pruning
* model-distillation
* model-conversion
* model-export
* model-serving
* model-routing
* ensemble-inference
* inference-optimization
* embedding-generation
* retrieval-augmentation
* reranking
* prompt-construction
* context-construction
* tool-use
* structured-generation
* constrained-decoding
* model-monitoring
* drift-detection
* hallucination-testing
* safety-evaluation

Tensor / Numerical Computing

* scalar-operations
* vector-operations
* matrix-operations
* tensor-operations
* sparse-operations
* linear-algebra
* differentiation
* automatic-differentiation
* optimization
* interpolation
* extrapolation
* integration
* finite-difference
* finite-element
* spectral-methods
* monte-carlo
* numerical-stability-analysis
* precision-analysis
* GPU-kernel-generation
* SIMD-vectorization

Distributed Systems

* leader-election
* consensus
* membership
* service-discovery
* distributed-locking
* distributed-transactions
* replication
* partitioning
* sharding
* routing
* load-balancing
* failover
* retries
* idempotency
* backpressure
* rate-limiting
* circuit-breaking
* queue-management
* clock-synchronization
* causal-ordering
* eventual-consistency
* strong-consistency
* distributed-tracing

Concurrency

* thread-management
* process-management
* coroutine-management
* async-io
* actor-management
* synchronization
* locking
* lock-free-programming
* wait-free-programming
* deadlock-detection
* deadlock-prevention
* race-detection
* atomic-operations
* scheduling
* work-stealing
* parallel-execution

Operating Systems

* process-control
* memory-management
* virtual-memory
* filesystem-management
* device-management
* driver-development
* interrupt-handling
* syscall-development
* kernel-module-development
* scheduler-development
* IPC
* networking-stack
* boot-management
* service-management
* privilege-management
* sandboxing
* namespace-management
* cgroup-management
* resource-accounting

Firmware / Embedded

* bootloader-development
* firmware-development
* HAL-development
* driver-development
* peripheral-control
* bus-protocols
* GPIO-control
* interrupt-control
* timer-control
* DMA-control
* power-management
* RTOS-development
* bare-metal-development
* firmware-signing
* firmware-update
* secure-boot
* hardware-debugging
* hardware-in-loop-testing

Hardware / HDL

* digital-logic-design
* RTL-design
* HDL-authoring
* synthesis
* timing-analysis
* place-and-route
* FPGA-programming
* ASIC-flow
* verification
* simulation
* formal-hardware-verification
* interface-design
* memory-controller-design
* accelerator-design
* board-bringup
* signal-analysis

Networking

* network-design
* subnetting
* routing
* switching
* DNS
* DHCP
* NAT
* VPN
* TLS
* HTTP
* HTTP2
* HTTP3
* QUIC
* TCP
* UDP
* IP
* BGP
* OSPF
* load-balancing
* proxying
* tunneling
* service-mesh
* firewalling
* packet-analysis
* traffic-shaping
* network-observability

Web

* semantic-html
* css
* responsive-layout
* accessibility
* browser-api
* DOM
* web-components
* client-routing
* server-rendering
* static-generation
* hydration
* forms
* state-management
* caching
* service-workers
* PWA
* web-performance
* browser-security
* SEO
* localization

Mobile

* native-mobile-development
* cross-platform-mobile-development
* mobile-ui
* mobile-navigation
* device-api
* mobile-storage
* mobile-networking
* push-notifications
* background-tasks
* mobile-security
* app-signing
* app-packaging
* mobile-testing
* mobile-performance
* accessibility-mobile

Desktop

* native-desktop-development
* cross-platform-desktop-development
* window-management
* desktop-ui
* filesystem-integration
* OS-integration
* desktop-packaging
* signing
* updating
* desktop-security
* desktop-testing

CLI / Terminal

* command-design
* argument-parsing
* stdin-processing
* stdout-formatting
* stderr-handling
* exit-code-management
* shell-integration
* terminal-ui
* interactive-prompts
* completion-generation
* piping
* streaming
* scripting
* automation

Build Systems

* configure-build
* resolve-dependencies
* compile
* link
* bundle
* package
* generate-artifacts
* cache-build
* incremental-build
* cross-compile
* reproducible-build
* hermetic-build
* sign-build
* attest-build
* verify-build

Package Management

* package-create
* package-install
* package-update
* package-remove
* dependency-lock
* dependency-resolve
* dependency-audit
* dependency-pin
* dependency-upgrade
* dependency-downgrade
* dependency-vendor
* publish-package
* verify-package
* sign-package

Source Control

* repository-init
* clone
* fetch
* pull
* branch
* checkout
* stage
* commit
* amend
* merge
* rebase
* cherry-pick
* revert
* reset
* tag
* diff
* blame
* bisect
* patch
* submodule-management
* worktree-management
* conflict-resolution
* history-analysis
* release-tagging

CI

* workflow-design
* pipeline-authoring
* trigger-management
* build-automation
* test-automation
* artifact-management
* cache-management
* matrix-testing
* secret-management
* environment-management
* approval-gates
* policy-gates
* evidence-capture
* pipeline-debugging
* pipeline-optimization

CD / Release

* release-plan
* version-management
* changelog-generation
* artifact-promotion
* artifact-signing
* deployment
* rolling-deployment
* canary-deployment
* blue-green-deployment
* shadow-deployment
* feature-flag-deployment
* progressive-delivery
* rollback
* roll-forward
* release-verification
* release-attestation

Containers

* image-authoring
* image-build
* image-optimize
* image-scan
* image-sign
* image-publish
* container-run
* container-network
* container-storage
* container-security
* runtime-hardening
* compose-services
* container-debugging

Orchestration

* cluster-bootstrap
* workload-definition
* workload-scheduling
* service-definition
* ingress-management
* egress-management
* autoscaling
* configuration-management
* secret-management
* storage-management
* network-policy
* admission-policy
* health-management
* rollout-management
* rollback-management
* cluster-upgrade
* cluster-observability
* cluster-security

Infrastructure as Code

* provision-infrastructure
* plan-infrastructure
* validate-infrastructure
* diff-infrastructure
* apply-infrastructure
* destroy-infrastructure
* import-infrastructure
* state-management
* module-authoring
* policy-validation
* drift-detection
* drift-remediation
* infrastructure-testing
* infrastructure-security
* cost-estimation

Cloud

* account-management
* project-management
* identity-management
* compute-management
* storage-management
* database-management
* networking-management
* serverless-management
* container-management
* messaging-management
* secret-management
* key-management
* certificate-management
* policy-management
* logging
* monitoring
* autoscaling
* cost-management
* quota-management
* disaster-recovery
* multi-region-design
* multi-cloud-design

Edge

* edge-provisioning
* edge-deployment
* edge-sync
* edge-cache
* edge-routing
* edge-inference
* disconnected-operation
* intermittent-network-handling
* fleet-management
* remote-update
* edge-security
* telemetry-sync

Identity

* identity-proofing
* authentication
* authorization
* federation
* SSO
* MFA
* passkeys
* credential-management
* token-management
* session-management
* role-management
* attribute-management
* policy-management
* certificate-identity
* workload-identity
* device-identity
* decentralized-identity
* verifiable-credentials
* revocation

Cryptography

* hashing
* symmetric-encryption
* asymmetric-encryption
* key-generation
* key-exchange
* key-storage
* key-rotation
* digital-signatures
* certificate-validation
* PKI
* secret-sharing
* threshold-cryptography
* secure-randomness
* authenticated-encryption
* envelope-encryption
* zero-knowledge-proofs
* post-quantum-cryptography

Application Security

* secure-design
* secure-coding
* input-validation
* output-encoding
* authentication-security
* authorization-security
* session-security
* CSRF-protection
* XSS-protection
* injection-prevention
* SSRF-prevention
* deserialization-protection
* file-upload-security
* API-security
* secrets-protection
* dependency-security
* supply-chain-security

Security Testing

* SAST
* DAST
* IAST
* SCA
* secret-scanning
* fuzzing
* attack-surface-analysis
* vulnerability-scanning
* exploit-validation
* penetration-testing
* adversary-emulation
* security-regression-testing
* configuration-scanning
* container-scanning
* cloud-security-posture-testing

Threat / Defense

* threat-modeling
* attack-tree-building
* abuse-case-modeling
* detection-engineering
* prevention-engineering
* containment
* eradication
* recovery
* incident-response
* forensic-analysis
* compromise-assessment
* threat-hunting
* IOC-analysis
* behavior-analysis
* malware-analysis
* defensive-validation

Zero Trust

* verify-identity
* verify-device
* verify-workload
* verify-context
* evaluate-policy
* enforce-least-privilege
* issue-capability
* revoke-capability
* segment-resource
* inspect-session
* continuous-evaluation
* record-decision

Sandbox / Isolation

* process-isolation
* filesystem-isolation
* network-isolation
* syscall-filtering
* namespace-isolation
* VM-isolation
* container-isolation
* browser-isolation
* language-runtime-isolation
* resource-limiting
* time-limiting
* capability-limiting
* secret-isolation
* output-sanitization
* hostile-code-execution

Testing

* unit-testing
* component-testing
* integration-testing
* contract-testing
* system-testing
* end-to-end-testing
* acceptance-testing
* regression-testing
* smoke-testing
* sanity-testing
* exploratory-testing
* snapshot-testing
* golden-testing
* property-testing
* fuzz-testing
* mutation-testing
* differential-testing
* metamorphic-testing
* compatibility-testing
* interoperability-testing
* localization-testing
* accessibility-testing

Performance

* benchmark
* profile
* flamegraph
* CPU-analysis
* memory-analysis
* GPU-analysis
* IO-analysis
* network-analysis
* latency-analysis
* throughput-analysis
* contention-analysis
* allocation-analysis
* cache-analysis
* query-analysis
* startup-analysis
* bundle-analysis
* optimize-runtime
* optimize-memory
* optimize-network
* optimize-storage
* optimize-cost

Reliability

* availability-analysis
* reliability-analysis
* fault-injection
* chaos-testing
* redundancy-design
* failover-testing
* backup-testing
* restore-testing
* disaster-recovery-testing
* retry-design
* timeout-design
* circuit-breaker-design
* graceful-degradation
* overload-protection
* capacity-testing
* recovery-time-testing
* recovery-point-testing

Observability

* instrument-code
* emit-logs
* emit-metrics
* emit-traces
* collect-logs
* collect-metrics
* collect-traces
* distributed-tracing
* profiling
* dashboarding
* alerting
* correlation
* anomaly-detection
* SLI-definition
* SLO-definition
* SLA-monitoring
* error-budget-management
* incident-timeline-generation

Debugging

* reproduce-failure
* minimize-reproducer
* inspect-stack
* inspect-core-dump
* inspect-memory
* inspect-registers
* inspect-heap
* inspect-thread
* inspect-process
* inspect-network
* inspect-database
* inspect-log
* inspect-trace
* breakpoint-debugging
* binary-search-debugging
* bisect-regression
* root-cause-analysis
* repair
* verify-repair

Compatibility

* OS-compatibility
* architecture-compatibility
* runtime-compatibility
* language-version-compatibility
* library-compatibility
* API-compatibility
* protocol-compatibility
* schema-compatibility
* data-format-compatibility
* browser-compatibility
* device-compatibility
* cloud-compatibility
* backward-compatibility
* forward-compatibility
* migration-compatibility

Migration

* assess-source
* assess-target
* map-components
* map-data
* map-interfaces
* transform-data
* transform-code
* transform-config
* migrate-schema
* migrate-infrastructure
* migrate-runtime
* migrate-service
* migrate-users
* dual-run
* verify-equivalence
* cutover
* rollback-migration
* decommission-source

Configuration

* configuration-authoring
* configuration-validation
* configuration-resolution
* configuration-templating
* environment-resolution
* configuration-diff
* configuration-migration
* configuration-policy
* configuration-secret-separation
* configuration-drift-detection

Secrets

* secret-generation
* secret-storage
* secret-injection
* secret-rotation
* secret-revocation
* secret-scanning
* secret-redaction
* secret-auditing
* secret-recovery

Policy

* policy-authoring
* policy-parsing
* policy-compilation
* policy-evaluation
* policy-enforcement
* policy-testing
* policy-simulation
* policy-diff
* policy-versioning
* policy-provenance
* policy-exception-management
* policy-audit

Standards / Compliance

* discover-standard
* ingest-standard
* parse-normative-language
* extract-requirements
* classify-requirements
* map-controls
* map-implementation
* map-tests
* map-evidence
* evaluate-conformance
* detect-nonconformance
* generate-control-matrix
* generate-evidence-package
* track-standard-version
* detect-standard-change
* impact-standard-change

Governance

* authority-check
* permission-check
* policy-check
* risk-check
* evidence-check
* qualification-check
* separation-of-duties-check
* approval-check
* signing-check
* provenance-check
* lifecycle-check
* release-check
* deployment-check
* exception-check
* audit-check

Evidence

* evidence-capture
* evidence-hash
* evidence-sign
* evidence-timestamp
* evidence-store
* evidence-index
* evidence-link
* evidence-query
* evidence-verify
* evidence-reproduce
* evidence-expire
* evidence-revoke
* evidence-package
* evidence-export

Provenance

* source-identification
* origin-tracking
* transformation-tracking
* dependency-tracking
* lineage-tracking
* author-tracking
* tool-tracking
* model-tracking
* environment-tracking
* version-tracking
* artifact-tracking
* decision-tracking

Qualification

* define-qualification-profile
* run-qualification
* assess-qualification
* record-pass
* record-fail
* record-unknown
* record-blocked
* record-not-run
* record-not-authorized
* record-insufficient-data
* record-expired
* requalify
* revoke-qualification
* qualification-reporting

Artifact Management

* artifact-create
* artifact-version
* artifact-hash
* artifact-sign
* artifact-store
* artifact-retrieve
* artifact-promote
* artifact-copy
* artifact-compare
* artifact-verify
* artifact-attest
* artifact-publish
* artifact-retire
* artifact-delete

Documentation

* generate-readme
* generate-reference
* generate-api-docs
* generate-architecture-docs
* generate-runbook
* generate-playbook
* generate-SOP
* generate-ADR
* generate-diagram
* generate-changelog
* generate-release-notes
* generate-tutorial
* generate-example
* update-documentation
* validate-documentation
* test-documentation

Knowledge

* ingest-knowledge
* extract-entities
* extract-relations
* resolve-entities
* link-entities
* classify-knowledge
* index-knowledge
* embed-knowledge
* retrieve-knowledge
* summarize-knowledge
* reconcile-knowledge
* version-knowledge
* validate-knowledge
* expire-knowledge

Memory

* write-memory
* read-memory
* index-memory
* retrieve-memory
* summarize-memory
* compress-memory
* merge-memory
* isolate-memory
* snapshot-memory
* restore-memory
* validate-memory
* version-memory
* expire-memory
* forget-memory

Tooling

* discover-tool
* inspect-tool
* select-tool
* configure-tool
* invoke-tool
* compose-tools
* validate-tool-output
* retry-tool
* cancel-tool
* sandbox-tool
* meter-tool
* audit-tool
* qualify-tool
* replace-tool

Capability Management

* discover-capability
* register-capability
* describe-capability
* classify-capability
* match-capability
* compose-capability
* authorize-capability
* invoke-capability
* observe-capability
* verify-capability
* qualify-capability
* version-capability
* deprecate-capability
* revoke-capability

Skill Management

* discover-skill
* register-skill
* parse-skill
* validate-skill
* classify-skill
* index-skill
* search-skill
* select-skill
* compose-skills
* parameterize-skill
* invoke-skill
* observe-skill
* test-skill
* benchmark-skill
* qualify-skill
* version-skill
* fork-skill
* repair-skill
* replace-skill
* deprecate-skill
* revoke-skill

Agent Management

* spawn-agent
* configure-agent
* constrain-agent
* authorize-agent
* route-agent
* delegate-agent
* supervise-agent
* observe-agent
* interrupt-agent
* steer-agent
* checkpoint-agent
* resume-agent
* clone-agent
* fork-agent
* merge-agent-output
* evaluate-agent
* qualify-agent
* terminate-agent
* archive-agent

Multi-Agent Coordination

* capability-routing
* task-routing
* work-allocation
* load-balancing
* flock-formation
* flock-splitting
* flock-merging
* hierarchy-formation
* peer-coordination
* delegation
* arbitration
* quorum
* consensus
* voting
* conflict-resolution
* redundancy
* diversity-routing
* cross-checking
* adversarial-review
* ensemble-synthesis

Model Management

* discover-model
* inspect-model
* select-model
* route-model
* load-model
* unload-model
* invoke-model
* constrain-model
* benchmark-model
* evaluate-model
* compare-models
* qualify-model
* monitor-model
* meter-model
* replace-model
* fallback-model
* ensemble-model
* version-model

Execution

* admit-work
* prepare-environment
* acquire-resources
* execute-command
* execute-script
* execute-program
* execute-build
* execute-test
* execute-workflow
* execute-job
* execute-container
* execute-vm
* execute-remote
* execute-sandbox
* execute-parallel
* execute-distributed
* observe-execution
* cancel-execution
* retry-execution
* checkpoint-execution
* resume-execution

Runtime Control

* start
* stop
* restart
* pause
* resume
* health-check
* readiness-check
* liveness-check
* supervise
* watchdog
* timeout
* retry
* backoff
* circuit-break
* throttle
* rate-limit
* scale-up
* scale-down
* failover
* rollback

Environment Management

* detect-platform
* detect-architecture
* detect-runtime
* detect-toolchain
* inspect-environment
* create-environment
* clone-environment
* configure-environment
* isolate-environment
* validate-environment
* snapshot-environment
* restore-environment
* destroy-environment

Resource Management

* CPU-allocation
* GPU-allocation
* memory-allocation
* storage-allocation
* network-allocation
* accelerator-allocation
* process-allocation
* worker-allocation
* quota-enforcement
* budget-enforcement
* priority-enforcement
* resource-reclamation

Cost

* cost-estimation
* cost-attribution
* cost-metering
* cost-budgeting
* cost-optimization
* compute-cost-analysis
* storage-cost-analysis
* network-cost-analysis
* model-cost-analysis
* tool-cost-analysis
* lifecycle-cost-analysis

Scheduling

* task-scheduling
* job-scheduling
* priority-scheduling
* dependency-scheduling
* deadline-scheduling
* resource-aware-scheduling
* affinity-scheduling
* locality-scheduling
* batch-scheduling
* preemptive-scheduling
* distributed-scheduling

Messaging / Events

* publish-message
* consume-message
* acknowledge-message
* retry-message
* dead-letter-message
* route-message
* filter-message
* transform-message
* deduplicate-message
* order-message
* replay-message
* persist-message
* schema-validate-message

Integration

* connector-development
* adapter-development
* wrapper-development
* bridge-development
* webhook-development
* protocol-integration
* API-integration
* event-integration
* database-integration
* identity-integration
* filesystem-integration
* cloud-integration
* tool-integration
* model-integration

Interoperability

* contract-mapping
* schema-mapping
* protocol-mapping
* type-mapping
* identifier-mapping
* semantic-mapping
* format-conversion
* compatibility-shimming
* capability-negotiation
* version-negotiation
* interoperability-testing

File / Format Processing

* text-read
* text-write
* binary-read
* binary-write
* JSON
* YAML
* TOML
* XML
* CSV
* TSV
* Markdown
* HTML
* PDF
* office-document
* image
* audio
* video
* archive
* compressed-data
* protocol-buffer
* message-pack
* columnar-data
* scientific-data
* CAD-data
* 3D-data

Serialization

* serialize
* deserialize
* encode
* decode
* compress
* decompress
* encrypt
* decrypt
* frame
* deframe
* canonicalize
* validate-format
* migrate-format

Media

* image-processing
* audio-processing
* video-processing
* speech-recognition
* speech-synthesis
* image-generation
* video-generation
* transcoding
* resizing
* compression
* metadata-extraction
* quality-analysis

Spatial / 3D

* geometry-processing
* mesh-processing
* point-cloud-processing
* scene-graph-processing
* coordinate-transform
* collision-detection
* ray-tracing
* rasterization
* rendering
* physics-integration
* spatial-indexing
* geospatial-processing

Scientific Computing

* experiment-definition
* simulation
* numerical-modeling
* parameter-sweep
* sensitivity-analysis
* uncertainty-quantification
* statistical-analysis
* reproducibility
* experiment-tracking
* scientific-visualization
* result-validation

Statistics

* descriptive-statistics
* inferential-statistics
* hypothesis-testing
* regression
* classification-analysis
* clustering-analysis
* Bayesian-analysis
* time-series-analysis
* anomaly-analysis
* distribution-fitting
* uncertainty-analysis
* causal-analysis

Optimization

* linear-optimization
* nonlinear-optimization
* integer-optimization
* combinatorial-optimization
* convex-optimization
* gradient-optimization
* evolutionary-optimization
* Bayesian-optimization
* multi-objective-optimization
* constraint-optimization
* search-space-pruning

Simulation

* discrete-event-simulation
* agent-based-simulation
* Monte-Carlo-simulation
* physical-simulation
* network-simulation
* workload-simulation
* fault-simulation
* traffic-simulation
* capacity-simulation

UI / UX

* information-architecture
* interaction-design
* interface-design
* component-design
* design-system
* responsive-design
* accessibility-design
* usability-testing
* visual-regression
* user-flow-modeling
* prototype-generation
* state-design
* error-state-design
* empty-state-design
* loading-state-design

Accessibility

* semantic-structure
* keyboard-access
* focus-management
* screen-reader-support
* contrast-validation
* captioning
* alternative-text
* motion-reduction
* accessibility-testing
* accessibility-audit

Localization

* string-extraction
* translation-management
* locale-formatting
* date-formatting
* number-formatting
* currency-formatting
* pluralization
* RTL-support
* locale-testing
* translation-validation

Quality

* code-quality-analysis
* maintainability-analysis
* complexity-analysis
* duplication-analysis
* lint-quality
* architecture-quality
* dependency-quality
* test-quality
* documentation-quality
* data-quality
* model-quality
* operational-quality

Lifecycle

* ideation
* discovery
* specification
* design
* implementation
* integration
* verification
* validation
* qualification
* release
* deployment
* operation
* monitoring
* maintenance
* upgrade
* migration
* deprecation
* retirement
* archival
* destruction

Change Management

* detect-change
* classify-change
* scope-change
* impact-change
* approve-change
* implement-change
* test-change
* qualify-change
* release-change
* deploy-change
* observe-change
* rollback-change
* document-change

Incident Management

* detect-incident
* classify-incident
* triage-incident
* contain-incident
* investigate-incident
* remediate-incident
* recover-service
* validate-recovery
* communicate-incident
* postmortem
* create-followups
* verify-followups

Operations Management

* runbook-execution
* maintenance
* patching
* upgrading
* scaling
* backup
* restore
* rotation
* failover
* capacity-management
* availability-management
* service-management
* dependency-management
* inventory-management

Product

* problem-definition
* user-needs-analysis
* feature-definition
* value-proposition
* product-requirements
* roadmap
* prioritization
* experiment-design
* adoption-analysis
* retention-analysis
* product-metrics
* release-management

Project / Program

* project-initiation
* work-breakdown
* dependency-management
* milestone-management
* schedule-management
* resource-management
* risk-management
* issue-management
* decision-management
* status-reporting
* change-control
* closure

Business

* business-modeling
* market-analysis
* competitive-analysis
* pricing-analysis
* unit-economics
* financial-modeling
* revenue-modeling
* cost-modeling
* procurement
* vendor-management
* contract-analysis
* operations-design
* organizational-design
* KPI-definition

Legal / IP Support

* license-identification
* license-compatibility
* attribution-tracking
* copyright-inventory
* patent-landscape-support
* trademark-inventory
* contract-clause-extraction
* data-rights-tracking
* usage-rights-validation
* export-control-screening
* retention-policy-mapping

Privacy

* data-inventory
* data-classification
* PII-detection
* minimization
* pseudonymization
* anonymization
* consent-management
* purpose-limitation
* retention-management
* deletion
* access-request-support
* privacy-impact-analysis
* privacy-testing

Supply Chain

* dependency-inventory
* SBOM-generation
* SBOM-validation
* provenance-validation
* build-provenance
* artifact-provenance
* supplier-analysis
* dependency-risk
* package-integrity
* signature-verification
* reproducible-build-verification

Audit

* event-capture
* decision-capture
* change-capture
* access-capture
* tool-use-capture
* model-use-capture
* evidence-capture
* immutable-recording
* audit-query
* audit-correlation
* audit-export
* audit-verification

Recovery

* checkpoint
* snapshot
* backup
* restore
* rollback
* roll-forward
* replay
* reconstruct
* failover
* disaster-recovery
* state-reconciliation
* consistency-repair

Optimization / Learning

* collect-feedback
* evaluate-result
* compare-result
* detect-regression
* detect-improvement
* update-routing
* update-priorities
* update-skill-selection
* update-tool-selection
* update-model-selection
* create-regression-test
* create-failure-case
* create-success-case
* retain-lessons

⸻

03. UNIVERSAL AGENT EXECUTION OPERATIONS

* identify
* advertise-capabilities
* inspect-capabilities
* admit
* reject
* constrain
* authorize
* decompose
* select-skills
* compose-skills
* select-tools
* select-models
* plan
* schedule
* allocate
* route
* delegate
* execute
* observe
* measure
* inspect
* compare
* diagnose
* repair
* retry
* rollback
* verify
* validate
* qualify
* attest
* record-evidence
* report
* checkpoint
* suspend
* resume
* cancel
* terminate
* release-resources
* archive

04. SKILL GRANULARITY

* Atomic
* Primitive
* Composite
* Procedure
* Workflow
* Pipeline
* Role
* Profession
* Domain
* System
* System-of-Systems

05. SKILL CONTRACT FIELDS

* identifier
* version
* description
* capability
* domain
* subdomain
* operation
* intent-types
* input-types
* output-types
* preconditions
* postconditions
* invariants
* parameters
* defaults
* dependencies
* required-skills
* optional-skills
* incompatible-skills
* tools
* engines
* runtimes
* models
* platforms
* architectures
* environments
* permissions
* authorities
* resource-limits
* time-limits
* cost-limits
* network-policy
* filesystem-policy
* secret-policy
* data-policy
* procedures
* branches
* checkpoints
* cancellation
* retries
* rollback
* recovery
* expected-failures
* known-failures
* failure-classes
* diagnostics
* tests
* regression-tests
* benchmarks
* evidence-requirements
* evidence-produced
* provenance
* qualification
* compatibility
* portability
* determinism
* idempotency
* reversibility
* observability
* security-properties
* safety-properties
* privacy-properties
* compliance-mappings
* standards-mappings
* known-successes
* known-limitations
* deprecation-state
* replacement
* owner
* maintainer
* created-at
* updated-at
* signature
* checksum

06. ROUTING DIMENSIONS

* intent
* capability
* skill
* operation
* domain
* target
* artifact-type
* input-type
* output-type
* language
* framework
* runtime
* operating-system
* processor-architecture
* accelerator
* environment
* locality
* connectivity
* authority
* permission
* security-classification
* trust-level
* evidence-level
* qualification-level
* compatibility
* latency
* throughput
* cost
* energy
* memory
* storage
* network
* reliability
* determinism
* reversibility
* risk
* availability
* specialization
* historical-success
* current-load
* resource-fit

07. RESULT STATES

* PASS
* FAIL
* PARTIAL
* UNKNOWN
* NOT_RUN
* BLOCKED
* NOT_AUTHORIZED
* UNSUPPORTED
* INCOMPATIBLE
* INSUFFICIENT_DATA
* INSUFFICIENT_EVIDENCE
* TIMEOUT
* CANCELLED
* RESOURCE_EXHAUSTED
* POLICY_DENIED
* SECURITY_DENIED
* QUALIFICATION_DENIED
* DEPENDENCY_FAILURE
* ENVIRONMENT_FAILURE
* TOOL_FAILURE
* MODEL_FAILURE
* EXECUTION_FAILURE
* VERIFICATION_FAILURE
* EXPIRED
* DEPRECATED

08. UNIVERSAL FLOW

* Interpret
* Parse
* Normalize
* Reconcile
* Mirror
* Formalize
* Discover
* Decompose
* Map
* Search
* Select
* Compose
* Plan
* Constrain
* Authorize
* Allocate
* Execute
* Observe
* Diagnose
* Repair
* Test
* Verify
* Validate
* Qualify
* Attest
* Evidence
* Release
* Deploy
* Operate
* Monitor
* Learn
ATLAS

echo "atlas written: $(wc -l < data/atlas/atlas.txt) lines"

# =========================================================
# STEP 2 — write the executable system (parse + contracts + tools + dispatch + cli)
# =========================================================
cat > src/parse_atlas.py <<'PY'
import json, re, sqlite3, sys
from pathlib import Path
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "data/atlas/atlas.txt")
OUT_JSONL = Path("data/atlas/atlas.jsonl"); OUT_DB = Path("data/atlas/atlas.sqlite")
SECTION_RE = re.compile(r"^(\d{2})\.\s+(.+?)\s*$")
BULLET_RE  = re.compile(r"^\*\s+(.+?)\s*$")
HEADER_RE  = re.compile(r"^[A-Z][A-Za-z0-9 /&\-]+$")
KIND = {"01":"role","02":"skill","03":"operation","04":"granularity",
        "05":"contract_field","06":"routing_dim","07":"result_state","08":"flow_step"}
def slugify(s): return re.sub(r"[^a-z0-9]+","-",s.lower().strip()).strip("-")
def parse(path):
    out, section, sub, num = [], None, None, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line.strip(): continue
        m = SECTION_RE.match(line)
        if m and len(m.group(1))==2: num, section, sub = m.group(1), line.strip(), None; continue
        if (not line.startswith("*")) and HEADER_RE.match(line.strip()) \
           and len(line.strip())<=60 and not line.strip().endswith("."):
            sub = line.strip(); continue
        b = BULLET_RE.match(line)
        if b:
            name=b.group(1).strip()
            out.append({"id":f"{num}:{slugify(sub or 'root')}:{slugify(name)}",
                        "kind":KIND.get(num,"unknown"),"section":section,"subsection":sub,
                        "name":name,"slug":slugify(name),"text":name})
    return out
def write_jsonl(recs,p):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("w",encoding="utf-8") as f:
        for r in recs: f.write(json.dumps(r,ensure_ascii=False)+"\n")
def write_db(recs,p):
    if p.exists(): p.unlink()
    con=sqlite3.connect(p)
    con.executescript("""CREATE TABLE items(id TEXT PRIMARY KEY, kind TEXT, section TEXT,
        subsection TEXT, name TEXT, slug TEXT, text TEXT);
        CREATE INDEX i_kind ON items(kind);
        CREATE VIRTUAL TABLE items_fts USING fts5(name,text,subsection,
        content='items',content_rowid='rowid');""")
    con.executemany("INSERT INTO items VALUES(?,?,?,?,?,?,?)",
        [(r["id"],r["kind"],r["section"],r["subsection"],r["name"],r["slug"],r["text"]) for r in recs])
    con.execute("INSERT INTO items_fts(rowid,name,text,subsection) SELECT rowid,name,text,subsection FROM items")
    con.commit(); con.close()
if __name__=="__main__":
    if not SRC.exists(): sys.exit(f"input not found: {SRC}")
    recs=parse(SRC); write_jsonl(recs,OUT_JSONL); write_db(recs,OUT_DB)
    from collections import Counter
    print(f"parsed {len(recs)} items -> {OUT_JSONL}, {OUT_DB}")
    for k,v in sorted(Counter(r['kind'] for r in recs).items()): print(f"  {k:16} {v}")
PY

cat > src/contracts.py <<'PY'
from dataclasses import dataclass, field, asdict
from enum import Enum
class ResultState(str, Enum):
    PASS="PASS"; FAIL="FAIL"; PARTIAL="PARTIAL"; UNKNOWN="UNKNOWN"; NOT_RUN="NOT_RUN"
    BLOCKED="BLOCKED"; NOT_AUTHORIZED="NOT_AUTHORIZED"; UNSUPPORTED="UNSUPPORTED"
    INCOMPATIBLE="INCOMPATIBLE"; INSUFFICIENT_DATA="INSUFFICIENT_DATA"
    INSUFFICIENT_EVIDENCE="INSUFFICIENT_EVIDENCE"; TIMEOUT="TIMEOUT"; CANCELLED="CANCELLED"
    RESOURCE_EXHAUSTED="RESOURCE_EXHAUSTED"; POLICY_DENIED="POLICY_DENIED"
    SECURITY_DENIED="SECURITY_DENIED"; QUALIFICATION_DENIED="QUALIFICATION_DENIED"
    DEPENDENCY_FAILURE="DEPENDENCY_FAILURE"; ENVIRONMENT_FAILURE="ENVIRONMENT_FAILURE"
    TOOL_FAILURE="TOOL_FAILURE"; MODEL_FAILURE="MODEL_FAILURE"
    EXECUTION_FAILURE="EXECUTION_FAILURE"; VERIFICATION_FAILURE="VERIFICATION_FAILURE"
    EXPIRED="EXPIRED"; DEPRECATED="DEPRECATED"
@dataclass
class SkillContract:
    identifier: str; version: str="0.0.1"; description: str=""; capability: str=""
    domain: str=""; operation: str=""
    input_types: dict=field(default_factory=dict); output_types: dict=field(default_factory=dict)
    preconditions: list=field(default_factory=list); postconditions: list=field(default_factory=list)
    permissions: list=field(default_factory=list); retries: dict=field(default_factory=dict)
    rollback: str="none"; evidence_produced: list=field(default_factory=list)
    result_states: list=field(default_factory=lambda:[s.value for s in ResultState])
    impl: str=""
    def as_dict(self): return asdict(self)
def validate_contract(c):
    e=[]
    if not c.identifier: e.append("identifier required")
    if not c.impl: e.append(f"{c.identifier}: no impl bound")
    for s in c.result_states:
        if s not in {r.value for r in ResultState}: e.append(f"bad state {s!r}")
    return e
def normalize_result(x):
    if isinstance(x,ResultState): return x
    if isinstance(x,str) and x in {r.value for r in ResultState}: return ResultState(x)
    if isinstance(x,dict):
        for k in ("result_state","result","state","status"):
            if k in x: return normalize_result(x[k])
    return ResultState.FAIL
PY

cat > src/tools.py <<'PY'
import hashlib, json, subprocess, time
from pathlib import Path
from .contracts import ResultState
REG={}
def register(name, schema=None):
    def deco(fn): REG[name]={"fn":fn,"schema":schema or {}}; return fn
    return deco
def call(name, inputs, ctx):
    if name not in REG: return {"result_state":ResultState.TOOL_FAILURE.value,"reason":f"unbound tool: {name}"}
    try:
        o=REG[name]["fn"](inputs or {}, ctx or {})
        if not isinstance(o,dict): o={"result":o}
        o.setdefault("result_state", ResultState.PASS.value); return o
    except TimeoutError: return {"result_state":ResultState.TIMEOUT.value}
    except PermissionError: return {"result_state":ResultState.POLICY_DENIED.value}
    except FileNotFoundError as e: return {"result_state":ResultState.ENVIRONMENT_FAILURE.value,"reason":str(e)}
    except Exception as e: return {"result_state":ResultState.EXECUTION_FAILURE.value,"reason":str(e)}
@register("filesystem-search", {"pattern":"string","root":"path"})
def filesystem_search(i,ctx):
    root=Path(i.get("root",".")).expanduser(); pat=i.get("pattern","*")
    hits=[str(p) for p in root.rglob(pat)][:500]
    return {"result_state":ResultState.PASS.value,"matches":hits,"count":len(hits)}
@register("regex-search", {"pattern":"string","path":"path"})
def regex_search(i,ctx):
    import re
    pat=re.compile(i["pattern"]); p=Path(i.get("path",".")).expanduser(); hits=[]
    files=[p] if p.is_file() else list(p.rglob("*"))
    for f in files:
        if not f.is_file(): continue
        try:
            for n,l in enumerate(f.read_text(errors="ignore").splitlines(),1):
                if pat.search(l): hits.append({"file":str(f),"line":n,"text":l})
        except Exception: pass
        if len(hits)>=500: break
    return {"result_state":ResultState.PASS.value,"matches":hits,"count":len(hits)}
@register("execute-command", {"argv":"list[string]","timeout_s":"int"})
def execute_command(i,ctx):
    argv=i["argv"]
    if not isinstance(argv,list) or not argv:
        return {"result_state":ResultState.INSUFFICIENT_DATA.value,"reason":"argv required"}
    t=int(i.get("timeout_s",10))
    try: r=subprocess.run(argv,capture_output=True,text=True,timeout=t)
    except subprocess.TimeoutExpired: return {"result_state":ResultState.TIMEOUT.value}
    return {"result_state":(ResultState.PASS if r.returncode==0 else ResultState.EXECUTION_FAILURE).value,
            "returncode":r.returncode,"stdout":r.stdout[:8000],"stderr":r.stderr[:8000]}
@register("evidence-hash", {"path":"path","algo":"string"})
def evidence_hash(i,ctx):
    p=Path(i["path"]).expanduser(); h=hashlib.new(i.get("algo","sha256"))
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1<<20), b""): h.update(c)
    return {"result_state":ResultState.PASS.value,"digest":h.hexdigest()}
@register("evidence-capture", {"payload":"json"})
def evidence_capture(i,ctx):
    log=Path(ctx.get("evidence_log","evidence.log"))
    with log.open("a",encoding="utf-8") as f:
        f.write(json.dumps({"ts":time.time(),"payload":i.get("payload")},ensure_ascii=False)+"\n")
    return {"result_state":ResultState.PASS.value,"recorded":str(log)}
@register("policy-check", {"permissions":"list[string]","required":"list[string]"})
def policy_check(i,ctx):
    missing=sorted(set(i.get("required",[]))-set(i.get("permissions",[])))
    return {"result_state":(ResultState.POLICY_DENIED if missing else ResultState.PASS).value,"missing":missing}
@register("authority-check", {"actor":"string","authorities":"list[string]","required":"list[string]"})
def authority_check(i,ctx):
    missing=sorted(set(i.get("required",[]))-set(i.get("authorities",[])))
    return {"result_state":(ResultState.NOT_AUTHORIZED if missing else ResultState.PASS).value,"missing":missing}
PY

cat > src/dispatch.py <<'PY'
import json, sqlite3
from pathlib import Path
from .contracts import ResultState, SkillContract, normalize_result, validate_contract
from . import tools
DB=Path("data/atlas/atlas.sqlite"); SK=Path("data/skills.sqlite"); EV=Path("evidence.log")
def route(query, limit=10):
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
    rows=con.execute("SELECT i.id,i.kind,i.section,i.subsection,i.name,i.slug "
        "FROM items_fts f JOIN items i ON i.rowid=f.rowid WHERE items_fts MATCH ? "
        "ORDER BY rank LIMIT ?", (" OR ".join(query.split()), limit)).fetchall()
    con.close(); return [dict(r) for r in rows]
def init():
    if SK.exists(): return
    con=sqlite3.connect(SK); con.execute("CREATE TABLE skills(id TEXT PRIMARY KEY,contract TEXT)")
    con.commit(); con.close()
def bind(c):
    init(); e=validate_contract(c)
    if e: raise ValueError("; ".join(e))
    con=sqlite3.connect(SK); con.execute("INSERT OR REPLACE INTO skills VALUES(?,?)",(c.identifier,json.dumps(c.as_dict())))
    con.commit(); con.close()
def get(sid):
    init(); con=sqlite3.connect(SK); r=con.execute("SELECT contract FROM skills WHERE id=?",(sid,)).fetchone(); con.close()
    return SkillContract(**json.loads(r[0])) if r else None
def _check(inp,spec):
    b=[]
    for k,t in spec.items():
        if k not in inp: b.append(f"missing {k}"); continue
        v=inp[k]; ok=(t=="string" and isinstance(v,str)) or (t=="int" and isinstance(v,int)) \
          or (t=="list[string]" and isinstance(v,list) and all(isinstance(x,str) for x in v)) \
          or (t in ("json","obj") and isinstance(v,(dict,list))) or (t=="path" and isinstance(v,str))
        if not ok: b.append(f"{k} must be {t}")
    return b
def dispatch(sid, inputs, ctx=None, retries=None):
    ctx=dict(ctx or {}); ctx.setdefault("evidence_log", str(EV))
    c=get(sid)
    if c is None: return {"result_state":ResultState.NOT_RUN.value,"reason":f"skill not bound: {sid}"}
    e=_check(inputs,c.input_types)
    if e: return {"result_state":ResultState.INSUFFICIENT_DATA.value,"errors":e}
    if c.permissions:
        p=tools.call("policy-check",{"permissions":ctx.get("permissions",[]),"required":c.permissions},ctx)
        if p["result_state"]!=ResultState.PASS.value:
            return {"result_state":ResultState.POLICY_DENIED.value,"policy":p}
    a=0; mx=1+(retries if retries is not None else int(c.retries.get("max",0))); last=None
    while a<mx:
        a+=1; last=tools.call(c.impl,inputs,ctx); st=normalize_result(last)
        if st==ResultState.PASS or st.value not in set(c.retries.get("on",[])): break
    out=dict(last or {}); out["result_state"]=normalize_result(out).value
    out["skill"]=c.identifier; out["attempts"]=a
    for ev in c.evidence_produced:
        tools.call("evidence-capture",{"payload":{"skill":c.identifier,"evidence":ev,"result_state":out["result_state"]}},ctx)
    return out
PY

cat > src/seed_skills.py <<'PY'
import sqlite3
from .contracts import SkillContract, ResultState
from . import dispatch
IMPL={"filesystem-search":"filesystem-search","regex-search":"regex-search",
      "execute-command":"execute-command","evidence-hash":"evidence-hash",
      "evidence-capture":"evidence-capture","policy-check":"policy-check",
      "authority-check":"authority-check"}
def main():
    con=sqlite3.connect("data/atlas/atlas.sqlite"); con.row_factory=sqlite3.Row
    rows=con.execute("SELECT * FROM items WHERE kind='skill'").fetchall(); con.close()
    n=nb=0
    for r in rows:
        n+=1; impl=IMPL.get(r["slug"],"")
        c=SkillContract(identifier=r["slug"],description=f"{r['name']} ({r['subsection']})",
            capability=r["subsection"] or "",domain=r["section"] or "",operation=r["slug"].split("-")[0],
            output_types={"result_state":"string"},result_states=[s.value for s in ResultState],
            impl=impl,evidence_produced=["skill_result"])
        try: dispatch.bind(c)
        except Exception as e: print(f"skip {r['slug']}: {e}")
        nb += 1 if impl else 0
    print(f"seeded {n} skills, {nb} bound to tools")
PY

cat > src/cli.py <<'PY'
import argparse, json, sqlite3, sys
from . import dispatch, tools, seed_skills
def main(argv=None):
    ap=argparse.ArgumentParser(prog="atlas"); sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("seed")
    r=sub.add_parser("route"); r.add_argument("query"); r.add_argument("--limit",type=int,default=10)
    d=sub.add_parser("dispatch"); d.add_argument("skill"); d.add_argument("--inputs",default="{}")
    l=sub.add_parser("list"); l.add_argument("--kind",default="skill"); l.add_argument("--limit",type=int,default=30)
    sub.add_parser("tools")
    a=ap.parse_args(argv)
    if a.cmd=="seed": seed_skills.main()
    elif a.cmd=="route": print(json.dumps(dispatch.route(a.query,a.limit),indent=2))
    elif a.cmd=="dispatch": print(json.dumps(dispatch.dispatch(a.skill,json.loads(a.inputs)),indent=2))
    elif a.cmd=="list":
        con=sqlite3.connect("data/atlas/atlas.sqlite"); con.row_factory=sqlite3.Row
        for r in con.execute("SELECT slug,subsection,name FROM items WHERE kind=? LIMIT ?",(a.kind,a.limit)):
            print(f"{r['slug']:40} {r['subsection'] or '':30} {r['name']}")
    elif a.cmd=="tools": print("\n".join(sorted(tools.REG)))
    return 0
if __name__=="__main__": sys.exit(main())
PY

touch src/__init__.py
echo "files written"

# =========================================================
# STEP 3 — build + smoke-test
# =========================================================
python src/parse_atlas.py data/atlas/atlas.txt
rm -f data/skills.sqlite evidence.log
python -m src.cli seed
echo; echo "== tools ==";          python -m src.cli tools
echo; echo "== route ==";          python -m src.cli route "security evidence qualification" --limit 5
echo; echo "== bound skill ==";    python -m src.cli dispatch filesystem-search --inputs '{"pattern":"*.py","root":"src"}'
echo; echo "== unbound skill ==";  python -m src.cli dispatch qualify-capability --inputs '{}'
echo; echo "== missing inputs =="; python -m src.cli dispatch execute-command --inputs '{}'
echo; echo "== tree =="; find . -maxdepth 2 -not -path './.venv*' -not -path './__pycache__*' \( -type d -o -type f \) | sort | sed 's|^\./||'
