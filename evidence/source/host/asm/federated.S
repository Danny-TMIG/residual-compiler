# federated.S — right
.global _federated
_federated:
    pushq %rbp
    movq %rsp, %rbp
    call _oidc_verify
    testq %rax, %rax
    jz .Lfed401
    movq $200, %rax
    popq %rbp
    ret
.Lfed401:
    movq $401, %rax
    popq %rbp
    ret
