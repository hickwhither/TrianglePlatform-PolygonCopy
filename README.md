

## Docker Usage

Build the container:
```sh
docker build -t triangle-platform .
```

Run the server:
```sh
docker run -p 9111:80 --name name triangle-platform <secret_key>
```

## Api
'/triangle-judge`
```
{
    "memory_limit": 256,
    "time_limit": 1,
    "tests": [
        "123"
    ],
    "generator":{
        "source": "...",
        "language": "cpp17"
    },
    "validator":{
        "source": "...",
        "language": "cpp17"
    },
    "solution":{
        "source": "...",
        "language": "cpp17"
    },
    "checker":{
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

Validator also be this
```
"validator": null
```