#include <linux/module.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/kobject.h>
#include <linux/sysfs.h>
#include <linux/string.h>

#define BUF_SIZE PAGE_SIZE

static char *kBuf = NULL;
static char *kPos = NULL;
static char *kBufEnd = NULL;
static struct kobject *modObj = NULL;

ssize_t kBuf_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf)
{
    printk(KERN_INFO "kBuf_show (size=%d)\n", kPos-kBuf);
    return snprintf(buf, PAGE_SIZE, "%s\n", kBuf);
}

static struct kobj_attribute kBuf_attribute = __ATTR(kBuf, 0440, kBuf_show, NULL);

// Writes log data to buffer for /sys/kernel/klog/kBuf
int log_write(unsigned char *data, unsigned int size)
{
    printk(KERN_INFO "log_write: kPos=0x%lx, size=%d, kBufEnd=0x%lx\n", kPos, size, kBufEnd);
    if ((char *)kPos + size >= (char *)kBufEnd)
    {
        printk(KERN_INFO "log_write: BUFFER FULL!\n");
        return 0;
    }
    memcpy(kPos, data, size);
    kPos += size;

	return size;
}

int init_module(void)
{
    int err;

    printk(KERN_INFO "Creating log file\n");
    // Allocate memory for the buffer
    kBuf = kzalloc(BUF_SIZE, GFP_KERNEL);
    if (!kBuf)
    {
        printk(KERN_ERR "Failed to allocate memory for the buffer\n");
        return -ENOMEM;
    }
    kBufEnd = kBuf + BUF_SIZE;
    kPos = kBuf;
    printk(KERN_INFO "Allocated memory for the buffer\n");

    // Setup /sys/kernel/klog
    modObj = kobject_create_and_add("klog", kernel_kobj);
    if (!modObj)
        return -ENOMEM;

    err = sysfs_create_file(modObj, &kBuf_attribute.attr);
    if (err)
    {
        printk(KERN_ERR "Failed to create the kBuf file in /sys/kernel/klog (err=%d)\n", err);
        return err;
    }

    printk(KERN_INFO "Created the kBuf file in /sys/kernel/klog\n");

    log_write("Hello, world!\n", 14);
    
    return 0;
}

void cleanup_module(void)
{
    kobject_put(modObj);
    printk(KERN_INFO "Removed /sys/kernel/klog\n");
    kfree(kBuf);
    printk(KERN_INFO "Freed memory for the buffer\n");
}

MODULE_LICENSE("GPL");
