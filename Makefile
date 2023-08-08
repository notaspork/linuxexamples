obj-m += 3-kernelext-basic.o 4-kernelext-sysfs.o 5-kernelext-proc.o 5a-kernelext-proc.o 5b-kernelext-proc.o 6-kernelext-syscall.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean