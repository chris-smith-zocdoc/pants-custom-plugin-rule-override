

```
PANTS_VERSION=2.27.0rc1 pants run src#start
Hello, world!. Injected env var: true


PANTS_VERSION=2.28.0.dev0 pants run src#start
Hello, world!. Injected env var: true


PANTS_VERSION=2.28.0.dev1 pants run src#start
Hello, world!. Injected env var: false
```

The typescript backend was migrated to call-by-name in 2.28.0.dev1
