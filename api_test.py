import requests
import time

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
language = "cpp17"    

site = "https://clean-jasper-blinker.glitch.me"

url = f'{site}/judge'
files = {
    'file': ('aplusb.zip', open("aplusb.zip", 'rb'), 'application/zip')
}
data = {
    'code': code,
    'language': language
}

HEADERS = {'Authorization': '69420'}

# response = requests.post(f"{site}/judge", files=files, data=data, headers=HEADERS)
# print(response.json())

# time.sleep(2)
response = requests.get(f"{site}/submissions", headers=HEADERS)
print(response.json())

