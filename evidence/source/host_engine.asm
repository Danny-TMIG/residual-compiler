// ====================================================================================
// NATIVE HOST ENGINE FOR APPLE SILICON M4 MAX (ARM64 / macOS POSIX TARGET)
// ====================================================================================

.global _main
.align 4

_main:
    // STEP 1: ALLOCATE NATIVE MEMORY WITH JIT PERMISSIONS VIA MMAP (0x20000C5)
    mov     x0, #0                  // NULL address pointer selection
    mov     x1, #4096               // Allocating 4KB hardware page
    mov     x2, #7                  // PROT_READ | PROT_WRITE | PROT_EXEC
    mov     w3, #0x1802             // MAP_ANON | MAP_PRIVATE | MAP_JIT
    mov     x4, #-1                 // No backing file descriptor
    mov     x5, #0                  // Zero file offset alignment

    movz    x16, #0x00C5
    movk    x16, #0x0200, lsl #16   // Construct 0x20000C5 class prefix value into X16
    svc     #0x80                   // Trigger Supervisor Call

    b.cs    _error_exit             // Check Carry Flag for system call failure
    mov     x10, x0                 // Save memory base address pointer

    // STEP 2: INJECT REAL MACHINE OPS DIRECTLY INTO SILICON CHANNELS
    //   mov x0, #42       (Hex packet word: 0xd2800540)
    //   ret               (Hex packet word: 0xd65f03c0)
    mov     w11, #0x0540
    movk    w11, #0xd280, lsl #16   // Construct 32-bit instruction word: mov x0, #42
    str     w11, [x10]              // Write at pointer offset 0

    mov     w12, #0x03c0
    movk    w12, #0xd65f, lsl #16   // Construct 32-bit instruction word: ret
    str     w12, [x10, #4]          // Write at pointer offset +4 bytes

    // STEP 3: FLUSH CPU INSTRUCTION CACHE (I-CACHE) FOR ARMV9 HARDWARE COMPLIANCE
    mov     x0, x10                 // Target buffer start address
    mov     x1, #8                  // Code footprint bounds (8 bytes total)
    bl      _sys_icache_invalidate  // Synchronize dynamic CPU decoding pipelines

    // STEP 4: EXECUTE THE RUNTIME MACHINE CODE
    blr     x10                     // Branch and link directly to the allocated page
    mov     x19, x0                 // Save execution return data state (42) into X19

    // STEP 5: EMIT CONSOLE CONFIRMATION MESSAGE VIA WRITE (0x2000004)
    mov     x0, #1                  // stdout
    adrp    x1, success_msg@PAGE    // Page coordinate lookup
    add     x1, x1, success_msg@PAGEOFF
    mov     x2, #37                 // Length of string message bytes

    movz    x16, #0x0004
    movk    x16, #0x0200, lsl #16   // Construct 0x2000004 into X16
    svc     #0x80                   // Trigger Write Syscall Interrupt

    // STEP 6: CLEAN SYSTEM TERMINATION (0x2000001)
    mov     x0, x19                 // Use execution result data (42) as shell return code
    movz    x16, #0x0001
    movk    x16, #0x0200, lsl #16   // Construct 0x2000001 into X16
    svc     #0x80                   // Final machine termination halt

_error_exit:
    mov     x0, #99                 // Custom failure exit code to flag mmap errors
    movz    x16, #0x0001
    movk    x16, #0x0200, lsl #16
    svc     #0x80

.section __TEXT,__cstring
success_msg:
    .ascii "🎉 Bare-Metal Host Complete. Core: 42\n"
