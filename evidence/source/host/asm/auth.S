# auth.S
.global _auth
_auth:
    movq $1, %rax
    ret
