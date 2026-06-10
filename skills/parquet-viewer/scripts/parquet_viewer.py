#!/usr/bin/env python3
"""Parquet 파일 웹 뷰어 — 브라우저에서 테이블 탐색."""
import argparse
import json
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import pandas as pd
import pyarrow.dataset as pads

PAGE_SIZE = 100
PORT_TRIES = 20

HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>Parquet Viewer</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',
Roboto,sans-serif;background:#0f172a;color:#e2e8f0;padding:16px}
h1{font-size:1.2rem;margin-bottom:8px;color:#38bdf8}
.info{font-size:.85rem;color:#94a3b8;margin-bottom:12px}
.controls{display:flex;gap:12px;align-items:center;
margin-bottom:12px;flex-wrap:wrap}
.controls input,.controls select{background:#1e293b;
color:#e2e8f0;border:1px solid #334155;border-radius:6px;
padding:6px 10px;font-size:.85rem}
.controls input{width:260px}
.controls button{background:#2563eb;color:#fff;border:none;
border-radius:6px;padding:6px 14px;cursor:pointer;font-size:.85rem}
.controls button:hover{background:#1d4ed8}
.controls button:disabled{opacity:.4;cursor:default}
.table-wrap{overflow:auto;max-height:calc(100vh - 160px);
border:1px solid #334155;border-radius:8px}
table{border-collapse:collapse;font-size:.78rem;white-space:nowrap}
th,td{padding:5px 10px;border:1px solid #1e293b}
th{background:#1e293b;position:sticky;top:0;z-index:2;
color:#38bdf8;cursor:pointer;user-select:none}
th:hover{background:#334155}
th .dtype{display:block;font-size:.65rem;color:#64748b;
font-weight:normal}
tr:nth-child(even){background:#1e293b44}
tr:hover{background:#334155}
td{max-width:320px;overflow:hidden;text-overflow:ellipsis}
.page-info{font-size:.82rem;color:#94a3b8}
.col-toggle{display:flex;flex-wrap:wrap;gap:4px;
margin-bottom:10px;max-height:120px;overflow-y:auto;
background:#1e293b;padding:8px;border-radius:6px}
.col-toggle label{font-size:.75rem;color:#cbd5e1;cursor:pointer;
padding:2px 6px;border-radius:4px;background:#0f172a}
.col-toggle label:hover{background:#334155}
.col-toggle label.hidden-col{opacity:.35}
#search-count{font-size:.82rem;color:#fbbf24;margin-left:8px}
</style>
</head>
<body>
<h1>Parquet Viewer</h1>
<div class="info" id="info"></div>
<div class="controls">
  <input id="search" placeholder="검색 (컬럼:값  또는  전체 검색)">
  <button onclick="doSearch()">검색</button>
  <button onclick="clearSearch()">초기화</button>
  <span id="search-count"></span>
  <span style="flex:1"></span>
  <button id="prev" onclick="prevPage()">← 이전</button>
  <span class="page-info" id="page-info"></span>
  <button id="next" onclick="nextPage()">다음 →</button>
</div>
<details style="margin-bottom:8px">
  <summary style="cursor:pointer;color:#38bdf8;font-size:.85rem">
    컬럼 표시/숨기기</summary>
  <div class="col-toggle" id="col-toggle"></div>
</details>
<div class="table-wrap"><table id="tbl"></table></div>

<script>
let cols=[], dtypes=[], page=0, totalRows=0, totalPages=0,
  pageSize=100, sampled=false, sourceRows=0;
let hiddenCols=new Set(), sortCol=null, sortAsc=true;

async function fetchMeta(){
  const r=await fetch('/api/meta');
  const d=await r.json();
  cols=d.columns; dtypes=d.dtypes||[]; totalRows=d.total_rows;
  pageSize=d.page_size; sampled=d.sampled;
  sourceRows=d.source_rows;
  let info=d.file+' — '+totalRows.toLocaleString()+' rows × '
    +cols.length+' cols';
  if(sampled) info+=' (샘플: 전체 '
    +sourceRows.toLocaleString()+'행 중 앞 '
    +totalRows.toLocaleString()+'행)';
  document.getElementById('info').textContent=info;
  buildColToggle();
  loadPage(0);
}

function buildColToggle(){
  const el=document.getElementById('col-toggle');
  el.textContent='';
  cols.forEach(function(c,i){
    const lbl=document.createElement('label');
    lbl.id='ct-'+i;
    lbl.textContent=c;
    lbl.addEventListener('click',function(){toggleCol(i)});
    el.appendChild(lbl);
  });
}

function toggleCol(i){
  if(hiddenCols.has(i)) hiddenCols.delete(i);
  else hiddenCols.add(i);
  document.getElementById('ct-'+i).classList
    .toggle('hidden-col',hiddenCols.has(i));
  renderTable(window._lastData);
}

async function loadPage(p){
  const q=document.getElementById('search').value;
  const params=new URLSearchParams({page:p,page_size:pageSize});
  if(q) params.set('q',q);
  if(sortCol!==null){
    params.set('sort',cols[sortCol]);
    params.set('asc',sortAsc?1:0);
  }
  const r=await fetch('/api/data?'+params);
  const d=await r.json();
  page=d.page; totalPages=d.total_pages; totalRows=d.total_rows;
  document.getElementById('page-info').textContent=
    (page+1)+' / '+totalPages+' ('+totalRows.toLocaleString()
    +'건)';
  document.getElementById('prev').disabled=page<=0;
  document.getElementById('next').disabled=page>=totalPages-1;
  document.getElementById('search-count').textContent=
    q?'검색 결과: '
    +totalRows.toLocaleString()+'건':'';
  window._lastData=d.data;
  renderTable(d.data);
}

function renderTable(data){
  var tbl=document.getElementById('tbl');
  tbl.textContent='';
  var visCols=cols.map(function(_,i){return i})
    .filter(function(i){return !hiddenCols.has(i)});
  var thead=document.createElement('thead');
  var hrow=document.createElement('tr');
  visCols.forEach(function(i){
    var th=document.createElement('th');
    var arrow='';
    if(sortCol===i) arrow=sortAsc?' ▲':' ▼';
    th.textContent=cols[i]+arrow;
    if(dtypes[i]){
      var sp=document.createElement('span');
      sp.className='dtype';
      sp.textContent=dtypes[i];
      th.appendChild(sp);
    }
    th.addEventListener('click',function(){doSort(i)});
    hrow.appendChild(th);
  });
  thead.appendChild(hrow);
  tbl.appendChild(thead);
  var tbody=document.createElement('tbody');
  data.forEach(function(row){
    var tr=document.createElement('tr');
    visCols.forEach(function(i){
      var td=document.createElement('td');
      var v=row[cols[i]];
      if(v===null||v===undefined) v='';
      td.textContent=String(v);
      td.title=String(v);
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  tbl.appendChild(tbody);
}

function doSort(i){
  if(sortCol===i) sortAsc=!sortAsc;
  else{sortCol=i;sortAsc=true;}
  loadPage(page);
}
function prevPage(){if(page>0)loadPage(page-1)}
function nextPage(){if(page<totalPages-1)loadPage(page+1)}
function doSearch(){loadPage(0)}
function clearSearch(){
  document.getElementById('search').value='';
  sortCol=null;sortAsc=true;loadPage(0);
}
document.getElementById('search')
  .addEventListener('keydown',function(e){
    if(e.key==='Enter')doSearch()
  });
fetchMeta();
</script>
</body>
</html>"""


def load_data(path, max_rows=None):
    """parquet 파일 또는 part 파일 디렉터리를 DataFrame으로 로드.

    max_rows가 있으면 pyarrow dataset으로 앞 N행만 읽어
    대용량 파일도 메모리 부담 없이 연다.
    """
    print(f"Loading {path} ...", flush=True)
    ds = pads.dataset(path, format="parquet")
    source_rows = ds.count_rows()
    if max_rows and source_rows > max_rows:
        df = ds.head(max_rows).to_pandas()
        print(
            f"Sampled first {max_rows:,} of "
            f"{source_rows:,} rows",
            flush=True,
        )
    else:
        df = ds.to_table().to_pandas()
    print(
        f"Loaded {len(df):,} rows x {len(df.columns)} cols",
        flush=True,
    )
    return df, source_rows


def sanitize_chunk(chunk):
    """JSON 직렬화 불가 값(bytes 등)을 문자열로 변환."""
    chunk = chunk.copy()
    for c in chunk.columns:
        if chunk[c].dtype == object:
            chunk[c] = chunk[c].map(
                lambda v: v.hex()
                if isinstance(v, (bytes, bytearray))
                else v
            )
    return chunk


def make_handler(df, parquet_path, source_rows):
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/":
                self._html()
            elif parsed.path == "/api/meta":
                self._meta()
            elif parsed.path == "/api/data":
                self._data(parse_qs(parsed.query))
            else:
                self.send_error(404)

        def _html(self):
            self.send_response(200)
            self.send_header(
                "Content-Type", "text/html; charset=utf-8"
            )
            self.end_headers()
            self.wfile.write(HTML.encode())

        def _meta(self):
            self._json({
                "file": parquet_path,
                "columns": list(df.columns),
                "dtypes": [str(t) for t in df.dtypes],
                "total_rows": len(df),
                "source_rows": source_rows,
                "sampled": len(df) < source_rows,
                "page_size": PAGE_SIZE,
            })

        def _data(self, qs):
            p = int(qs.get("page", [0])[0])
            ps = int(qs.get("page_size", [PAGE_SIZE])[0])
            q = qs.get("q", [""])[0].strip()
            sort_col = qs.get("sort", [None])[0]
            asc = qs.get("asc", ["1"])[0] == "1"

            subset = df
            if q:
                if ":" in q:
                    col_name, val = q.split(":", 1)
                    col_name = col_name.strip()
                    val = val.strip()
                    if col_name in df.columns:
                        subset = subset[
                            subset[col_name].astype(str)
                            .str.contains(
                                val, case=False, na=False
                            )
                        ]
                else:
                    mask = pd.Series(
                        False, index=subset.index
                    )
                    for c in subset.columns:
                        mask |= (
                            subset[c].astype(str)
                            .str.contains(
                                q, case=False, na=False
                            )
                        )
                    subset = subset[mask]

            if sort_col and sort_col in subset.columns:
                subset = subset.sort_values(
                    sort_col, ascending=asc,
                    na_position="last",
                )

            total = len(subset)
            total_pages = max(1, (total + ps - 1) // ps)
            p = max(0, min(p, total_pages - 1))
            chunk = sanitize_chunk(
                subset.iloc[p * ps:(p + 1) * ps]
            )

            self._json({
                "page": p,
                "total_pages": total_pages,
                "total_rows": total,
                "data": json.loads(
                    chunk.to_json(
                        orient="records",
                        force_ascii=False,
                        date_format="iso",
                    )
                ),
            })

        def _json(self, obj):
            self.send_response(200)
            self.send_header(
                "Content-Type", "application/json"
            )
            self.end_headers()
            self.wfile.write(
                json.dumps(obj, ensure_ascii=False).encode()
            )

        def log_message(self, fmt, *args):
            pass

    return Handler


def bind_server(handler, start_port):
    """start_port부터 빈 포트를 찾아 서버를 바인딩."""
    for port in range(start_port, start_port + PORT_TRIES):
        try:
            return HTTPServer(("", port), handler), port
        except OSError:
            print(
                f"Port {port} in use, trying {port + 1}",
                flush=True,
            )
    raise SystemExit(
        f"No free port in {start_port}-"
        f"{start_port + PORT_TRIES - 1}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Parquet 파일 웹 뷰어"
    )
    parser.add_argument(
        "file",
        help="parquet 파일 또는 part 파일 디렉터리 경로",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=8765,
        help="서버 포트 (사용 중이면 자동으로 다음 포트 탐색)",
    )
    parser.add_argument(
        "-n", "--rows", type=int, default=None,
        help="최대 로딩 행 수 (앞 N행만 읽음)",
    )
    parser.add_argument(
        "--no-open", action="store_true",
        help="브라우저 자동 열기 비활성화",
    )
    args = parser.parse_args()

    df, source_rows = load_data(args.file, args.rows)
    handler = make_handler(df, args.file, source_rows)
    server, port = bind_server(handler, args.port)

    url = f"http://localhost:{port}"
    print(f"READY {url}", flush=True)

    if not args.no_open:
        webbrowser.open(url)

    server.serve_forever()


if __name__ == "__main__":
    main()
