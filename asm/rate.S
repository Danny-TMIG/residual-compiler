# rate.S
.global _rate
_rate:
    movq (%rdi), %rax
    testq %rax, %rax
    jz .Lthr
    decq (%rdi)
    movq $1, %rax
    ret
.Lthr:
    xorq %rax, %rax
    ret
