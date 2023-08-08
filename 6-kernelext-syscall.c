#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/syscalls.h>
#include <linux/string.h>
#include <linux/uaccess.h>
#include <linux/kprobes.h>

MODULE_LICENSE("GPL");

// Define the list of filter words to filter
static const char *filter_words[] = {
    "secret_user",
    "secret_password"
};
static const int num_filter_words = sizeof(filter_words) / sizeof(filter_words[0]);

// Define the replacement string
// Note that these are the exact same length as the words they replace to prevent issues
static const char *replace_words[] = {
    "maxwelltran",
    "acde$2a2Ak#@!33"
};

// Pointer to the system call table
static void **sys_call_table;

#ifdef CONFIG_ARCH_HAS_SYSCALL_WRAPPER
// Define the original read system call
asmlinkage ssize_t (*original_read)(const struct pt_regs *);

// Define the new read system call
asmlinkage ssize_t new_read(const struct pt_regs *regs) {
    int fd = regs->di;
    char *buf = (char *)regs->si;
    size_t count = regs->dx;

    ssize_t ret = original_read(regs);
#else
// Define the original read system call
asmlinkage ssize_t (*original_read)(int fd, void *buf, size_t count);

// Define the new read system call
asmlinkage ssize_t new_read(int fd, void *buf, size_t count) {
    ssize_t ret = original_read(fd, buf, count);
#endif
    if ((ret > 0) && buf) {
        // Allocate a kernel buffer to hold the user space data
        int i,j;
        char *str;
        int numMatches = 0;
        char *kernel_buf = kmalloc(ret, GFP_KERNEL);
        if (!kernel_buf) {
            printk(KERN_ERR "Failed to allocate memory (%d bytes)\n",ret);
            return ret;
        }

        // Copy the data from user space to kernel space
        if (copy_from_user(kernel_buf, buf, ret)) {
            kfree(kernel_buf);
            printk(KERN_ERR "copy_from_user failed (%d bytes)\n",ret);
            return ret;
        }

        // Filter any filter words in the buffer
        str = kernel_buf;
        
        for (i = 0; i < ret; i++,str++) {
            for (j = 0; j < num_filter_words; j++) {
                if (strncmp(str, filter_words[j], strlen(filter_words[j])) == 0) {
                    printk(KERN_INFO "[%lx] Found word #%d\n", kernel_buf, j);
                    memcpy(str, replace_words[j], strlen(filter_words[j]));
                    numMatches++;
                }
            }
        }

        // Copy the filtered data back to user space
        if (numMatches) {
            int err;
            
            printk(KERN_INFO "[%lx] Intercepted read call (%d matches): fd=%d, count=%d, ret=%d, buf=[%lx]\n", kernel_buf, numMatches, fd, count, ret, buf);
            err = copy_to_user(buf, kernel_buf, ret);
            if (err) {
                printk(KERN_ERR "copy_to_user failed (%d bytes)\n",ret);
            }
        }
        kfree(kernel_buf);
    }
    return ret;
}

static inline void __write_cr0(unsigned long cr0)
{
    asm volatile("mov %0,%%cr0" : "+r"(cr0) : : "memory");
}

static void enable_write_protection(void)
{
    unsigned long cr0 = read_cr0();
    set_bit(16, &cr0);
    __write_cr0(cr0);
    printk(KERN_INFO "Write protection enabled\n");
}

static void disable_write_protection(void)
{
    unsigned long cr0 = read_cr0();
    clear_bit(16, &cr0);
    __write_cr0(cr0);
    printk(KERN_INFO "Write protection disabled\n");
}

static unsigned long sym;
module_param(sym,ulong,0644);
MODULE_PARM_DESC(sym, "sys_call_table address");

static int get_sys_call_table(void) {
    
    if (sym == 0) {
        // no module parameter specified, so we need to find the address of sys_call_table using kprobes
        unsigned long (*kallsyms_lookup_name)(const char *name);
        struct kprobe kp = {
            .symbol_name = "kallsyms_lookup_name"
        };
        printk(KERN_INFO "loading kallsyms_lookup_name\n");

        if (register_kprobe(&kp) < 0) {
            printk(KERN_ERR "register_kprobe failed\n");
            return -1;
        }
        kallsyms_lookup_name = (void *)kp.addr;
        unregister_kprobe(&kp);
        printk(KERN_INFO "kallsyms_lookup_name address: 0x%lx\n", kallsyms_lookup_name);
        sys_call_table = kallsyms_lookup_name("sys_call_table");
    }
    else {
        sys_call_table = (void **)sym;
    }
    printk(KERN_INFO "sys_call_table address specified: 0x%lx\n", sys_call_table);
    return(0);
}

// Initialize the kernel module
static int __init init_syscall(void) {

    printk(KERN_INFO "Starting init_syscall\n");
    sys_call_table = NULL;
    if (get_sys_call_table()) {
        printk(KERN_ERR "Failed to get kallsyms_lookup_name address\n");
        return -1;
    }
    
    if (!sys_call_table) {
        printk(KERN_ERR "Failed to find sys_call_table\n");
        return -1;
    }

    // Replace the read system call with our new implementation
    printk(KERN_INFO "Replacing syscall read\n");
    disable_write_protection();
    original_read = sys_call_table[__NR_read];
    sys_call_table[__NR_read] = new_read;
    printk(KERN_INFO "Syscall read patched\n");
    enable_write_protection();

    return 0;
}

// Cleanup the kernel module
static void __exit exit_syscall(void) {

    // Restore the original read system call
    if (sys_call_table[__NR_read] != new_read) {
        printk(KERN_ERR "Syscall read patch not at expected address -- may have been patched by another module -- exiting\n");
    }
    disable_write_protection();
    sys_call_table[__NR_read] = original_read;
    printk(KERN_INFO "Syscall read restored\n");
    enable_write_protection();
}

module_init(init_syscall);
module_exit(exit_syscall);
