# parse.S
.global _parse
_parse:
    pushq %rbp
    movq %rsp, %rbp
    movq (%rdi), %rax
    cmpb $0x7b, %al
    je .Lok
    xorq %rax, %rax
    popq %rbp
    ret
.Lok:
    movq $1, %rax
    popq %rbp
    ret
