# lateral.S — left
.global _lateral
_lateral:
    pushq %rbp
    movq %rsp, %rbp
    call _parse_peer
    testq %rax, %rax
    jz .Ldrop
    movq $0, %rax
    popq %rbp
    ret
.Ldrop:
    movq $1, %rax
    popq %rbp
    ret
