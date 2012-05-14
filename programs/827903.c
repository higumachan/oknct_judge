#include <stdio.h>


main(){
FILE* fp;

fp = fopen("test.txt", "w");

fputs("HelloWorld", fp);

return (0);
}
