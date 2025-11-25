# app.py  (放在 /root/graphrag_course/)
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import graphrag.api as gr_api
from graphrag.config.load_config import load_config
from graphrag.storage.file_pipeline_storage import FilePipelineStorage
from graphrag.utils.storage import load_table_from_storage
import asyncio
import logging, traceback
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(".")                         # settings.yaml 所在目录
CFG  = load_config(ROOT)
STORE = FilePipelineStorage(ROOT / CFG.output.base_dir)

app = FastAPI(title="GraphRAG API")

from graphrag.utils.storage import load_table_from_storage, storage_has_table  # ← 多了 storage_has_table

@app.on_event("startup")
async def preload():
    global ENTITIES, TEXT_UNITS, COMMUNITIES, COMMUNITY_REP, RELATIONSHIPS, COVARIATES

    ENTITIES       = await load_table_from_storage("entities", STORE)
    TEXT_UNITS     = await load_table_from_storage("text_units", STORE)
    COMMUNITIES    = await load_table_from_storage("communities", STORE)
    COMMUNITY_REP  = await load_table_from_storage("community_reports", STORE)
    RELATIONSHIPS  = await load_table_from_storage("relationships", STORE)

    # <- 新写法：先判断再加载
    if await storage_has_table("covariates", STORE):
        COVARIATES = await load_table_from_storage("covariates", STORE)
    else:
        COVARIATES = None          # 或者 pd.DataFrame()

class QueryReq(BaseModel):
    query: str = Field(..., description="用户问题")
    method: str = Field("local", description="local | global | drift | basic")



BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
async def root():
    # 直接返回文件
    return FileResponse(BASE_DIR / "static" / "index.html", media_type="text/html")


@app.post("/query")
async def query(req: QueryReq):
    try:
        if req.method == "local":
            resp, ctx = await gr_api.local_search(
                config=CFG,
                entities=ENTITIES,
                communities=COMMUNITIES,
                community_reports=COMMUNITY_REP,
                text_units=TEXT_UNITS,
                relationships=RELATIONSHIPS,
                covariates=COVARIATES,
                query=req.query,           # 用户问题
                community_level=1,         # 0=实体级, 1=社区级, 2=跨社区
                response_type="text",      # 或 "json" / 自定义描述
            )
        elif req.method == "global":
            resp, ctx = await gr_api.global_search(
                config=CFG,
                entities=ENTITIES,
                communities=COMMUNITIES,
                community_reports=COMMUNITY_REP,
                query=req.query,
            )
        else:
            raise HTTPException(400, f"不支持的 method={req.method}")
        return {"answer": resp, "context": str(ctx)}
    except Exception as e:
        logging.exception("GraphRAG 查询失败")   # ← 打印完整回溯
        raise HTTPException(500, str(e))
