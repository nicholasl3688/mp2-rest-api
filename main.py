import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import DatasetInfo, DatasetStorage, HealthResponse, setup_logging, ProcessConfig, ProcessingReport, log_requests
from data_pipeline import create_cleaning_report, process_data, validate_dataframe


setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
storage = DatasetStorage()
app.middleware("http")(log_requests)




@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return {"status": "ok", "version": "1.0.0"}

@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix != ".csv":
        logger.warning(f"Unsupported file format: {suffix}")
        raise HTTPException( status_code=400, detail="Unsupported file type")
    
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
        logger.warning(f"Parsing errors. Errors: {error}")
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {error}")


    dataset_id = storage.save(df, file.filename)
    metadata = storage.get_metadata(dataset_id)
    logger.info(f"Uploaded dataset: id={dataset_id}, filename={file.filename}, rows={len(df)} ")
    return metadata
#returns metadata



@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)):
    """Return up to limit rows from a stored dataset."""
    df = storage.get(dataset_id)
    if df is None:
        logger.warning(f"ID not found: {dataset_id}")
        raise HTTPException( status_code=404, detail="ID not found")

    records = json.loads(df.head(limit).to_json(orient="records"))
    logger.info(f"Retrieved dataset: id={dataset_id}, rows returned={len(records)}")
    return {"id": dataset_id,
            "data": records,
            "total_rows": len(df)}
# return {"id": dataset_id, "data": records, "total_rows": len(df)}




@app.post(
    "/datasets/{dataset_id}/process",
    response_model=ProcessingReport
)
def process_dataset(dataset_id: int, config: ProcessConfig):
    """Validate and process a stored dataset using MP1 functions."""
    # TODO: retrieve, validate, process, report, update, and return.
    df = storage.get(dataset_id)
    if df is None:
        raise HTTPException( status_code=404, detail="Dataset does not exist")
    conf = config.model_dump()

    for col in conf["validation"]["numeric_columns"]:
        if col not in df.columns:
            raise HTTPException( status_code=400, detail=f"Missing column: {col}")
    
    try:
        validated_df = validate_dataframe(df, conf["validation"]["required_columns"], conf["validation"]["numeric_columns"])
        rows_removed = len(df) - len(validated_df) 
        validated_copy = validated_df.copy()
        processed_df = process_data(validated_copy, conf)
    except ValueError as error:
        raise HTTPException( status_code=400, detail=str(error))

    

    logger.info(f"Processed dataset: id={dataset_id}, validation_removed={rows_removed}, rows_before={len(validated_copy)}, rows_after={len(processed_df)}")
    report = create_cleaning_report(validated_copy, processed_df)

    storage.update(dataset_id, processed_df)

    return {"id": dataset_id, "validation_rows_removed": rows_removed, "cleaning_report": report}
