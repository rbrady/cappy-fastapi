from typing import List, Optional

from pydantic import BaseModel


# incoming
class ReportFileCreate(BaseModel):
    content_type: str
    filename: str
    label: str
    report_id: int


# outgoing
class ReportFile(BaseModel):
    id: int
    content_type: str
    filename: str
    label: str
    report_id: int

    class Config:
        orm_mode = True


# incoming
class ReportCreate(BaseModel):
    source: str
    policy: str
    exit_code: int
    files: List[ReportFile] = []
    pod: str
    namespace: str
    tag: str
    repo_digest: str


# outgoing
class Report(BaseModel):
    id: int
    source: str
    policy: str
    exit_code: int
    files: List[ReportFile] = []
    pod: str
    namespace: str
    tag: str
    repo_digest: str

    class Config:
        orm_mode = True

