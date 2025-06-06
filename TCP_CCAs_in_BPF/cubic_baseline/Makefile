
Clang=clang -O2 -target bpf -c -g
default:	bpf_cubic
clean:
	-rm *.o
bpf_cubic:
	$(Clang) bpf_cubic.c -o bpf_cubic.o -I /home/ubuntu/NECC_Cleaning/TCP_CCAs_in_BPF/headers
register:
	bpftool struct_ops register bpf_cubic.o
