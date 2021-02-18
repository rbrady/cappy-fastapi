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


@app.post("/files2/", response_model=schemas.ReportFile)
async def create_report_file(report_file: schemas.ReportFileCreate, db: Session = Depends(get_db)):
    return crud.create_report(db=db, report_file=report_file)


@app.post("/reports/", response_model=schemas.Report)
async def create_report(report: schemas.ReportCreate, db: Session = Depends(get_db)):
    return crud.create_report(db=db, report=report)


@app.get("/reports/", response_model=List[schemas.Report])
async def get_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_reports(db, skip=skip, limit=limit)


@app.get("/reports/{report_id}", response_model=schemas.Report)
async def get_report(report_id, db: Session = Depends(get_db)):
    return crud.get_report(db, report_id=report_id)


@app.delete("/reports/{report_id}")
async def delete_report(report_id):
    return {"message": "Hello World"}
