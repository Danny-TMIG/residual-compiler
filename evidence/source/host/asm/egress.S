# egress.S — down
.global _egress
_egress:
    pushq %rbp
    movq %rsp, %rbp
    call _serialize
    call _sign
    call _audit
    movq $200, %rax
    popq %rbp
    ret
