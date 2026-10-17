# boot.S — entry point
.global _start
_start:
    movq $dispatch_table, %rdi
    call _dispatch
    movq %rax, %rdi
    movq $60, %rax
    syscall
