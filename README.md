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

### '/'
For ping/result of judge
```json
{
    "start": "timezone:int", // uptime
    "status": "idle/compiling/judging",
    
    "response": "...",
    "runtime": "seconds:int",
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

### '/judge`
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

Checker also be this
```
"checker": "token"
"checker": "line"
"checker": "float6"
```
