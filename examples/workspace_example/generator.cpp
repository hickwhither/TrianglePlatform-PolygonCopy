#include <bits/stdc++.h>

using namespace std;

int main(int argc, char* argv[]) {
    if (argc > 1) {
        srand(atoi(argv[1]));
    }
    int tests = rand() % 10000 + 1;
    cout << tests << endl;
    
    for(int i = 0; i < tests; i++) {
        int a = rand() % 2000000001 - 1000000000;
        int b = rand() % 2000000001 - 1000000000;
        cout << a << " " << b << endl;
    }
    
    return 0;
}
