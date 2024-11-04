#include "testlib.h"

int main(int argc, char* argv[]) {
    registerValidation(argc, argv);
    
    int t = inf.readInt(1, 10000, "t");
    inf.readEoln();
    
    for(int i = 0; i < t; i++) {
        int a = inf.readInt(-1000000000, 1000000000, "a");
        inf.readSpace();
        int b = inf.readInt(-1000000000, 1000000000, "b");
        inf.readEoln();
    }
    
    inf.readEof();
    return 0;
}
