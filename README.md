# artificial-life

A simple (300 lines of code) reproduction of [Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple Interaction](https://arxiv.org/abs/2406.19108).

## Program description

A 240x135 grid of 64 instruction-length [Brainfuck](https://en.wikipedia.org/wiki/Brainfuck)-like programs are randomly initialized. Every iteration, neighboring programs are randomly paired, have their instruction tapes concattenated together, and are run for a maximum of $`2^{13}`$ steps. Once execution completes, the tapes are split back apart. The instructions are such that they can loop and mutate the instruction tapes (programs) themselves. As found in the paper, self-replicating programs that copy themselves over their neighbor's tape often spontaneously emerge, which soon spread to take over the entire grid.

## Example simulation
Every pixel is an instruction; each instruction has a unique color, while black represents a value on the tape that is raw data storage / not an instruction. Every 8x8 section of pixels represents a single program.

```
uv run main.py --seed 1
```

In this run, a self-replicator emerges relatively early on into the run and soon takes over most of the grid, until a more efficient self-replicator evolves and takes over everything.

![Example](./universe.gif)
