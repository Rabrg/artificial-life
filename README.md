# artificial-life

A simple (300 lines of code) reproduction of [Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple Interaction](https://arxiv.org/abs/2406.19108).

## Program description

A 240x135 grid of 64 instruction-length [Brainfuck](https://en.wikipedia.org/wiki/Brainfuck)-like programs are randomly initialized. Every iteration, neighboring programs are randomly paired, have their instruction tapes concattenated together, and are run for a maximum of $`2^{13}`$ steps. Once execution completes, the tapes are split back apart. The instructions are such that they can loop and mutate the instruction tapes (programs) themselves. As found in the paper, self-replicating programs that copy themselves over their neighbor's tape often spontaneously emerge, which soon spread to take over the entire grid.

## Example simulation
Every pixel is an instruction; each instruction has a unique color, while black represents a value on the tape that is raw data storage / not an instruction. Every 8x8 section of pixels represents a single program.

```
uv run main.py --seed 1
```

In this specific `--seed 1` run, a self-replicator emerges relatively early on into the run and soon takes over most of the grid, until a more efficient self-replicator evolves and takes over everything. Other seeds can produce different behaviors and timelines.

![Example](./universe.gif)

## Output formats

The checked-in `universe.gif` above is the original demo asset used by the README. New simulation runs do not overwrite it.

By default, the simulation writes a GIF to a fresh timestamped path under `outputs/`.

To also write an MP4 alongside it, pass `--mp4-path` with or without a value:

```
uv run main.py --seed 1 --mp4-path
uv run main.py --seed 1 --mp4-path outputs/universe.mp4
```

Passing `--mp4-path` without a value defaults to the generated GIF path with an `.mp4` suffix.

If you want a fixed location instead of a timestamped one, pass `--gif-path` explicitly:

```
uv run main.py --seed 1 --gif-path outputs/my-run.gif --mp4-path
```

To generate a shorter run that is roughly 10 seconds long:

```
uv run main.py --seed 1 --num-epochs 4000 --gif-every 20 --gif-fps 20 --mp4-path
```

## Contributing

Contributions are welcome. For setup, workflow, and contribution guidelines, see [CONTRIBUTING.md](./CONTRIBUTING.md).

If you are looking for a good first contribution, a few useful areas are:

- add tests for the interpreter and pairing logic
- improve experiment ergonomics and CLI options
- improve documentation and example runs
- extend visualization and export options

## Contributors

Current contributors:

<a href="https://github.com/DhruvShankpal">
  <img src="https://avatars.githubusercontent.com/u/136054942?v=4" width="72" alt="Dhruv Shankpal" />
</a>
<br />
<a href="https://github.com/DhruvShankpal">Dhruv Shankpal</a>

Add contributors directly to this README using the template below. A typical entry uses:

- display name or GitHub username
- GitHub profile link
- avatar image link from GitHub

Example template:

```html
<a href="https://github.com/your-username">
  <img src="https://github.com/your-username.png" width="72" alt="Your Name" />
</a>
<br />
<a href="https://github.com/your-username">Your Name</a>
```

Suggested naming options:

- your full name
- your GitHub username
- your first name plus last initial

Once you share your preferred name, profile URL, and avatar URL, this section can be updated with your contributor card.
