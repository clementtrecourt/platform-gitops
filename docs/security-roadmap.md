# Security roadmap & known limits

Honest status of the platform's security posture (what is done, what is deliberately deferred).

| Area | Status | Next step |
|------|--------|-----------|
| Admission policy | Enforce: resources, non-root, no privileged. Audit: no `:latest`, drop ALL caps | Fix reported workloads, then flip to Enforce |
| Secrets | Lab credentials are still plaintext in manifests (Backstage/Postgres/Grafana) | Sealed Secrets or SOPS+age, rotate values, purge git history |
| Supply chain | Trivy + SBOM in CI | Pin actions by SHA, Cosign signing + Kyverno `verifyImages` |
| Network | No NetworkPolicies outside ArgoCD | default-deny per namespace + explicit allows |
| Exposure | HTTP `nip.io` ingresses, Ollama unauthenticated | cert-manager TLS, oauth2-proxy |
| Availability | Single node, no backup | Velero / pg_dump CronJob, second node |
| SRE agent | Deterministic fix (OOM only), LLM = RCA text | More incident classes, eval on simulated incidents |
