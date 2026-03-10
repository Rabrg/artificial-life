import argparse
from pathlib import Path

import numpy as np
from numba import njit, prange
from PIL import Image
from tqdm import tqdm

ZERO, ONE = np.uint8(0), np.uint8(1)
LT, GT, LB, RB, MINUS, PLUS, DOT, COMMA, LBRACK, RBRACK = map(ord, "<>{}-+.,[]")
OPCODE_TOKENS = np.array(
    [LT, GT, LB, RB, MINUS, PLUS, DOT, COMMA, LBRACK, RBRACK], dtype=np.uint8
)
NORMALIZED_VALUE = np.uint8(255)
NORMALIZE_LOOKUP = np.full(256, NORMALIZED_VALUE, dtype=np.uint8)
NORMALIZE_LOOKUP[OPCODE_TOKENS] = OPCODE_TOKENS


@njit(cache=True)
def run_tape(tape: np.ndarray, max_iterations: int = 2**13) -> np.ndarray:
    tape_size = tape.shape[0]
    pc = head0 = head1 = 0

    def seek_match(pc: int, step: int, open_tok: int, close_tok: int) -> int:
        depth = 1
        pc += step
        while 0 <= pc < tape_size and depth:
            opcode = tape[pc]
            if opcode == open_tok:
                depth += 1
            elif opcode == close_tok:
                depth -= 1
            pc += step
        return pc - step if depth == 0 else -1

    for _ in range(max_iterations):
        if not 0 <= pc < tape_size:
            break
        opcode = tape[pc]

        if opcode == LT or opcode == GT:
            head0 = (head0 + (1 if opcode == GT else -1)) % tape_size
        elif opcode == LB or opcode == RB:
            head1 = (head1 + (1 if opcode == RB else -1)) % tape_size
        elif opcode == MINUS or opcode == PLUS:
            tape[head0] = tape[head0] - ONE if opcode == MINUS else tape[head0] + ONE
        elif opcode == DOT:
            tape[head1] = tape[head0]
        elif opcode == COMMA:
            tape[head0] = tape[head1]
        elif opcode == LBRACK and tape[head0] == ZERO:
            pc = seek_match(pc, 1, LBRACK, RBRACK)
            if pc < 0:
                break
        elif opcode == RBRACK and tape[head0] != ZERO:
            pc = seek_match(pc, -1, RBRACK, LBRACK)
            if pc < 0:
                break
        pc += 1

    return tape


@njit(cache=True)
def select_pairs(
    order: np.ndarray, proposals: np.ndarray, pairs: np.ndarray, taken: np.ndarray
) -> int:
    taken[:] = 0
    pair_count = 0

    for i in range(order.shape[0]):
        p = order[i]
        n = proposals[p]
        if n < 0 or taken[p] or taken[n]:
            continue
        taken[p] = 1
        taken[n] = 1
        pairs[pair_count, 0] = p
        pairs[pair_count, 1] = n
        pair_count += 1

    return pair_count


@njit(parallel=True, cache=True)
def run_epoch_pairs(programs: np.ndarray, pairs: np.ndarray, pair_count: int) -> None:
    tape_size = programs.shape[1]
    concat_size = tape_size * 2

    for pair_idx in prange(pair_count):
        idx_a = pairs[pair_idx, 0]
        idx_b = pairs[pair_idx, 1]

        tape = np.empty(concat_size, dtype=np.uint8)
        tape[:tape_size] = programs[idx_a]
        tape[tape_size:] = programs[idx_b]

        run_tape(tape)

        programs[idx_a] = tape[:tape_size]
        programs[idx_b] = tape[tape_size:]


def apply_background_mutation(
    programs: np.ndarray, mutation_rate: float, rng: np.random.Generator
) -> None:
    if mutation_rate <= 0.0:
        return

    grid_width, grid_height, tape_size = programs.shape
    num_cells = grid_width * grid_height
    cells = programs.reshape(num_cells, tape_size)
    mutation_mask = (rng.random(num_cells) < mutation_rate)
    num_mutations = mutation_mask.sum()
    if num_mutations != 0:
        cells[mutation_mask] = rng.integers(0, 256, size=(num_mutations, tape_size), dtype=np.uint8)


def build_neighborhood(width: int, height: int) -> tuple[np.ndarray, np.ndarray]:
    num_programs = width * height
    neighbors = np.full((num_programs, 24), -1, dtype=np.int32)
    neighbor_counts = np.zeros(num_programs, dtype=np.int32)

    for x in range(width):
        x_lo, x_hi = max(0, x - 2), min(width, x + 3)
        for y in range(height):
            y_lo, y_hi = max(0, y - 2), min(height, y + 3)
            idx = x * height + y
            count = 0

            for nx in range(x_lo, x_hi):
                base = nx * height
                for ny in range(y_lo, y_hi):
                    if nx == x and ny == y:
                        continue
                    neighbors[idx, count] = base + ny
                    count += 1

            neighbor_counts[idx] = count

    return neighbors, neighbor_counts


def normalize_cells(cells: np.ndarray) -> np.ndarray:
    return NORMALIZE_LOOKUP[cells]


def build_color_lut() -> np.ndarray:
    palette = np.array(
        [
            [239, 71, 111],  # <
            [255, 209, 102],  # >
            [6, 214, 160],  # {
            [17, 138, 178],  # }
            [255, 127, 80],  # -
            [131, 56, 236],  # +
            [58, 134, 255],  # .
            [255, 190, 11],  # ,
            [139, 201, 38],  # [
            [255, 89, 94],  # ]
            [20, 20, 20],  # normalized 255
        ],
        dtype=np.uint8,
    )
    lut = np.empty((256, 3), dtype=np.uint8)
    lut[:] = palette[-1]
    lut[OPCODE_TOKENS] = palette[:-1]
    return lut


def render_program_frame(programs: np.ndarray, color_lut: np.ndarray) -> np.ndarray:
    if programs.shape[2] != 64:
        raise ValueError("GIF rendering requires tape_size == 64 (8x8 tapes)")

    grid_width, grid_height, _ = programs.shape
    tapes = normalize_cells(programs).reshape(grid_width, grid_height, 8, 8)
    colored = color_lut[tapes]
    return colored.transpose(1, 2, 0, 3, 4).reshape(grid_height * 8, grid_width * 8, 3)


def save_evolution_gif(frames: list[Image.Image], output_path: str, fps: int) -> None:
    if not frames:
        raise ValueError("No GIF frames were captured")
    if fps <= 0:
        raise ValueError("--gif-fps must be > 0")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=max(1, int(round(1000 / fps))),
        loop=0,
        optimize=False,
        disposal=2,
    )


def opcode_token_percent(programs: np.ndarray) -> float:
    counts = np.bincount(programs.ravel(), minlength=256)
    return 100.0 * float(counts[OPCODE_TOKENS].sum()) / float(programs.size)


def run_epochs(
    programs: np.ndarray,
    nepochs: int,
    mutation_rate: float,
    rng: np.random.Generator,
    gif_every: int,
) -> list[Image.Image]:
    grid_width, grid_height, tape_size = programs.shape
    num_programs = grid_width * grid_height
    flat_programs = programs.reshape(num_programs, tape_size)
    neighbors, neighbor_counts = build_neighborhood(grid_width, grid_height)
    rows = np.arange(num_programs, dtype=np.int32)
    valid_rows = rows[neighbor_counts > 0]
    valid_neighbor_counts = neighbor_counts[valid_rows]
    all_rows_are_valid = valid_rows.size == num_programs
    pairs = np.empty((num_programs // 2, 2), dtype=np.int32)
    proposals = np.empty(num_programs, dtype=np.int32)
    taken = np.empty(num_programs, dtype=np.uint8)
    frames: list[Image.Image] = []
    color_lut = build_color_lut()

    pbar = tqdm(range(nepochs))
    for epoch in pbar:
        order = rng.permutation(num_programs).astype(np.int32, copy=False)
        if all_rows_are_valid:
            choices = rng.integers(0, neighbor_counts)
            proposals[:] = neighbors[rows, choices]
        else:
            proposals.fill(-1)
            choices = rng.integers(0, valid_neighbor_counts)
            proposals[valid_rows] = neighbors[valid_rows, choices]

        pair_count = select_pairs(order, proposals, pairs, taken)
        run_epoch_pairs(flat_programs, pairs, pair_count)
        apply_background_mutation(programs, mutation_rate, rng)
        if color_lut is not None and (
            (epoch + 1) % gif_every == 0 or epoch + 1 == nepochs or epoch == 0
        ):
            frames.append(
                Image.fromarray(render_program_frame(programs, color_lut), mode="RGB")
            )
        pbar.set_postfix_str(f"opcode={opcode_token_percent(programs):.2f}%")

    return frames


if __name__ == "__main__":
    np.seterr(over="ignore", under="ignore")

    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--num-epochs", type=int, default=7_500)
    parser.add_argument("--mutation-rate", type=float, default=0.024 / 100.0)
    parser.add_argument("--tape-size", type=int, default=64)
    parser.add_argument("--num-programs", type=int, default=32_400)
    parser.add_argument("--grid-width", type=int, default=240)
    parser.add_argument("--grid-height", type=int, default=135)
    parser.add_argument("--gif-path", type=str, default="universe.gif")
    parser.add_argument(
        "--mp4-path",
        type=str,
        default=None,
        help="MP4 output path; defaults to --gif-path with .mp4 suffix",
    )
    parser.add_argument("--gif-every", type=int, default=20)
    parser.add_argument("--gif-fps", type=int, default=20)
    args = parser.parse_args()

    if args.grid_width * args.grid_height != args.num_programs:
        raise ValueError("grid_width * grid_height must equal num_programs")
    if args.gif_every <= 0:
        raise ValueError("--gif-every must be > 0")
    if args.gif_fps <= 0:
        raise ValueError("--gif-fps must be > 0")
    if args.tape_size != 64:
        raise ValueError("--tape-size must be 64 to render each tape as an 8x8 grid")

    rng = np.random.default_rng(args.seed)
    programs = rng.integers(
        0, 256, size=(args.grid_width, args.grid_height, args.tape_size), dtype=np.uint8
    )

    frames = run_epochs(
        programs,
        args.num_epochs,
        args.mutation_rate,
        rng,
        gif_every=args.gif_every,
    )
    save_evolution_gif(frames, args.gif_path, args.gif_fps)
    print(f"wrote GIF: {Path(args.gif_path).resolve()}")
