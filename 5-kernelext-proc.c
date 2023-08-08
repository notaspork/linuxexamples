#include <linux/module.h>
#include <linux/init.h>
#include <linux/proc_fs.h>
#include <linux/vmalloc.h>
#include <linux/timer.h>

#define DEFAULT_BUF_SIZE 1048576 // 1 MB
#define SCRATCH_BUF_SIZE 64
#define TIMER_INTERVAL 5000 // in milliseconds

static struct timer_list kTimer;
static int kTimerCount = 0;

static struct proc_dir_entry *kLogFile = NULL;
static ssize_t kLogOffset = 0;

static char *kBuf = NULL;
static ssize_t kBufSize = 0;
static char *scratch = NULL;

static ssize_t procfs_read(struct file *filp, char __user *buffer, size_t length, loff_t *offset)
{
    ssize_t readSize;

    printk(KERN_INFO "procfs_read (/proc/klog) called\n");
    if (!filp || !buffer || !offset)
        return -EINVAL;

    if (*offset >= kLogOffset) {
        printk(KERN_INFO "procfs_read: EOF\n");
        return 0;
    }

    readSize = length>(kLogOffset-*offset) ? (kLogOffset-*offset) : length;
    if (readSize > 0)
    {
        if (copy_to_user(buffer, kBuf+*offset, readSize))
        {
            printk(KERN_ERR "procfs_read: Failed to copy data to user space\n");
            return -EFAULT;
        }
        *offset += readSize;
    }

    return readSize;
}

loff_t procfs_llseek(struct file *file, loff_t offset, int whence)
{
    loff_t newpos;

    switch (whence) {
    case 0: /* SEEK_SET */
        newpos = offset;
        break;

    case 1: /* SEEK_CUR */
        newpos = file->f_pos + offset;
        break;

    case 2: /* SEEK_END */
        newpos = kLogOffset + offset;
        break;

    default: /* can't happen */
        return -EINVAL;
    }
    if (newpos < 0)
        return -EINVAL;
    file->f_pos = newpos;
    return newpos;
}

static const struct proc_ops proc_file_fops = {
    .proc_read = procfs_read,
    .proc_lseek = procfs_llseek,
};

/* Writes log entry to proc buffer */
int log_write(unsigned char *data, unsigned int size)
{
	int ret;

    ret = size;

    printk(KERN_INFO "log_write: kLogOffset=%d, size=%d, kBufSize=%d\n", kLogOffset, size, kBufSize);
    if (size > 32)
    {
        // check for unreasonably large sizes
        printk(KERN_ERR "log_write: size too big\n");
        return -EINVAL;
    }
    
    if (kLogOffset+size > kBufSize)
    {
        printk(KERN_INFO "log_write: BUFFER FULL!\n");
        return 0;
    }
    memcpy(kBuf+kLogOffset, data, size);
    kLogOffset += size;

	return ret;
}

void kTimer_callback(struct timer_list *t)
{
    int len;
    
    kTimerCount++;
    printk(KERN_INFO "Timer %d hit\n", kTimerCount);
    len = snprintf(scratch, SCRATCH_BUF_SIZE, "Timer %d hit\n", kTimerCount);
    log_write(scratch, len);

    // Set new timer time
    mod_timer(&kTimer, jiffies + msecs_to_jiffies(TIMER_INTERVAL));
}

int init_module(void)
{
    printk(KERN_INFO "Creating log file\n");
    // Allocate memory for the buffers
    kBuf = vmalloc(DEFAULT_BUF_SIZE);
    scratch = vzalloc(SCRATCH_BUF_SIZE);
    if (!kBuf || !scratch) {
        printk(KERN_INFO "Failed to allocate memory for the buffers\n");
        if (kBuf)
            vfree(kBuf);
        if (scratch)
            vfree(scratch);
        return -ENOMEM;
    }
    printk(KERN_INFO "Allocated memory for the buffers\n");
    kBufSize = DEFAULT_BUF_SIZE;

    // Setup /proc/klog
    kLogFile = proc_create("klog", 0444, NULL, &proc_file_fops);
    if (!kLogFile) {
        vfree(kBuf);
        vfree(scratch);
        printk(KERN_ERR "Failed to create the kBuf file in /proc/klog\n");
        return -ENOMEM;
    }
    printk(KERN_INFO "Created the klog file in /proc/klog\n");

    log_write("Hello, world!\n", 14);

    // Initialize the timer
    timer_setup(&kTimer, kTimer_callback, 0);

    // Start the timer
    mod_timer(&kTimer, jiffies + msecs_to_jiffies(TIMER_INTERVAL));
    printk(KERN_INFO "Timer started\n");

    return 0;
}

void cleanup_module(void)
{
    del_timer(&kTimer);
    printk(KERN_INFO "Timer stopped\n");
    proc_remove(kLogFile);
    printk(KERN_INFO "Removed /proc/klog\n");
    vfree(kBuf);
    vfree(scratch);
    printk(KERN_INFO "Freed memory for the buffers\n");
}

MODULE_LICENSE("GPL");
