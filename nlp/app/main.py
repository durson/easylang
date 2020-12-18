import orjson as json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import Response

from zh_cmn.engine import ZhCmnEngine

cfg = json.loads(Path("config.json").read_text())
app = FastAPI()

engines = {
    ZhCmnEngine.iso(): ZhCmnEngine(cfg)
}

print("ready..")

@app.post("/nlp/generate", response_class=Response)
async def nlp_generate(request: Request):
    headers = request.headers
    corrid = headers.get("corrid", None)
    if corrid is None:
        detail = "Corrid not specified"
        raise HTTPException(status_code=400, detail=detail)
    lang = headers.get("lang", None)
    if lang is None:
        detail = "Lang not specified"
        raise HTTPException(status_code=400, detail=detail)
    text = (await request.body()).decode()
    if text == "":
        detail = "Text empty"
        raise HTTPException(status_code=400, detail=detail)
    engine = engines.get(lang, None)
    if engine is None:
        detail = f"Engine not found for lang {lang}"
        raise HTTPException(status_code=400, detail=detail)
    try:
        output = engine.predict(corrid, text)
    except Exception as e:
        detail = f"Engine error {e}"
        raise HTTPException(status_code=400, detail=detail)
    output_json = json.dumps({
        "output": output,
        "input": text,
        "lang": lang,
        "corrid": corrid,
    }).decode()
    print(output_json)
    return output_json


@app.post("/nlp/describe", response_class=Response)
async def nlp_generate(request: Request):
    headers = request.headers
    lang = headers.get("lang", None)
    if lang is None:
        detail = "Lang not specified"
        raise HTTPException(status_code=400, detail=detail)
    text = (await request.body()).decode()
    if text == "":
        detail = "Text empty"
        raise HTTPException(status_code=400, detail=detail)
    engine = engines.get(lang, None)
    if engine is None:
        detail = f"Engine not found for lang {lang}"
        raise HTTPException(status_code=400, detail=detail)
    try:
        output = engine.describe(text)
    except Exception as e:
        detail = f"Engine error {e}"
        raise HTTPException(status_code=400, detail=detail)
    output_json = json.dumps({
        "output": output,
        "input": text,
        "lang": lang,
    }).decode()
    print(output_json)
    return output_json
