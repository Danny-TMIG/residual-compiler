# ingress.S — up
.global _ingress
_ingress:
    pushq %rbp
    movq %rsp, %rbp
    call _parse
    testq %rax, %rax
    jz .Lreject400
    call _auth
    testq %rax, %rax
    jz .Lreject401
    call _rate
    testq %rax, %rax
    jz .Lreject429
    movq $200, %rax
    popq %rbp
    ret
.Lreject400:
    movq $400, %rax
    popq %rbp
    ret
.Lreject401:
    movq $401, %rax
    popq %rbp
    ret
.Lreject429:
    movq $429, %rax
    popq %rbp
    ret
