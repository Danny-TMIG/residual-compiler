# dispatch.S
.global _dispatch
_dispatch:
    pushq %rbp
    movq %rsp, %rbp
    call _ingress
    call _egress
    call _lateral
    call _federated
    popq %rbp
    ret
