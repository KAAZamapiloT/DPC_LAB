#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

#define N 12   // Keep small or you will wait forever

int is_sorted(int *arr) {
    for (int i = 0; i < N - 1; i++) {
        if (arr[i] > arr[i + 1])
            return 0;
    }
    return 1;
}

void shuffle(int *arr) {
    for (int i = 0; i < N; i++) {
        int j = rand() % N;
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}

void print_array(int *arr) {
    for (int i = 0; i < N; i++)
        printf("%d ", arr[i]);
    printf("\n");
}

double sequential_bogo(int *arr, long long *shuffle_count) {

    int temp[N];
    memcpy(temp, arr, sizeof(int) * N);

    *shuffle_count = 0;

    double start = (double)clock() / CLOCKS_PER_SEC;

    while (!is_sorted(temp)) {
        shuffle(temp);
        (*shuffle_count)++;
    }

    double end = (double)clock() / CLOCKS_PER_SEC;

    printf("Sorted Array:\n");
    print_array(temp);

    return end - start;
}

int main() {

    int arr[N];
    srand(time(NULL));

    // generate random values (1–50 allowed)
    for (int i = 0; i < N; i++)
        arr[i] = rand() % 50 + 1;

    printf("Original Array:\n");
    print_array(arr);

    long long shuffles;
    double time_taken = sequential_bogo(arr, &shuffles);

    printf("Time Taken: %.6f sec\n", time_taken);
    printf("Total Shuffles: %lld\n", shuffles);

    return 0;
}
