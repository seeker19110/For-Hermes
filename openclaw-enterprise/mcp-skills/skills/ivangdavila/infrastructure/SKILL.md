---
name: Infrastructure
description: "Design, provision, and connect cloud resources across servers, networks, and services."
---

## Scope

This skill covers **architecture and orchestration** — how pieces fit together.
For individual components, use dedicated skills: `server`, `docker`, `ci-cd`, `ssl`, `monitoring`.

## When to Use

- Planning architecture for a new project
- Provisioning VPS/cloud resources programmatically
- Networking: firewalls, VPNs, load balancers, DNS routing
- Infrastructure as Code (Terraform, Pulumi)
- Connecting services across multiple servers
- Backup strategies and disaster recovery
- Cost analysis and optimization

## Decision Framework

| Question | This skill? |
|----------|-------------|
| "How do I structure infra for this project?" | ✅ Yes |
| "Should I add another server or scale this one?" | ✅ Yes |
| "How do I connect services across servers?" | ✅ Yes |
| "How do I configure nginx?" | ❌ Use `server` |
| "How do I write a Dockerfile?" | ❌ Use `docker` |
| "How do I set up GitHub Actions?" | ❌ Use `ci-cd` |

## Architecture Patterns

| Stage | Recommended Setup |
|-------|-------------------|
| MVP (<1K users) | Single VPS, Docker Compose, managed DB optional |
| Growth (1K-50K) | Dedicated DB, load balancer, separate workers |
| Scale (50K+) | Multi-region, auto-scaling, CDN, managed services |

For detailed patterns per stage, see `patterns.md`.

## Cloud Provider Quick Reference

| Task | Hetzner | AWS | DigitalOcean |
|------|---------|-----|--------------|
| Create server | `hcloud server create` | `aws ec2 run-instances` | `doctl compute droplet create` |
| Firewall | Cloud Firewall | Security Groups | Cloud Firewall |
| DNS | External (Cloudflare) | Route53 | Domains |
| Load balancer | Load Balancer | ALB/NLB | Load Balancer |

For provider-specific commands, see `providers.md`.

## Networking Essentials

- **Firewall:** Default deny, explicit allow. Open only needed ports.
- **VPN:** WireGuard for server-to-server. Tailscale for quick setup.
- **DNS:** Cloudflare for most cases. Low TTL during migrations.
- **Load balancing:** Start with reverse proxy (Caddy/Traefik). Add LB when needed.

## Backup Strategy

| Data Type | Method | Frequency |
|-----------|--------|-----------|
| Database | pg_dump + S3/B2 | Daily + before changes |
| Volumes | Snapshots | Weekly |
| Config | Git (IaC) | Every change |

For backup scripts and restore procedures, see `backups.md`.

## Cost Optimization

- Right-size instances (most apps need less than you think)
- Use reserved instances for stable workloads (30-50% savings)
- Spot/preemptible for batch jobs
- Monitor egress — it's often the hidden cost
- Hetzner/OVH for predictable pricing vs hyperscalers
