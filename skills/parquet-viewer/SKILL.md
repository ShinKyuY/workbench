---
name: parquet-viewer
description: >-
  Launch a web-browser table viewer for Parquet files. Use when the user
  wants to view a parquet file, open parquet, inspect data, browse a
  table, or preview data — including Korean phrasings such as
  "parquet 파일 보기", "parquet 열어줘", "데이터 확인", "테이블 뷰어",
  "parquet 탐색", "데이터 미리보기". Supports a single file, a directory
  containing multiple part files, and parquet downloaded from HDFS.
---

# Parquet Viewer

Serves a Parquet file through a local web server for browsing in the
browser. The script lives at `scripts/parquet_viewer.py` in this skill
directory.

## How to run (important)

The server keeps running in the foreground, so **always run it in the
background**. A normal run blocks the shell, and the server dies on
timeout.

1. Run with the Bash tool's `run_in_background: true`.
2. Find the `READY http://localhost:<port>` line in the output.
   (If the port is taken, the script probes the next one automatically,
   so the actual port may differ from the requested one — always check
   the URL on the READY line.)
3. Tell the user the actual URL. The browser opens automatically by
   default.

```bash
# background run (run_in_background: true)
python3 <skill-dir>/scripts/parquet_viewer.py data.parquet
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--port`, `-p` | Starting port (probes +1 at a time if in use) | `8765` |
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
clean up the server.

```bash
lsof -ti:<port> | xargs kill
```

Port collisions are not a concern — the script finds a free port
automatically. But an old server still serving the same data can confuse
the user, so kill the existing server before relaunching the same file.

## Viewer features

- **Pagination**: 100 rows per page
- **Search**: full text, or `column:value`
- **Sort**: click a column header
- **Column toggle**: show/hide only the columns you need
- **Column types**: dtype shown in the header
