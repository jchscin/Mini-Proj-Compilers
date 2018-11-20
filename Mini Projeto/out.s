	.text
	.file	"out.ll"
	.globl	h                       # -- Begin function h
	.p2align	4, 0x90
	.type	h,@function
h:                                      # @h
	.cfi_startproc
# %bb.0:
	movl	%edi, -4(%rsp)
	movl	%esi, -8(%rsp)
	movl	%esi, -12(%rsp)
	negl	%esi
	movl	%esi, -16(%rsp)
	movl	%edi, %eax
	retq
.Lfunc_end0:
	.size	h, .Lfunc_end0-h
	.cfi_endproc
                                        # -- End function
	.globl	main                    # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:
	movl	$2, -4(%rsp)
	movl	$4, -8(%rsp)
	xorl	%eax, %eax
	retq
.Lfunc_end1:
	.size	main, .Lfunc_end1-main
	.cfi_endproc
                                        # -- End function

	.section	".note.GNU-stack","",@progbits
