"""
Pydantic Model for copy course API's
"""
import datetime
from typing import Optional
from pydantic import BaseModel, constr
from schemas.schema_examples import CREDENTIAL_JSON, SECTION_EXAMPLE,INSERT_SECTION_EXAMPLE,ASSIGNMENT_MODEL


class Sections(BaseModel):
  """Sections Details """
  id: str
  name: str
  section: str
  description: str
  classroom_id: str
  classroom_code: str
  classroom_url: str
  teachers: list[constr(min_length=7, max_length=128,
      regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")]
  course_template: str
  cohort: str

  class Config():
    orm_mode = True
    schema_extra = {"example": SECTION_EXAMPLE}


class SectionDetails(BaseModel):
  """Course Detail model"""
  name: str
  description: str
  course_template: str
  cohort: str
  teachers: list[constr(min_length=7, max_length=128,
    regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")]
  class Config():
    orm_mode=True
    schema_extra={"example":INSERT_SECTION_EXAMPLE}


class SectionListResponseModel(BaseModel):
  """Get a list of sections"""
  success: Optional[bool] = True
  message: Optional[str] = "Success list"
  data: Optional[list[Sections]] = []

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Success",
            "data": [SECTION_EXAMPLE]
        }
    }



class CreateSectiontResponseModel(BaseModel):
  """Create Section Response Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created the section"
  data: Optional[Sections]

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully created the section",
            "section": SECTION_EXAMPLE
        }
    }


class GetSectiontResponseModel(BaseModel):
  """Get  Section Response Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Success"
  data: Optional[Sections] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Success",
            "data": SECTION_EXAMPLE
        }
    }


class UpdateSectionResponseModel(BaseModel):
  """Update  Section Response Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Success"
  data: Optional[Sections] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Section Updated successfully",
            "data": SECTION_EXAMPLE
        }
    }


class SectionResponseModel(BaseModel):
  """Get a list of sections"""
  success: Optional[bool] = True
  message: Optional[str] = "Success list"
  data: Optional[list[Sections]] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully send the list of  course ",
            "data": []
        }
    }


class CredentialKeys(BaseModel):
  """Credential model"""
  token: str
  refresh_token: str
  token_uri: str
  client_id: str
  client_secret: str
  scopes: list[str]
  expiry: str

  class Config():
    orm_mode = True
    schema_extra = {"example": CREDENTIAL_JSON}


class DeleteSectionResponseModel(BaseModel):
  """Delete section Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully deleted the section"
  data: Optional[str] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully deleted the section",
            "data": None
        }
    }

class DeleteStudentFromSectionResponseModel(BaseModel):
  """Delete student from section Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully deleted the student from course"
  data: Optional[str] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully deleted the section",
            "data": None
        }
    }
class StudentListResponseModel(BaseModel):
  """list student for section  response Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Success"
  data: Optional[list] =[]

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Success",
            "data":[{
      "first_name": "steve4",
      "last_name": "jobs",
      "email": "clplmstestuser1@gmail.com",
      "user_type": "other",
      "user_groups": [],
      "status": "active",
      "is_registered":True,
      "failed_login_attempts_count": 0,
      "access_api_docs": False,
      "gaia_id": "F2GGRg5etyty",
      "user_id": "vtETClM9JdWBSUBB4ZEr",
      "created_time": "2023-01-24 17:38:32.689496+00:00",
      "last_modified_time": "2023-01-24 17:38:32.823430+00:00",
      "user_type_ref": "cnkybYRTLPobwyo52JBR"}]
      }
      }
class AssignmentModel(BaseModel):
  """Assignment Details Model"""
  id: str
  classroom_id: str
  title: Optional[str] = None
  description: Optional[str] = None
  link: Optional[str] = None
  state: Optional[str] = None
  creation_time: str
  update_time: str
  due_date: Optional[datetime.date] = None
  due_time: Optional[datetime.time] = None
  max_grade: Optional[int] = None
  work_type: Optional[str] = None
  assignee_mode: Optional[str] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": ASSIGNMENT_MODEL
    }
     