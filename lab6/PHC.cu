#include <stdio.h>
#include <cuda_runtime.h>
#include <device_launch_parameters.h>

#define N 10
#define BINS 5

// GPU Kernel
__global__ void histogram(int* data, int* hist)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < N)
    {
        atomicAdd(&hist[data[i]], 1);
    }
}

int main()
{
    int data[N] = {1, 2, 1, 3, 2, 4, 0, 1, 3, 2};
    int hist[BINS] = {0};

    int* d_data;
    int* d_hist;

    // Allocate GPU memory
    cudaMalloc((void**)&d_data, N * sizeof(int));
    cudaMalloc((void**)&d_hist, BINS * sizeof(int));

    // Copy data from Host to Device
    cudaMemcpy(d_data, data, N * sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(d_hist, hist, BINS * sizeof(int), cudaMemcpyHostToDevice);

    // Launch Kernel
    histogram<<<1, N>>>(d_data, d_hist);

    // Copy result back to Host
    cudaMemcpy(hist, d_hist, BINS * sizeof(int), cudaMemcpyDeviceToHost);

    printf("Histogram Result:\n");

    for (int i = 0; i < BINS; i++)
    {
        printf("Value %d : %d\n", i, hist[i]);
    }

    // Free GPU memory
    cudaFree(d_data);
    cudaFree(d_hist);

    return 0;
}
