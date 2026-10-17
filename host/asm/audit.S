# audit.S
.global _audit
_audit:
    movq $1, %rax
    syscall
    ret
