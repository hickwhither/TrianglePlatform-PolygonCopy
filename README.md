Make sure .env
```
SECRET=blah
```

A config file should looks like this
```
{
    "memorylimit": 256,
    "timelimit": 1,
    "tests": [
        "123"
    ],
    "generator":{
        "path": "generator.cpp",
        "language": "cpp17"
    },
    "validator":{
        "path": "validator.cpp",
        "language": "cpp17"
    },
    "solution":{
        "path": "solution.cpp",
        "language": "cpp17"
    },
    "checker":{
        "path": "checker.cpp",
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

Validator also be this
```
"validator": null
```