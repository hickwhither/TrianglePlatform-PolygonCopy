#include "testlib.h"
#include <iostream>

int main(int argc, char* argv[]) {
    registerTestlibCmd(argc, argv);
    
    int t = inf.readInt();
    
    for(int i = 1; i <= t; i++) {
        int ja = ans.readInt();
        int pa = ouf.readInt();
        
        if (ja != pa) {
            quitf(_wa, "Test case %d: Expected %d, found %d", i, ja, pa);
        }
    }
    
    quitf(_ok, "All test cases passed");
}
