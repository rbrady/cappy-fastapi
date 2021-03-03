import shutil
from typing import List
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, UploadFile
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import SessionLocal, engine


# create the db tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/compliance/", response_model=schemas.Report)
async def ingest_report(
        source: str = Form(...),
        policy: str = Form(...),
        exit_code: int = Form(...),
        pod: str = Form(...),
        namespace: str = Form(...),
        tag: str = Form(...),
        repo_digest: str = Form(...),
        files: List[UploadFile] = File(...),
        db: Session = Depends(get_db)
):
    # iterate through the uploaded files and generate a unique name for them to avoid
    # filename collisions in the storage backend.  Collect the original filename and content type into a tuple with
    # the unique filename to send to the data layer.
    # ex: ("ab50d69f1e2b43cebadcd8da35262942', "text/xml", "my_report.xml")
    db_report = models.Report(
        source=source,
        policy=policy,
        exit_code=exit_code,
        pod=pod,
        namespace=namespace,
        tag=tag,
        repo_digest=repo_digest)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    saved_files = []
    for report_file in files:
        unique_filename = uuid4().hex
        with open(unique_filename, 'wb') as file_buffer:
            # TODO: replace the following line with whatever the file storage backend requires in anchore
            shutil.copyfileobj(report_file.file, file_buffer)
            # update the list of files with the created object returned
            saved_files.append(
                crud.create_report_file(
                    db=db,
                    uploaded_file=(unique_filename, report_file.content_type, report_file.filename),
                    report_id=db_report.id
                )
            )

    # refreshing the report should pick up the related objects
    db.refresh(db_report)

    return db_report

# use these methods to query and confirm the correct database records were created.
@app.get("/reports/", response_model=List[schemas.Report])
async def get_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_reports(db, skip=skip, limit=limit)


@app.get("/reports/{report_id}", response_model=schemas.Report)
async def get_report(report_id, db: Session = Depends(get_db)):
    return crud.get_report(db, report_id=report_id)


# DEPRECATED
# This was the previous design where the report and files were two separate methods
@app.post("/files/", response_model=List[schemas.ReportFile])
async def create_file(
        files: List[UploadFile] = File(...), report_id: str = Form(...), db: Session = Depends(get_db)
):
    # iterate through the uploaded files and generate a unique name for them to avoid
    # filename collisions in the storage backend.  Collect the original filename and content type into a tuple with
    # the unique filename to send to the data layer.
    # ex: ("ab50d69f1e2b43cebadcd8da35262942', "text/xml", "my_report.xml")
    saved_files = []
    for report_file in files:
        unique_filename = uuid4().hex
        with open(unique_filename, 'wb') as file_buffer:
            shutil.copyfileobj(report_file.file, file_buffer)
            saved_files.append(
                crud.create_report_file(
                    db=db,
                    uploaded_file=(unique_filename, report_file.content_type, report_file.filename),
                    report_id=report_id
                )
            )

    return saved_files


@app.post("/reports/", response_model=schemas.Report)
async def create_report(report: schemas.ReportCreate, db: Session = Depends(get_db)):
    return crud.create_report(db=db, report=report)

