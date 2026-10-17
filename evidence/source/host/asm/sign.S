# sign.S
.global _sign
_sign:
    xorq %rax, %rax
.L:
    movzbq (%rdi), %rdx
    addq %rdx, %rax
    incq %rdi
    decq %rsi
    jnz .L
    ret
