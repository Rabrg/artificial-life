# Contributing

Thanks for contributing to `artificial-life`.

## Getting started

This project uses Python and `uv` for environment management.

1. Install `uv`.
2. Sync dependencies:

```bash
uv sync
```

If you do not have `uv` on your shell `PATH`, you can still run the project with the virtual environment Python after syncing:

```bash
.venv/bin/python main.py --help
```

## Running the project

Default example:

```bash
uv run main.py --seed 1
```

Generate both GIF and MP4 outputs:

```bash
uv run main.py --seed 1 --mp4-path
```

If `uv` is not available globally, use:

```bash
.venv/bin/python main.py --seed 1 --mp4-path
```

## Contribution workflow

1. Fork the repository.
2. Create a branch for your change.
3. Make the smallest clear change that solves one problem well.
4. Run the relevant checks or reproduction commands.
5. Update documentation if behavior or CLI usage changes.
6. Open a pull request with:
   - a short summary of the change
   - why the change is useful
   - how you tested it

## Good first contributions

- Add tests for `run_tape`, `select_pairs`, or `build_neighborhood`.
- Improve CLI help text and README examples.
- Add better experiment controls or output summaries.
- Improve export and visualization behavior.

## Style notes

- Keep changes focused and easy to review.
- Prefer small functions and descriptive names.
- Preserve existing behavior unless the change is intentional and documented.

## Adding yourself as a contributor

Contributors are listed in `README.md`.

For each contributor, collect:

- display name
- profile URL
- avatar image URL

A simple GitHub-based entry usually looks like:

```html
<a href="https://github.com/your-username">
  <img src="https://github.com/your-username.png" width="72" alt="Your Name" />
</a>
<br />
<a href="https://github.com/your-username">Your Name</a>
```

GitHub avatar URL options:

- `https://github.com/your-username.png`
- the image URL from your GitHub profile photo

Name options:

- full name
- GitHub username
- first name plus last initial
