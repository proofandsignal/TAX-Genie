# BUILD-020 — Secure PDF ingress preflight, phase 1

The existing pilot already runs a bounded PDF subprocess and uses a fail-closed scanner interface. Neither constitutes a hardened OS sandbox or a production-grade malware scanning integration.

This phase adds a deterministic, testable **preflight policy** for synthetic PDFs:
- explicit PDF filename extension and no path separators or NUL;
- bounded content size using existing MAX_BYTES;
- PDF version header check;
- rejection of invalid metadata before scanner invocation;
- a composed helper that only returns true when an explicitly configured scanner returns literal `True`.

## Security limitations

A correct PDF header is not proof a file is valid, benign, or parseable. The private-pilot FastAPI upload route now invokes preflight and verified scanning before calling the existing `IntakeStore.add_pdf` path. No public Cloudflare Worker route has been enabled. The pilot scanner remains intentionally unconfigured by default, so uploads continue to fail closed. This integration is not a production-safe upload service. Scanner implementations, cloud queue, hardened isolation, decompression and parser resource budgets require separate implementation and review.

**No real customer invoices, live uploads, Cloudflare deployment, D1/R2 provisioning or merge approved by this phase.**

## Subprocess lifecycle review
- Replaced the multiprocessing queue with a one-way pipe: the parent receives the bounded extraction result before joining the process, avoiding queue feeder deadlock when text is large.
- Worker closes its pipe and the parent always closes both ends and reaps/terminates the process.
- The PDF reader still runs in a normal child process with inherited host access; there is **no** hardened OS sandbox, memory/CPU cgroup limit, network disablement, antivirus implementation, or validated isolation boundary.
- The bounded parser tests use generated synthetic PDFs only; full adversarial fuzzing and independent review are outstanding.
