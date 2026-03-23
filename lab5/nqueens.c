#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <omp.h>

#define N 8

typedef struct {
    int queens[N];
} Board;

bool found = false;


// check if safe
bool isSafe(Board *board, int row, int col)
{
    for (int i = 0; i < row; i++)
    {
        int prev = board->queens[i];

        if (prev == col)
            return false;

        if (abs(prev - col) == abs(i - row))
            return false;
    }

    return true;
}


// print board
void printBoard(Board *board)
{
    printf("\nOne Valid Solution:\n\n");

    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            if (board->queens[i] == j)
                printf("Q ");
            else
                printf(". ");
        }
        printf("\n");
    }
}


// recursive solver
void solve(Board *board, int row)
{
    if (found)
        return;

    if (row == N)
    {
        #pragma omp critical
        {
            if (!found)
            {
                found = true;
                printBoard(board);
            }
        }
        return;
    }

    for (int col = 0; col < N; col++)
    {
        if (found)
            return;

        if (isSafe(board, row, col))
        {
            board->queens[row] = col;
            solve(board, row + 1);
        }
    }
}


int main()
{
    double start = omp_get_wtime();

    #pragma omp parallel for
    for (int col = 0; col < N; col++)
    {
        if (found)
            continue;

        Board board;
        board.queens[0] = col;

        solve(&board, 1);
    }

    double end = omp_get_wtime();

    printf("\nExecution Time: %f seconds\n", end - start);

    return 0;
}
