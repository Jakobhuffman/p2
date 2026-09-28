# P2 LLVM CFG Inference

Run:

```sh
make
./graph test1.ll
dot main.dot -o main.png -Tpng
```

The `graph` program writes one Graphviz DOT file per function, named
`<function>.dot`. For a single-function input, it also prints the DOT graph to
stdout.
