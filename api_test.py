import requests
import time

generator = """
#include <iostream>

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
"""

brute = """
#include <iostream>
using namespace std;

int main() {
    int t;
    cin >> t;
    while (t--) {
        int a, b;
        cin >> a >> b;
        cout << a + b << endl;
    }
    return 0;
}
"""

code = """
#include <iostream>
using namespace std;

int main() {
    int t;
    cin >> t;
    while (t--) {
        int a, b;
        cin >> a >> b;
        cout << a + b << endl;
        // if((a+b)%69==0) cout << "Time for error!";
    }
    return 0;
}
"""

site = "http://127.0.0.1:9111"

url = f'{site}/judge'
data = {
    "limit_character": 200,
    "memory_limit": 256,
    "time_limit": 1,
    "tests":["123", "69420" "19973"],
    "generator":{"source":generator, "language":"cpp"},
    "brute":{"source":brute, "language":"cpp"},
    "user":{"source":code, "language":"cpp"},
    "checker": "token"
}

response = requests.post(f"{site}/judge", json=data)
print(response.json())
time.sleep(2)
response = requests.get(site)
print(response.json())

