#include <linux/module.h>
#include <linux/init.h>

int init_module(void)
{
    printk(KERN_INFO "Hello, kernel!\n");
    return 0;
}

void cleanup_module(void)
{
    printk(KERN_INFO "Goodbye, kernel!\n");
}

MODULE_LICENSE("GPL");
