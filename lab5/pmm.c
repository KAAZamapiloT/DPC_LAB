#include <stdio.h>
#include <omp.h>

#define N 3

int main(){
    int A [ N ][ N ] = {{1 ,2 ,3} ,{4 ,5 ,6} ,{7 ,8 ,9}};
    int B [ N ][ N ] = {{1 ,0 ,0} ,{0 ,1 ,0} ,{0 ,0 ,1}};
    int C [ N ][ N ];
    int i ,j , k ;

    #pragma omp parallel for private(j,k)
    for(i=0;i<N;++i){
        for(j=0;j<N;j++){
            C[i][j]=0;
            for(k=0;k<N;k++){
                C[i][j]+=A[i][k]*B[k][j];
            }
        }
    }
printf("Input Matrix\n");
printf("A:\n");
for(int i=0;i<N;++i){
    for(int j=0;j<N;j++){
        printf("%d ", A[i][j]);
    }
    printf("\n");
}
printf("B:\n");
for(int i=0;i<N;++i){
    for(int j=0;j<N;j++){
        printf("%d ", B[i][j]);
    }
    printf("\n");
}
    printf("Resulatant matrix\n");

    for(int i=0;i<N;++i){
        for(int j=0;j<N;j++){
            printf("%d ", C[i][j]);
        }
        printf("\n");
    }

    return 0;
}
