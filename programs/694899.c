#include <stdio.h>

int main(void)
{
	int i;

	for (i = 0; i <= 100; i++){
		printf("%d:", i);
		if (i % 3 == 0){
			printf("Fizz");
		}
		if (i % 5 == 0){
			printf("Buzz");
		}
		puts("");
	}

	return (0);
}
