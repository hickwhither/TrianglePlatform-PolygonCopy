This is use for high quality stress test with low quality machine ~~(free host yes im actually doing it)~~
I named triangle because it's the minumum edge 'Polygon'

## Normal run
```
python main.py
```

## Docker Usage
Build the container:
```sh
docker build -t triangle-platform .
```

Run the server:
```sh
docker run -p 9111:8080 --name name triangle-platform
```

### GET '/'
Pinging judge
`200`
```json
{
    "start": "timezone:int", // uptime
    "status": "idle/compiling/judging",
    "versions": {
        "cpp17":{
            "id": "cpp17",
            "file_extension": ".cpp",
            "compilation": "g++ -std=c++17 -Wall -O2 -lm -fmax-errors=5 -march=native -s {name}.cpp -o {name}.out",
            "execution": "./{name}.out",
            "version": "..."
        },
    },
    "response": "...",
    "runtime": "seconds:int",
}
```

### GET '/result'
Get result after judge
```json
{
    "status": "idle/compiling/judging",
    "results_count": 69,
    "results": [ // could be null if not successfully compile
        {
            "verdict": "int",
            "response": "reponse from checker/judger",
            "input": "str",
            "output":"str",
            "answer":"str"
        },
        ...
    ]
}
```

### POST '/judge`
```json
{
    "memory_limit": 256,
    "time_limit": 1,
    "limit_character": 256, // if it's too long
    "tests": [ // args for generator
        "123"
    ],
    "generator":{
        "source": "...",
        "language": "cpp17"
    },
    "checker":{
        "source": "...",
        "language": "cpp17"
    },
    "brute":{ // answer
        "source": "...",
        "language": "cpp17"
    },
    "user":{
        "source": "...",
        "language": "cpp17"
    }
}
```

`200`
```json
{"response": "Judging started"}
```
`400`
```json
{"response": "Invalid 'tests' format. Expected a list."}
```
`400`
```json
{"response": "Invalid 'memory_limit' or 'time_limit' format. Expected float values."}
```
`400`
```json
{"response": f"Invalid `{key}` format. Expected a dictionary with 'source' and 'language' keys."}
```
`400`
```json
{"response": "Invalid 'checker' format. Expected a dictionary with 'source' and 'language' keys or a string starting with 'token', 'line', or 'float'."}
```

Checker also be this
```js
"checker": "token"
"checker": "line"
"checker": "float6"
```

### POST '/stop'
`200`
```json
{"response": "Judge is already idle"}
```

`200`
```json
{"response": "Judge stopped"}
```