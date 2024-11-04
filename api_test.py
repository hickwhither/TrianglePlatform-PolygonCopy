import requests

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

url = 'http://localhost:5000/judge'
files = {
    'file': ('aplusb.zip', open("aplusb.zip", 'rb'), 'application/zip')
}
data = {
    'code': code,
    'language': language
}

HEADERS = {'Authorization': '69420'}

response = requests.post(url, files=files, data=data, headers=HEADERS)
print(response.json())

response = requests.get("http://127.0.0.1:5000/submissions", headers=HEADERS)
print(response.json())

