---
name: parquet-viewer
description: >-
  Launch a browser table viewer for Parquet files (single file,
  multi-part directory, HDFS download). Use when the user wants to
  view, inspect, or preview parquet data — "parquet 열어줘",
  "데이터 미리보기", "테이블 뷰어".
---

# Parquet Viewer

Serves a Parquet file through a local web server for browsing in the
browser. The script lives at `scripts/parquet_viewer.py` in this skill
directory.

## Compatibility

Requires `python3`, `pandas`, and `pyarrow`
(`python3 -c "import pandas, pyarrow"` to check). If missing, install
into the active project or virtual environment, not globally.

## How to run (important)

The server keeps running in the foreground, so **always run it in the
background**. A normal run blocks the shell, and the server dies on
timeout.

1. Run with the available background/session mechanism. In Claude Code,
   use Bash `run_in_background: true`; in Codex, start it as a
   long-running exec session and keep the session id.
2. Find the `READY http://<host>:<port>` line in the output. The port
   may differ from the requested one if it was taken.
3. Tell the user the actual URL. The browser opens automatically by
   default.

```bash
# background/session run
python3 <skill-dir>/scripts/parquet_viewer.py data.parquet
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--port`, `-p` | Starting port (probes +1 at a time if in use) | `8765` |
| `--host` | Bind host. Use `0.0.0.0` only when the user needs access from another machine or container. The READY line then still prints `127.0.0.1`, so give the user this machine's address with that port | `127.0.0.1` |
| `--rows`, `-n` | Read only the first N rows — fast, no full load | all |
| `--no-open` | Disable auto-opening the browser | auto-open |

## Large files

`--rows` reads **only the first N rows** via pyarrow, so it is fast even
for multi-GB files. For files over 100MB or with an unknown row count,
starting with `--rows 50000` is the safe choice. The viewer header shows
"sample: first M of N rows", so the user can tell it is not the full
data.

```bash
python3 <skill-dir>/scripts/parquet_viewer.py -n 50000 big_data.parquet
```

## Directories of part files

For a directory holding multiple `part-00000-*.parquet` files (Spark/
HDFS output), pass the directory path as-is and everything is combined.
Hive-style partition directories (`dt=2024-01-01/…`) expose their keys
as columns.

```bash
python3 <skill-dir>/scripts/parquet_viewer.py /tmp/my_table/
```

Download HDFS data locally first. For a quick look, a single part file
is usually enough.

```bash
cx dfs get hdfs://camino/.../part-00000-xxx.snappy.parquet /tmp/sample.parquet
python3 <skill-dir>/scripts/parquet_viewer.py /tmp/sample.parquet
```

## Stopping the server

When relaunching the same file, or when the user says they are done,
kill the old server first — a stale server still serving the same data
confuses the user.

```bash
lsof -ti:<port> | xargs kill
```

## Viewer features

- **Pagination**: 100 rows per page
- **Search**: full text, or `column:value`. Literal substring match, no
  regex. If the text before the colon is not a column name, the whole
  string is searched as full text (so `07:00` finds timestamps)
- **Sort**: click a column header
- **Column toggle**: show/hide only the columns you need
- **Column types**: dtype shown in the header
