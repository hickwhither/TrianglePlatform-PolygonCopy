from judger import *
import json

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

triangle = Triangle()
triangle.compile()

if not os.path.exists("user_submissions"): os.mkdir("user_submissions")
shutil.rmtree("user_submissions")
os.mkdir("user_submissions")
usercode = SourceCode(triangle)
usercode.compile(code, "cpp17")

triangle.run(usercode)
for i in triangle.results:
    print(json.dumps(i, indent=4))


