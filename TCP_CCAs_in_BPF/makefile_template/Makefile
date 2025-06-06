Clang=clang -O2 -target bpf -c -g

default:	latest_response
	
clean:
	-rm *.o
	
	
latest_response:
	$(Clang) latest_response.c -o latest_response.o

register:
	sudo bpftool struct_ops register latest_response.o