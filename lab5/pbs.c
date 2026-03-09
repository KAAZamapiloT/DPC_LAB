#include <stdio.h>
#include<omp.h>

int main(){
    int n,i,j,temp;
    printf("Enter Size of Matrix\n");
    scanf("%d",&n);
    int arr[n];

    printf("\nEnter Array Elements\n");
    for(int i=0;i<n;++i){
        scanf("%d",&arr[i]);
    }

    for(int i=0;i<n;++i){

        if(i%2==0){

            # pragma omp parallel for private ( temp )
             for(j=0;j<n-1;j+=2){
                 if(arr[j]>arr[j+1]){
                     temp=arr[j];
                     arr[j]=arr[j+1];
                     arr[j+1]=temp;
                 }
             }
        }else{
            # pragma omp parallel for private ( temp )
            for(j=1;j<n-1;j+=2){
                if(arr[j]>arr[j+1]){
                    temp=arr[j];
                    arr[j]=arr[j+1];
                    arr[j+1]=temp;
                }
            }
        }
    }
    printf (" Sorted ␣ array :\n") ;

     for( i = 0; i < n ; i ++)
      printf (" %d `1", arr [ i ]) ;

     return 0;
}
