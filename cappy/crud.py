from typing import Tuple

from sqlalchemy.orm import Session

import models
import schemas


def get_report(db: Session, report_id: int):
    return db.query(models.Report).filter(models.Report.id == report_id).first()


def get_reports(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Report).offset(skip).limit(limit).all()


def create_report(db: Session, report: schemas.ReportCreate):
    db_report = models.Report(
        source=report.source,
        policy=report.policy,
        exit_code=report.exit_code,
        pod=report.pod,
        namespace=report.namespace,
        tag=report.tag,
        repo_digest=report.repo_digest)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_report_files(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ReportFile).offset(skip).limit(limit).all()


def create_report_file(db: Session, uploaded_file: Tuple[str, str, str], report_id: int):
    db_report_file = models.ReportFile(
        report_id=report_id,
        filename=uploaded_file[0],
        content_type=uploaded_file[1],
        label=uploaded_file[2],
    )
    db.add(db_report_file)
    db.commit()
    db.refresh(db_report_file)
    return db_report_file

