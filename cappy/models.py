from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    source = Column(String)
    result = Column(String)
    pod = Column(String)
    namespace = Column(String)
    tag = Column(String)
    repo_digest = Column(String)

    files = relationship("ReportFile", back_populates="report")


class ReportFile(Base):
    __tablename__ = 'reportfiles'

    id = Column(Integer, primary_key=True)
    content_type = Column(String)
    filename = Column(String)
    report_id = Column(Integer, ForeignKey("reports.id"))
    label = Column(String)

    report = relationship("Report", back_populates="files")
