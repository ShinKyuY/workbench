# Framework Cues (프레임워크별 관용구)

Read this **right after you identify the repo's framework** in
reconnaissance (Step 1). The reconnaissance patterns in `SKILL.md` are
kept framework-neutral so they match any repo; this file gives the
framework-specific signatures you grep for once you know which
framework(s) the repo uses. A repo may mix frameworks (e.g. a HF
Transformers model trained with a custom PyTorch loop) — read every
matching column.

## How to identify the framework first

Check imports and dependency files before anything else:

- `import torch` / `torch` in `requirements.txt`·`pyproject.toml` → **PyTorch**
- `import jax`, `flax`, `import haiku` → **JAX / Flax / Haiku**
- `import tensorflow`, `from tensorflow import keras` → **TF / Keras**
- `from transformers import ...`, `transformers` dependency → **HF Transformers**
  (sits on top of PyTorch **or** TF/JAX — identify the backend too)

## Signature table

| Concern | PyTorch | JAX / Flax | TF / Keras | HF Transformers |
|---------|---------|------------|------------|-----------------|
| Model definition | `class ...(nn.Module)` | `class ...(nn.Module)` (flax.linen) / `hk.Module` | `class ...(keras.Model)` / `keras.layers.Layer` | `class ...(PreTrainedModel)`, `AutoModel`, `AutoModelFor*` |
| Forward pass | `def forward(self, ...)` | `def __call__(self, ...)` / `setup()` (Flax), `hk.transform` | `def call(self, ...)` | `def forward` (PT backend) / `def call` (TF); `.generate()` for LMs |
| Layers | `nn.Linear`, `nn.Conv2d`, `nn.Embedding`, `nn.LSTM`, `nn.MultiheadAttention` | `nn.Dense`, `nn.Conv`, `nn.Embed`, `nn.MultiHeadDotProductAttention` | `keras.layers.Dense`, `Conv2D`, `Embedding`, `LSTM`, `MultiHeadAttention` | reuses the backend's layers; blocks in `modeling_*.py` |
| Params / state | attributes on `self`, `state_dict()` | explicit `params` pytree, `init()` / `apply(params, x)` | `self.trainable_variables`, weights on layers | `config` + backend params |
| Training loop | hand-written loop / `Trainer` (Lightning) | `jax.grad`/`value_and_grad`, `optax` update, `train_state.TrainState` | `model.fit()` / `GradientTape` | `transformers.Trainer`, `TrainingArguments`, `accelerate` |
| Loss | `nn.CrossEntropyLoss`, `F.*`, custom `nn.Module` | `optax.softmax_cross_entropy`, hand-written in loss fn | `keras.losses.*`, `model.compile(loss=...)` | loss returned inside model output (`outputs.loss`) |
| Optimizer | `torch.optim.*` | `optax.*` | `keras.optimizers.*` | `TrainingArguments` / `optim` arg |
| Config | argparse / `.yaml` / `dataclass` / OmegaConf-Hydra | same + `ml_collections.ConfigDict` | same + Keras `get_config()` | `config.json` → `PretrainedConfig` (`AutoConfig`) |
| Distributed | `DistributedDataParallel`, `FSDP`, `torchrun`, `deepspeed` | `jax.pmap`, `jax.pjit`/`shard_map`, `mesh`, `NamedSharding` | `tf.distribute.*Strategy`, `MirroredStrategy` | `accelerate`, `deepspeed`, `Trainer` handles it |
| Compile / perf | `torch.compile`, TorchScript | `jax.jit` | `tf.function`, XLA `jit_compile` | inherits backend |
| Checkpoint | `torch.save`/`load` (`.pt`, `.pth`), `state_dict` | `orbax`, `flax.training.checkpoints`, `msgpack` | `model.save`/`SavedModel`, `.h5`, `.ckpt` | `save_pretrained`/`from_pretrained` (`.safetensors`/`.bin` + `config.json`) |
| Entry point | `if __name__ == "__main__"`, `train.py` | same | same | `run_*.py` example scripts, `Trainer` |

## Framework-specific gotchas for shape tracing

- **JAX/Flax**: shapes are not attributes on `self`; they are determined
  by `init` with a dummy input. Look for the `jnp.ones(...)`/
  `jnp.zeros(...)` shape passed to `.init(rng, x)` to recover the input
  shape. Modules are functional — `apply(params, x)` — so trace
  `__call__`, not stored state.
- **TF/Keras**: `model.summary()` output (if committed in a notebook or
  test) gives per-layer output shapes directly. `build(input_shape)`
  encodes the expected input rank.
- **HF Transformers**: the real forward logic lives in
  `modeling_<arch>.py` (e.g. `modeling_llama.py`), not the thin
  `AutoModel` wrapper. Shapes and config numbers (`hidden_size`,
  `num_attention_heads`, `num_hidden_layers`) come from `config.json` /
  the `*Config` class — read that first, then trace the block classes.
- **PyTorch**: default and most detailed path; the `SKILL.md`
  procedures assume it.

See `shape-tracing.md` for tactics when a shape is not obvious in any
framework.
