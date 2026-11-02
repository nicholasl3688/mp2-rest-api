# MP2 REST API

This is a FastAPI app that stores uploaded CSV files in memory and cleans them with the MP1 pipeline. It has four endpoints: GET /health returns the status and version; POST /upload accepts a CSV and returns its ID and column info; GET /datasets/{dataset_id} returns up to limit stored rows plus the total row count; and POST /datasets/{dataset_id}/process validates and cleans the stored data using settings from a JSON body, saves the result, and returns a cleaning report. Bad uploads return 400 and missing datasets return 404. Middleware logs every request with a request ID, status code, and duration. The API code is in src/, the copied MP1 modules are in data_pipeline/, and the pytest tests are in tests/.

## Run

pip install -r requirements.txt
python -m uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs to try the endpoints.

## Test

python -m pytest tests -v

## Output

14:46:38 DEBUG    src.storage — Stored dataset: id=1, rows=6
14:46:38 DEBUG    src.storage — Retrieved metadata: id=1
14:46:38 INFO     main — Uploaded dataset: id=1, filename=sample_data.csv, rows=6
14:46:38 INFO     src.middleware — request_id=8374de34 POST /upload status=200 duration=18.1ms
INFO:     127.0.0.1:63934 - "POST /upload HTTP/1.1" 200 OK
14:49:17 DEBUG    src.storage — Retrieved dataset copy: id=1, rows=6
14:49:17 WARNING  data_pipeline.data_validator — Removed 1 rows with invalid values in score
14:49:17 DEBUG    data_pipeline.data_validator — Validation: 6 -> 5 rows (1 removed)
14:49:17 DEBUG    data_pipeline.data_processor — Removed 1 duplicate rows
14:49:17 DEBUG    data_pipeline.data_processor — Dropped 1 rows
14:49:17 INFO     main — Processed dataset: id=1, validation_removed=1, rows_before=5, rows_after=3
14:49:17 DEBUG    src.storage — Updated dataset: id=1, rows=3
14:49:18 INFO     src.middleware — request_id=ca6a9818 POST /datasets/1/process status=200 duration=93.8ms