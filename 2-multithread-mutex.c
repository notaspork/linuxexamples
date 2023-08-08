/*
    This program creates two threads that both increment a shared sequence_number variable 
    by 1,000,000 times. The expected value of sequence_number after both threads have finished 
    is 2,000,000. However, because the threads are executing concurrently and accessing 
    the shared variable without any synchronization mechanism, a race condition occurs 
    and the final value of sequence_number is unpredictable.
*/

#include <stdio.h>
#include <pthread.h>

int sequence_number = 0;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void *do_thread_sequence(void *arg) {
    int i;
    for (i = 0; i < 1000000; i++) {
        pthread_mutex_lock(&mutex);
        // Do_Something(sequence_number); // Commented out because we don't actually implement Do_Something in this example
        sequence_number++;
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

int main() {
    pthread_t thread1, thread2;

    pthread_create(&thread1, NULL, do_thread_sequence, NULL);
    pthread_create(&thread2, NULL, do_thread_sequence, NULL);

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    printf("sequence_number value: %d\n", sequence_number);

    return 0;
}
