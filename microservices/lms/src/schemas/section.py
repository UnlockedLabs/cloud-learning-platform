"""
Pydantic Model for copy course API's
"""
import datetime
from typing import Optional
from pydantic import BaseModel, constr
from schemas.student import UserModel
from schemas.schema_examples import CREDENTIAL_JSON, SECTION_EXAMPLE,\
  INSERT_SECTION_EXAMPLE,ASSIGNMENT_MODEL,\
    STUDENT,SHORT_COURSEWORK_MODEL,COURSE_ENROLLMENT_USER_EXAMPLE


class Sections(BaseModel):
  """Sections Details """
  id: str
  name: str
  section: str
  description: str
  classroom_id: str
  classroom_code: str
  classroom_url: str
  # teachers: list[constr(
  #     min_length=7,
  #     max_length=128,
  #     regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
  #     to_lower=True)]
  course_template: str
  cohort: str
  status: Optional[str]
  enrollment_status:Optional[str]
  enrolled_students_count: int
  max_students:int

  class Config():
    orm_mode = True
    schema_extra = {"example": SECTION_EXAMPLE}


class TempUsers(BaseModel):
  "User Details"
  user_id: str
  first_name: str
  last_name: str
  email: constr(min_length=7,
                max_length=128,
                regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                to_lower=True)
  user_type: str
  user_groups: Optional[list]
  status: str
  is_registered: Optional[bool] = True
  failed_login_attempts_count: Optional[int] = 0
  access_api_docs: Optional[bool] = False
  gaia_id: Optional[str] = ""
  photo_url: Optional[str] = ""


class SectionDetails(BaseModel):
  """Course Detail model"""
  name: str
  description: str
  course_template: str
  cohort: str
  max_students :int
  # teachers: list[constr(
  #     min_length=7,
  #     max_length=128,
  #     regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
  #     to_lower=True)]

  class Config():
    orm_mode = True
    schema_extra = {"example": INSERT_SECTION_EXAMPLE}


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


class TeachersListResponseModel(BaseModel):
  """Get a list of Teachers"""
  success: Optional[bool] = True
  message: Optional[str] = "Success"
  data: Optional[list[UserModel]] = []

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Success",
            "data": [COURSE_ENROLLMENT_USER_EXAMPLE]
        }
    }


class GetTeacherResponseModel(BaseModel):
  """Get a Teacher """
  success: Optional[bool] = True
  message: Optional[str] = "Success"
  data: Optional[UserModel] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Success",
            "data": COURSE_ENROLLMENT_USER_EXAMPLE
        }
    }


class EnrollTeacherSection(BaseModel):
  """Enroll Teacher in a section Model"""
  email: constr(min_length=7,
                max_length=128,
                regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                to_lower=True)

  class Config():
    orm_mode = True
    schema_extra = {"email": "teacher@gmail.com"}


class CreateSectiontResponseModel(BaseModel):
  """Create Section Response Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Your section will be created shortly"
  data: None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Your section will be created shortly",
            "data": None
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


class DeleteTeacherFromSectionResponseModel(BaseModel):
  """Delete Teacher from section Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully deleted the student from section"
  data: Optional[str] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully deleted teacher from section",
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
  data: Optional[list[UserModel]] = []

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Success",
            "data": [STUDENT]
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
    schema_extra = {"example": ASSIGNMENT_MODEL}


class GetCourseWorkList(BaseModel):
  """Coursework list model"""
  success: Optional[bool] = True
  message: Optional[str] = "Success"
  data: Optional[list] = []

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Success",
            "data": [SHORT_COURSEWORK_MODEL]
        }
    }


class ImportGradeResponseModel(BaseModel):
  """Import grade esponseModel Details Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Success"
  data: Optional[dict] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Success",
            "data": None
        }
    }

class UpdateEnrollmentStatusSectionModel(BaseModel):
  """Update  Section Response Model"""
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
class DeleteFailedSectionSectionModel(BaseModel):
  """Update  Section Response Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Success"
  data: Optional[int] = 0

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Success",
            "data": 2
        }
    }
class UpdateInviteResponseModel(BaseModel):
  """Invite Student Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully Updated the invitation status"
  data: Optional[dict] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully Invited the Student",
            "data": {
                "list_coursenrolment": [
                    "courseenrollment_id1", "courseenrollment_id2",
                    "courseenrollment_id3"
                ]
            }
        }
    }
