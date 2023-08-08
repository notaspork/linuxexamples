#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/init.h>
#include <linux/vmalloc.h>
#include <linux/timer.h>
#include <linux/workqueue.h>
#include <linux/mutex.h>

#define DEFAULT_BUF_SIZE 32
#define SCRATCH_BUF_SIZE 64
#define TIMER_INTERVAL 5000 // in milliseconds

static struct timer_list kTimer;
static int kTimerCount = 0;
static struct workqueue_struct *kWorkqueue;
static struct work_struct kWork;

static struct proc_dir_entry *kLogFile = NULL;
static ssize_t kLogOffset = 0;

static char *kBuf = NULL;
static ssize_t kBufSize = 0;
static char *scratch = NULL;
static int scratchLen = 0;
static struct mutex logMutex;

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

    // make sure kBuf is not modified while we are copying it
    mutex_lock(&logMutex);

    readSize = length>(kLogOffset-*offset) ? (kLogOffset-*offset) : length;
    if (readSize > 0)
    {
        if (copy_to_user(buffer, kBuf+*offset, readSize))
        {
            printk(KERN_ERR "procfs_read: Failed to copy data to user space\n");
            mutex_unlock(&logMutex);
            return -EFAULT;
        }
        *offset += readSize;
    }

    mutex_unlock(&logMutex);

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
    char *newBuf;

    ret = size;

    printk(KERN_INFO "log_write: kLogOffset=%d, size=%d, kBufSize=%d\n", kLogOffset, size, kBufSize);
    if (size > DEFAULT_BUF_SIZE)
    {
        // check for unreasonably large sizes
        printk(KERN_ERR "log_write: size too big\n");
        return -EINVAL;
    }
    
    if (kLogOffset+size > kBufSize)
    {
        printk(KERN_INFO "log_write: BUFFER FULL!\n");
        // reallocate buffer to one twice as big
        mutex_lock(&logMutex);
        if (kLogOffset+size > kBufSize)
        {
            newBuf = vmalloc(kBufSize*2);
            if (!newBuf) {
                mutex_unlock(&logMutex);
                printk(KERN_ERR "log_write: Failed to reallocate memory for the buffer\n");
                return -ENOMEM;
            }
            memcpy(newBuf, kBuf, kBufSize);
            kBufSize *= 2;
            vfree(kBuf);
            kBuf = newBuf;
        }
        mutex_unlock(&logMutex);
        // note that if we didn't have the size check at the beginning of this function, we would want to check here again to make sure the data would fit in the newly resized buffer (in case size was bigger than the growth of the buffer)
    }
    memcpy(kBuf+kLogOffset, data, size);
    kLogOffset += size;

	return ret;
}

static void kWork_handler(struct work_struct *work)
{
    // Now we are in a non-interrupt context, so it's safe to call vmalloc()
    // Note that because there may be delays between the time the timer fires and the work is actually done, the timer may have fired multiple times before the work is actually done, so scratch may be clobbered by the time we get here
    // If this happens, we may lose log data, but we won't crash, since scratch was initialized with zeros and we would never write more than 63 bytes, so at least we won't read past the end of the buffer
    // If it's important to not lose any log data, we could use a system with multiple buffers
    // It shouldn't really matter in this example, since the timer only fires every 5 seconds
    log_write(scratch, scratchLen);
}

void kTimer_callback(struct timer_list *t)
{
    kTimerCount++;
    printk(KERN_INFO "Timer %d hit\n", kTimerCount);
    scratchLen = snprintf(scratch, SCRATCH_BUF_SIZE, "Timer %d hit\n", kTimerCount);
    
    // We are in an interrupt context here, so we can't do any work that might sleep, such as calling vmalloc()
    // Schedule the work to be done on the current CPU (Note that queue_work() can sleep, so queue_work_on() is necessary to avoid this possibility)
    queue_work_on(smp_processor_id(), kWorkqueue, &kWork);
    
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

    mutex_init(&logMutex);
    
    // Create a workqueue
    kWorkqueue = create_workqueue("kWorkqueue");
    if (!kWorkqueue) {
        printk(KERN_ERR "Failed to create workqueue\n");
        vfree(kBuf);
        vfree(scratch);
        return -ENOMEM;
    }

    // Initialize the work structure
    INIT_WORK(&kWork, kWork_handler);

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
    destroy_workqueue(kWorkqueue);
    printk(KERN_INFO "Destroyed workqueue\n");
    proc_remove(kLogFile);
    printk(KERN_INFO "Removed /proc/klog\n");
    vfree(kBuf);
    vfree(scratch);
    printk(KERN_INFO "Freed memory for the buffers\n");
}

MODULE_LICENSE("GPL");
