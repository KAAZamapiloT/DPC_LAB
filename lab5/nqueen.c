#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <omp.h>

#define N 8

bool isSafe(int queens[], int row, int col)
{
    for (int i = 0; i < row; i++)
    {
        int placedCol = queens[i];

        if (placedCol == col)
            return false;

        if (abs(placedCol - col) == abs(i - row))
            return false;
    }

    return true;
}

int solve(int queens[], int row)
{
    if (row == N)
        return 1;

    int count = 0;

    for (int col = 0; col < N; col++)
    {
        if (isSafe(queens, row, col))
        {
            queens[row] = col;
            count += solve(queens, row + 1);
        }
    }

    return count;
}


int main()
{
    int totalSolutions = 0;
    double start, end;

    start = omp_get_wtime();


    #pragma omp parallel for reduction(+:totalSolutions)
    for (int col = 0; col < N; col++)
    {
        int queens[N];

        queens[0] = col;

        totalSolutions += solve(queens, 1);
    }

    end = omp_get_wtime();

    printf("Board Size (N): %d\n", N);
    printf("Total Solutions: %d\n", totalSolutions);
    printf("Execution Time: %f seconds\n", end - start);

    return 0;
}
