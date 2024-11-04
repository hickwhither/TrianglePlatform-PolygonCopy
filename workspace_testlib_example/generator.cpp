#include "testlib.h"
#include <iostream>

using namespace std;

int main(int argc, char* argv[]) {
    registerGen(argc, argv, 1);
    
    int tests = rnd.next(1, 10000);
    println(tests);
    
    for(int i = 0; i < tests; i++) {
        int a = rnd.next(-1000000000, 1000000000);
        int b = rnd.next(-1000000000, 1000000000);
        println(a, b);
    }
    
    return 0;
}
