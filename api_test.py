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

solver = """
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

site = "http://127.0.0.1:80"

url = f'{site}/judge'
data = {
    "memory_limit": 256,
    "time_limit": 1,
    "tests":["123", "69420" "19973"],
    "generator":{"source":generator, "language":"cpp17"},
    "solver":{"source":solver, "language":"cpp17"},
    "user":{"source":code, "language":"cpp17"},
    "validator": "null",
    "checker": "token"
}

HEADERS = {'Authorization': '69420'}

# response = requests.post(f"{site}/triangle_judge", json=data, headers=HEADERS)
# print(response.json())

# time.sleep(2)
response = requests.get(f"{site}/submission", headers=HEADERS)
print(response.json())

