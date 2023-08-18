/* This file contains the source for the reversebinary executable used in the tutorial. 
   It is HIGHLY RECOMMENDED that you close this file immediately and do not look at it 
   if you have not yet completed that tutorial.  This should give you a better learning 
   experience. The binary is provided for this purpose, so you should not need this file.
   
   If for some reason, you want to compile this file later yourself, the command used is:
   
   gcc -s -fno-stack-protector -o reversebinary 7-bufferoverflow.c

*/

#include <stdio.h>
#include <string.h>

void vulnerable_function(char *input) {
    char buffer[32];
    strcpy(buffer, input);
    printf("Input: %s\n", buffer);
}

int main() {
    char input[64];
    printf("Enter input: ");
    scanf("%63s", input);
    vulnerable_function(input);
    return 0;
}
