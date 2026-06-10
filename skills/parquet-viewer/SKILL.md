---
name: parquet-viewer
description: Parquet 파일을 웹 브라우저에서 테이블로 탐색하는 뷰어를 띄운다. 사용자가 parquet 파일 보기, parquet 열기, 데이터 확인, 테이블 뷰어, parquet 탐색, 데이터 미리보기 등을 요청할 때 사용한다. 단일 파일, part 파일 여러 개가 든 디렉터리, HDFS에서 다운로드한 parquet 모두 지원한다.
---

# Parquet Viewer

Parquet 파일을 로컬 웹서버로 띄워 브라우저에서 탐색하는 스킬.
스크립트는 이 스킬 디렉터리의 `scripts/parquet_viewer.py`에 있다.

## 실행 방법 (중요)

서버는 포그라운드에서 계속 실행되므로 **반드시 백그라운드로 실행**한다.
일반 실행하면 셸이 블로킹되고 타임아웃 시 서버가 죽는다.

1. Bash 도구의 `run_in_background: true`로 실행한다.
2. 출력에서 `READY http://localhost:<port>` 줄을 확인한다.
   (포트가 사용 중이면 자동으로 다음 포트를 찾으므로, 요청한
   포트가 아닐 수 있다 — 반드시 READY 줄의 실제 URL을 확인할 것)
3. 사용자에게 실제 URL을 알려준다. 브라우저는 기본으로 자동 열린다.

```bash
# 백그라운드 실행 (run_in_background: true)
python3 <skill-dir>/scripts/parquet_viewer.py data.parquet
```

**옵션:**
| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--port`, `-p` | 시작 포트 (사용 중이면 자동으로 +1씩 탐색) | `8765` |
| `--rows`, `-n` | 앞 N행만 읽기 — 전체 로드 없이 빠르게 동작 | 전체 |
| `--no-open` | 브라우저 자동 열기 비활성화 | 자동 열기 |

## 큰 파일 다루기

`--rows`는 pyarrow로 **앞 N행만 읽으므로** 파일이 수 GB여도 빠르다.
100MB가 넘거나 행 수를 모르는 파일은 `--rows 50000` 정도로 시작하는
것이 안전하다. 뷰어 상단에 "샘플: 전체 N행 중 앞 M행"으로 표시되므로
사용자가 전체가 아님을 알 수 있다.

```bash
python3 <skill-dir>/scripts/parquet_viewer.py -n 50000 big_data.parquet
```

## part 파일 디렉터리

Spark/HDFS 출력처럼 `part-00000-*.parquet`가 여러 개 있는 디렉터리는
디렉터리 경로를 그대로 넘기면 전부 합쳐서 보여준다.

```bash
python3 <skill-dir>/scripts/parquet_viewer.py /tmp/my_table/
```

HDFS에 있는 데이터는 먼저 로컬로 다운로드한다. 빠르게 훑어보는
목적이면 part 1개만 받아도 충분하다.

```bash
cx dfs get hdfs://camino/.../part-00000-xxx.snappy.parquet /tmp/sample.parquet
python3 <skill-dir>/scripts/parquet_viewer.py /tmp/sample.parquet
```

## 서버 종료

같은 파일을 다시 띄우거나 사용자가 다 봤다고 하면 서버를 정리한다.

```bash
lsof -ti:<port> | xargs kill
```

포트 충돌은 걱정할 필요 없다 — 스크립트가 빈 포트를 자동으로 찾는다.
다만 같은 데이터의 옛 서버가 떠 있으면 사용자가 혼동할 수 있으니,
동일 파일을 다시 띄울 때는 기존 서버를 먼저 종료한다.

## 뷰어 기능

- **페이지네이션**: 100행 단위
- **검색**: 전체 텍스트 또는 `컬럼명:값` 형태
- **정렬**: 컬럼 헤더 클릭
- **컬럼 토글**: 필요한 컬럼만 표시/숨기기
- **컬럼 타입 표시**: 헤더에 dtype 표시
