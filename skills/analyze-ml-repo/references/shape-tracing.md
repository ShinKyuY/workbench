# Shape Tracing Tactics (텐서 형상 추적 전술)

Use these when a tensor shape is **not obvious from reading the code**
— runtime-decided dimensions, `einops`/`rearrange`, collapsing
`view/reshape(-1)`, broadcasting, dynamic batching. The goal is to
recover a concrete shape with evidence; when you cannot, label it
honestly (`inferred`/`unavailable`) per the report contract rather
than guessing.

## 1. Substitute config symbols with numbers

The forward pass is usually written in symbols (`D`, `H`, `hidden_size`).
Read the config first, then substitute so the trace carries real
numbers: `[B, N, hidden_size]` → `[B, N, 512]`. Cite both the config
line and the code line. If a dimension stays symbolic (e.g. sequence
length `N` chosen at runtime), state the config-bounded max and mark it
inferred.

## 2. Mine tests and asserts for ground-truth shapes

Test files and inline `assert x.shape == (...)` are the most reliable
source — they are shapes the authors confirmed. Search:

- `assert .*\.shape`, `\.shape ==`, `torch.Size`, `expected_shape`
- test files that build the model with concrete inputs
  (`torch.randn(2, 3, 224, 224)`, `jnp.ones((2, 128))`)

The dummy input in a test or in `model.init(rng, x)` gives you the
true input shape and batch example.

## 3. Read einops / rearrange patterns literally

`einops` strings encode the shape transform explicitly — decode them
instead of guessing:

- `rearrange(x, "b (h w) c -> b c h w", h=H)` — splits a flattened
  spatial axis; `h*w` was the sequence length, now `[B, C, H, W]`.
- `rearrange(x, "b n (h d) -> b h n d", h=heads)` — the classic
  multi-head split; `d = D / heads`.
- `repeat`, `reduce` change count/rank — note which axis appears or
  collapses.

Named axes make the before/after unambiguous; write both shapes.

## 4. Resolve `-1` and flattening

`view(B, -1)` / `reshape(-1, D)` hide a dimension. Compute it from the
surrounding known dims (the `-1` is `total_elements / known_dims`).
State what the `-1` resolves to, e.g. `[B, C, H, W]` → `view(B, -1)`
→ `[B, C*H*W] = [B, 2048]`.

## 5. Track broadcasting explicitly

When two tensors of different rank combine (`a + b`, `a * mask`), the
result takes the broadcast shape. Note the broadcast so the output
shape is not mistaken for one of the inputs — e.g. `scores [B, H, N, N]
+ mask [1, 1, N, N]` → `[B, H, N, N]`.

## 6. Follow existing print/hook/log traces

Authors often leave shape-debugging behind. Search for
`print(.*shape)`, logging of shapes, `register_forward_hook`, or
notebook cells with `.shape` output already captured — these are
confirmed values you can cite.

## When all tactics fail

If the shape genuinely cannot be pinned down (decided by data at
runtime, no test, no config bound), do **not** invent it. Record it in
the report's "unverified/assumed items" block with what you confirmed
and what evidence (a data sample, a run) would resolve it.
