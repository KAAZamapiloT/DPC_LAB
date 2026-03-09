#include <ctype.h>
#include <signal.h>
#include<stdio.h>
#include<omp.h>
#include <time.h>
#include <string.h>
#include <stdlib.h>
#define N 12


int is_sorted(int *arr){
    for(int i=0;i<N-1;++i){
        if(arr[i]>arr[i+1]){
            return 0;
        }
    }
    return 1;
}

void shuffle(int *arr,unsigned int *seed){
    for(int i=0;i<N;++i){
        int j=rand()%N;
        int temp=arr[i];
        arr[i]=arr[j];
        arr[j]=temp;
    }
}
void copy_array(int *src, int *dest) {
    memcpy(dest, src, sizeof(int) * N);
}

void print_array(int *arr) {
    for (int i = 0; i < N; i++)
        printf("%d ", arr[i]);
    printf("\n");
}
double parallel_bogo(int *arr, int *result,
                     long long *total_shuffles,
                     int threads) {

    volatile int found = 0;
    *total_shuffles = 0;

    double start = omp_get_wtime();

#pragma omp parallel num_threads(threads) shared(found, result)
    {
        int local_arr[N];
        unsigned int seed = time(NULL) ^ omp_get_thread_num();
        long long local_count = 0;

        copy_array(arr, local_arr);

        while (!found) {

            if (is_sorted(local_arr)) {

#pragma omp critical
                {
                    if (!found) {
                        copy_array(local_arr, result);
                        found = 1;
                        printf("Thread %d found sorted array!\n",
                               omp_get_thread_num());
                    }
                }
                break;
            }

            shuffle(local_arr, &seed);
            local_count++;
        }

#pragma omp atomic
        *total_shuffles += local_count;
    }

    double end = omp_get_wtime();
    return end - start;
}


int main() {

    int arr[N], result[N];
    srand(time(NULL));


    for (int i = 0; i < N; i++)
        arr[i] = rand() % 50 + 1;

    printf("Original Array:\n");
    print_array(arr);

    int thread_list[3] = {2, 4, 8};

    printf("\nSummary Table:\n");
    printf("Threads   Time(sec)   Shuffles   Speedup\n");

    double baseline_time = 0;

    for (int i = 0; i < 3; i++) {

        long long shuffles;
        double t = parallel_bogo(arr, result,
                                 &shuffles,
                                 thread_list[i]);

        if (i == 0)
            baseline_time = t;

        double speedup = baseline_time / t;

        printf("%d         %.6f     %lld     %.2f\n",
               thread_list[i],
               t,
               shuffles,
               speedup);
    }

    printf("\nSorted Result (if found):\n");
    print_array(result);

    return 0;
}
