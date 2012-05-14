#include <stdio.h>


main(){
FILE* fp;

fp = fopen("nadeko.txt", "w");

fputs("HelloWorld", fp);

return (0);
}
