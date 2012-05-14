main(){
FILE* fp;

fp = fopen("test.txt", "w");

fputs("HelloWorld", fp);

fclose(fp);

return (0);
}
