# Project: Advance

Plenty more, ranging from approachable to genuinely advanced. Grouped by flavour. Unlike the other projects in this repo, several of these work at the kernel/systems level — always do this work inside a disposable VM you control, not on real hardware or anything with data on it: custom kernels, kernel modules, and exploit labs can crash or corrupt a system.

## Kernel internals

*Hands-on with how the kernel works.*

- **Compile a custom kernel** — download the mainline source, configure, build, and boot it. Then strip it down or turn on a hardening option and measure the difference. Teaches the whole build pipeline.
- **Loadable kernel module that intercepts syscalls** — a classic learning exercise showing how rootkits hook the syscall table (do it observationally, e.g. logging file opens, not maliciously). Big "aha" for understanding kernel-level attacks.
- **/proc or /dev driver** — expose custom data through a virtual file. Reinforces the "everything is a file" model and kernel/user boundary.
- **Kernel debugging with QEMU + GDB** — boot a kernel in QEMU and step through it with a debugger. Serious systems skill that stands out.

## Sandboxing & isolation

*Very cyber-relevant.*

- **seccomp-bpf filter** — write a filter that whitelists syscalls for a program and watch it get killed when it steps out of line. Directly relevant to how browsers and containers sandbox untrusted code.
- **AppArmor / SELinux profile** — confine a real application and demonstrate blocking an exploit path. Mandatory access control is core defensive knowledge.
- **Landlock** — a newer, unprivileged sandboxing API; using it shows you follow current kernel development.
- **Namespaces + cgroups deep dive** — extend the "container from scratch" idea into resource limits and network namespaces.

## Memory safety & exploitation

*Advanced — the offensive side.*

- **Buffer overflow lab** — compile a deliberately vulnerable C program with protections off, then exploit it in a VM. Re-enable ASLR, stack canaries, NX and watch the exploit fail. This single project teaches why modern mitigations exist — enormously valuable understanding.
- **Return-oriented programming intro** — the next step up once overflows click.
- **Explore KASLR / SMEP / SMAP** — write up how these kernel hardening features work.

## Observability & detection

- **eBPF security monitor** — use bcc or bpftrace to detect suspicious behaviour (unexpected execve, connections to odd ports). Genuinely in-demand industry skill.
- **auditd rules** — configure the Linux audit system to log security-relevant events and analyse the output.
- **Build a tiny "process monitor" reading from /proc** — approachable, all user-space, but teaches what the kernel exposes.

## Boot & integrity

- **Secure Boot + measured boot** — explore how the chain of trust works from firmware upward.
- **dm-verity / read-only rootfs** — set up a tamper-evident filesystem.
