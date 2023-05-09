"""
Pydantic Model for Course template API's
"""
from typing import Optional
from pydantic import BaseModel, constr
from schemas.schema_examples import COURSE_TEMPLATE_EXAMPLE, INSERT_COURSE_TEMPLATE_EXAMPLE, UPDATE_COURSE_TEMPLATE_EXAMPLE


class CourseTemplateModel(BaseModel):
  """Course Template Pydantic Model"""
  id: str
  name: str
  description: str
  admin: str
  classroom_id: Optional[str]
  classroom_code: Optional[str]
  classroom_url: Optional[str]

  class Config():
    orm_mode = True
    schema_extra = {"example": COURSE_TEMPLATE_EXAMPLE}


class UpdateCourseTemplateModel(BaseModel):
  """Update Course Template Pydantic Model"""
  name: Optional[str] = None
  description: Optional[str] = None

  class Config():
    orm_mode = True
    schema_extra = {"example": UPDATE_COURSE_TEMPLATE_EXAMPLE}


class CourseTemplateListModel(BaseModel):
  """Pydantic Course Template Response Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully get the course template list"
  course_template_list: Optional[list[CourseTemplateModel]] = []

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully get the course template list",
            "course_template_list": [COURSE_TEMPLATE_EXAMPLE]
        }
    }


class CreateCourseTemplateResponseModel(BaseModel):
  """Create Course Template Response Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created the course template"
  course_template: Optional[CourseTemplateModel]

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully created the course template",
            "course_template": COURSE_TEMPLATE_EXAMPLE
        }
    }


class InputCourseTemplateModel(BaseModel):
  """Insert Course Template Model"""
  name: str
  description: str

  class Config():
    orm_mode = True
    schema_extra = {"example": INSERT_COURSE_TEMPLATE_EXAMPLE}


class DeleteCourseTemplateModel(BaseModel):
  """Delete Course Template Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully deleted the course template"
  data: Optional[str] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully deleted the course template",
            "data": None
        }
    }


class UpdateCourseTemplateResponseModel(BaseModel):
  """Update Course Template response Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully Updated the Course Template"
  course_template: Optional[CourseTemplateModel]

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully Updated the Course Template",
            "course_template": COURSE_TEMPLATE_EXAMPLE
        }
    }

class AddInstructionalDesigner(BaseModel):
  email: constr(min_length=7, max_length=128,
          regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
          to_lower=True)
  class Config():
    orm_mode = True
    schema_extra = {
      "example": {
        "email":"xyz@gmail.com"
      }
    }

class EnrollmentResponseModel(BaseModel):
  """Enrollment Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully enrolled instructional designer"
  data: Optional[dict] = {}
  
  class Config():
    orm_mode=True
    schema_extra ={
      "example":{
        "success": True,
        "message": "Successfully enrolled instructional designer",
        "data":{
        "enrollment_id": "12345678",
        "email": "xcvb@gmail.com",
        "course_template_id": "234red3fr32",
        "classroom_id": "234r21we123",
        "classroom_url": "https://classroom.google.com"
    }
      }
    }
