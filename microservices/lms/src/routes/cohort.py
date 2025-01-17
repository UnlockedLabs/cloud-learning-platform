'''Cohort Endpoint'''
import traceback
import datetime
from fastapi import APIRouter, Request
from common.models import Cohort, CourseTemplate,CourseEnrollmentMapping
from common.models.section import Section
from common.utils.logging_handler import Logger
from common.utils.errors import ResourceNotFoundException, ValidationError
from common.utils.http_exceptions import ResourceNotFound, InternalServerError, BadRequest
from common.utils import classroom_crud
from common.utils.cache_service import set_key, get_key
from common.utils.bq_helper import insert_rows_to_bq
from schemas.cohort import (CohortListResponseModel, CohortModel,
                            CreateCohortResponseModel, InputCohortModel,
                            DeleteCohortResponseModel,
                            UpdateCohortResponseModel, UpdateCohortModel)
from schemas.error_schema import (InternalServerErrorResponseModel,
                                  NotFoundErrorResponseModel,
                                  ConflictResponseModel,
                                  ValidationErrorResponseModel)
from schemas.section import SectionListResponseModel
from schemas.student import (GetProgressPercentageCohortResponseModel,GetOverallPercentage)
from config import BQ_TABLE_DICT,BQ_DATASET
from utils.helper import (convert_cohort_to_cohort_model,
                          convert_section_to_section_model)
from utils.user_helper import get_user_id


router = APIRouter(prefix="/cohorts",
                   tags=["Cohorts"],
                   responses={
                       500: {
                           "model": InternalServerErrorResponseModel
                       },
                       404: {
                           "model": NotFoundErrorResponseModel
                       },
                       409: {
                           "model": ConflictResponseModel
                       },
                       422: {
                           "model": ValidationErrorResponseModel
                       }
                   })


@router.get("", response_model=CohortListResponseModel)
def get_cohort_list(skip: int = 0, limit: int = 10):
  """Get a list of Cohort endpoint
    Raises:
        HTTPException: 500 Internal Server Error if something fails.

    Returns:
        CohortListModel: object which contains list of Cohort object.
        InternalServerErrorResponseModel:
            if the get cohort list raises an exception.
    """
  try:
    if skip < 0:
      raise ValidationError("Invalid value passed to \"skip\" query parameter")
    if limit < 1:
      raise ValidationError\
        ("Invalid value passed to \"limit\" query parameter")
    fetched_cohort_list = Cohort.fetch_all(skip=skip, limit=limit)
    if fetched_cohort_list is None:
      return {
          "message":
          "Successfully get the cohort list, but the list is empty.",
          "cohort_list": []
      }
    cohort_list = [
        convert_cohort_to_cohort_model(i) for i in fetched_cohort_list
    ]
    return {"cohort_list": cohort_list}
  except ValidationError as ve:
    raise BadRequest(str(ve)) from ve
  except ResourceNotFoundException as re:
    raise ResourceNotFound(str(re)) from re
  except Exception as e:
    print(e.message)
    Logger.error(e)
    raise InternalServerError(str(e)) from e


@router.get("/{cohort_id}", response_model=CohortModel)
def get_cohort(cohort_id: str):
  """Get a Cohort endpoint

    Args:
        cohort_id (str): unique id of the cohort

    Raises:
        ResourceNotFoundException: If the Cohort does not exist.
        HTTPException: 500 Internal Server Error if something fails.

    Returns:
        CohortModel: Cohort object for the provided id
        NotFoundErrorResponseModel: if the Cohort not found,
        InternalServerErrorResponseModel: if the get Cohort raises an exception
    """
  try:
    cohort = Cohort.find_by_id(cohort_id)
    loaded_cohort = convert_cohort_to_cohort_model(cohort)
    return loaded_cohort
  except ResourceNotFoundException as re:
    raise ResourceNotFound(str(re)) from re
  except Exception as e:
    Logger.error(e)
    raise InternalServerError(str(e)) from e


@router.post("", response_model=CreateCohortResponseModel)
def create_cohort(input_cohort: InputCohortModel):
  """Create a Cohort endpoint

    Args:
        input_cohort (InputCohortModel): input Cohort to be inserted

    Raises:
        ResourceNotFoundException: If the Course Template does not exist.
        Exception: 500 Internal Server Error if something went wrong

    Returns:
        CreateCohortResponseModel: Cohort Object,
        NotFoundErrorResponseModel: if the Course template not found,
        InternalServerErrorResponseModel:
            if the Cohort creation raises an exception
  """
  try:
    cohort_dict = {**input_cohort.dict()}
    course_template = CourseTemplate.find_by_id(
        cohort_dict["course_template_id"])
    cohort_dict.pop("course_template_id")
    cohort = Cohort.from_dict(cohort_dict)
    cohort.course_template = course_template
    cohort_id = cohort.save().id
    rows=[{
      "cohortId":cohort_id,\
        "name":cohort_dict["name"],\
        "description":cohort_dict["description"],\
        "startDate":cohort_dict["start_date"],\
        "endDate":cohort_dict["end_date"],\
        "registrationStartDate":cohort_dict["registration_start_date"],\
        "registrationEndDate":cohort_dict["registration_end_date"],\
        "maxStudents":cohort_dict["max_students"],\
        "timestamp":datetime.datetime.utcnow()
    }]
    insert_rows_to_bq(
      rows=rows,
      dataset=BQ_DATASET,
      table_name=BQ_TABLE_DICT["BQ_COLL_COHORT_TABLE"]
      )
    return {"cohort": convert_cohort_to_cohort_model(cohort)}
  except ResourceNotFoundException as re:
    raise ResourceNotFound(str(re)) from re
  except Exception as e:
    Logger.error(e)
    raise InternalServerError(str(e)) from e


@router.patch("/{cohort_id}", response_model=UpdateCohortResponseModel)
def update_cohort(cohort_id: str, update_cohort_model: UpdateCohortModel):
  """Update Cohort API

    Args:
        update_cohort_model (UpdateCohortModel):
            pydantic model object which contains update details
    Raises:
        InternalServerError: 500 Internal Server Error if something fails
        ResourceNotFoundException :
          404 if cohort or course template id not found
    Returns:
        UpdateCohort: Returns Updated Cohort object,
        InternalServerErrorResponseModel:
            if the Cohort updation raises an exception
    """
  try:
    cohort_details = Cohort.find_by_id(cohort_id)
    update_cohort_dict = {**update_cohort_model.dict()}
    if not any(update_cohort_dict.values()):
      raise ValidationError("Invalid request please provide some data " +
                            f"to update the Cohort with id {cohort_id}")
    for key in update_cohort_dict:
      if update_cohort_dict[key] is not None:
        if key == "course_template":
          course_template = CourseTemplate.find_by_id(update_cohort_dict[key])
          setattr(cohort_details, key, course_template)
        else:
          setattr(cohort_details, key, update_cohort_dict[key])
    cohort_details.update()
    rows=[{
      "cohortId":cohort_id,\
        "name":update_cohort_dict["name"],\
        "description":update_cohort_dict["description"],\
        "startDate":update_cohort_dict["start_date"],\
        "endDate":update_cohort_dict["end_date"],\
        "registrationStartDate":update_cohort_dict["registration_start_date"],\
        "registrationEndDate":update_cohort_dict["registration_end_date"],\
        "maxStudents":update_cohort_dict["max_students"],\
        "timestamp":datetime.datetime.utcnow()
    }]
    insert_rows_to_bq(
      rows=rows,
      dataset=BQ_DATASET,
      table_name=BQ_TABLE_DICT["BQ_COLL_COHORT_TABLE"]
      )
    return {
        "message": f"Successfully Updated the Cohort with id {cohort_id}",
        "cohort": convert_cohort_to_cohort_model(cohort_details)
    }
  except ValidationError as ve:
    raise BadRequest(str(ve)) from ve
  except ResourceNotFoundException as err:
    Logger.error(err)
    raise ResourceNotFound(str(err)) from err
  except Exception as e:
    Logger.error(e)
    raise InternalServerError(str(e)) from e


@router.delete("/{cohort_id}", response_model=DeleteCohortResponseModel)
def delete_cohort(cohort_id: str):
  """Delete a Cohort endpoint
    Args:
        cohort_id (str): unique id of the Cohort

    Raises:
        ResourceNotFoundException: If the Cohort does not exist
        HTTPException: 500 Internal Server Error if something fails

    Returns:
        DeleteCohortModel: if the Cohort is deleted,
        NotFoundErrorResponseModel: if the Cohort not found,
        InternalServerErrorResponseModel:
            if the Cohort deletion raises an exception
    """
  try:
    Cohort.soft_delete_by_id(cohort_id)
    return {"message": f"Successfully deleted the Cohort with id {cohort_id}"}
  except ResourceNotFoundException as re:
    raise ResourceNotFound(str(re)) from re
  except Exception as e:
    Logger.error(e)
    raise InternalServerError(str(e)) from e


@router.get("/{cohort_id}/sections", response_model=SectionListResponseModel)
def list_section(cohort_id: str, skip: int = 0, limit: int = 10):
  """ Get a list of sections of one cohort from db

  Args:
    cohort_id(str):cohort id from firestore db
  Raises:
    HTTPException: 500 Internal Server Error if something fails
    ResourceNotFound: 404 Resource not found exception
  Returns:
    {"status":"Success","data":{}}: Returns list of sections
    {'status': 'Failed',"data":null}
  """
  try:

    # Get cohort Id and create a reference of cohort object
    if skip < 0:
      raise ValidationError("Invalid value passed to \"skip\" query parameter")
    if limit < 1:
      raise ValidationError\
        ("Invalid value passed to \"limit\" query parameter")
    cohort = Cohort.find_by_id(cohort_id)
    # Using the cohort object reference key query sections model to get a list
    # of section of a perticular cohort
    result = Section.fetch_all_by_cohort(cohort_key=cohort.key,
                                         skip=skip,
                                         limit=limit)
    sections_list = list(map(convert_section_to_section_model, result))
    return {"data": sections_list}
  except ResourceNotFoundException as err:
    Logger.error(err)
    raise ResourceNotFound(str(err)) from err
  except ValidationError as ve:
    raise BadRequest(str(ve)) from ve
  except Exception as e:
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    raise InternalServerError(str(e)) from e

@router.get("/{cohort_id}/get_progress_percentage/{user}",
      response_model=GetProgressPercentageCohortResponseModel)
def get_progress_percentage(cohort_id: str, user: str, request: Request):
  """Get progress percentage of assignments turned in

  Args:
    cohort_id : cohort_id for which progess is required
    user : email id or user id for whol progress is required

  Raises:
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    A number indicative of the percentage of the course completed
    by the student,
    {'status': 'Failed'} if any exception is raise
  """
  try:
    headers = {"Authorization": request.headers.get("Authorization")}
    user_id = get_user_id(user=user.strip(), headers=headers)
    Logger.info(f"user id : {user_id}")
    section_with_progress_percentage = []
    cached_progress_percentage = get_key(f"{cohort_id}::{user_id}")
    if cached_progress_percentage is not None:
      section_with_progress_percentage = cached_progress_percentage
    else:
      cohort = Cohort.find_by_id(cohort_id)
      # Using the cohort object reference key query sections model to get a list
      # of section of a perticular cohort
      result = Section.fetch_all_by_cohort(cohort_key=cohort.key)
      for section in result:
        submitted_course_work_list = 0
        record = CourseEnrollmentMapping.\
          find_active_enrolled_student_record(section.key,user_id)
        if record is not None:
          course_work_list = len\
            (classroom_crud.get_course_work_list(section.key.split("/")[1]))
          submitted_course_work = classroom_crud.get_submitted_course_work_list(
          section.key.split("/")[1], user_id,headers)
          for submission_obj in submitted_course_work:
            if submission_obj["state"] == "TURNED_IN":
              submitted_course_work_list = submitted_course_work_list + 1
          progress_percent=0
          if course_work_list !=0:
            progress_percent = round\
          ((submitted_course_work_list / course_work_list) * 100, 2)
          else:
            progress_percent = 0
          data = {"section_id":\
          section.key.split("/")[1],"progress_percentage":\
            progress_percent}
          section_with_progress_percentage.append(data)
      cached_value = set_key(f"{cohort_id}::{user_id}",\
      section_with_progress_percentage, 3600)
      Logger.info\
      (f"progress percentage caching status for cohort_id \
      {cohort_id}, user_id {user_id} : {cached_value}")
    return {"data":section_with_progress_percentage}

  except ResourceNotFoundException as err:
    Logger.error(err)
    raise ResourceNotFound(str(err)) from err
  except ValidationError as ve:
    raise BadRequest(str(ve)) from ve
  except Exception as e:
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise InternalServerError(str(e)) from e

@router.get("/{cohort_id}/get_progress_percentage/not_turned_in/{user}",
      response_model=GetProgressPercentageCohortResponseModel)
def get_progress_percentage_not_turned_in(\
  cohort_id: str, user: str, request: Request):
  """Get progress percentage of assignments having assigned grades

  Args:
    cohort_id : cohort_id for which progess is required
    user : email id or user id for whol progress is required

  Raises:
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    A number indicative of the percentage of the course completed
    by the student,
    {'status': 'Failed'} if any exception is raise
  """
  try:
    headers = {"Authorization": request.headers.get("Authorization")}
    user_id = get_user_id(user=user.strip(), headers=headers)
    section_with_progress_percentage = []
    cached_progress_percentage = get_key(\
    f"not_turned_in::{cohort_id}::{user_id}")
    if cached_progress_percentage is not None:
      section_with_progress_percentage = cached_progress_percentage
    else:
      cohort = Cohort.find_by_id(cohort_id)
      # Using the cohort object reference key query sections model to get a list
      # of section of a perticular cohort
      result = Section.fetch_all_by_cohort(cohort_key=cohort.key)
      for section in result:
        submitted_course_work_list = 0
        record = CourseEnrollmentMapping.\
          find_active_enrolled_student_record(section.key,user_id)
        if record is not None:
          course_work_list = len\
            (classroom_crud.get_course_work_list(section.key.split("/")[1]))
          submitted_course_work = classroom_crud.get_submitted_course_work_list(
          section.key.split("/")[1], user_id,headers)
          for submission_obj in submitted_course_work:
            if "assignedGrade" in submission_obj:
              submitted_course_work_list = submitted_course_work_list + 1
          progress_percent=0
          if course_work_list !=0:
            progress_percent = round\
          ((submitted_course_work_list / course_work_list) * 100, 2)
          else:
            progress_percent = 0
          data = {"section_id":\
          section.key.split("/")[1],"progress_percentage":\
            progress_percent}
          section_with_progress_percentage.append(data)
      cached_value = set_key(\
      f"not_turned_in::{cohort_id}::{user_id}",\
      section_with_progress_percentage, 3600)
      Logger.info\
      (f"progress percentage caching status for \
       not_turned_in cohort_id \
      {cohort_id}, user_id {user_id} : {cached_value}")
    return {"data":section_with_progress_percentage}

  except ResourceNotFoundException as err:
    Logger.error(err)
    raise ResourceNotFound(str(err)) from err
  except ValidationError as ve:
    raise BadRequest(str(ve)) from ve
  except Exception as e:
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise InternalServerError(str(e)) from e

@router.get("/{cohort_id}/get_overall_grade/{user}",
      response_model=GetOverallPercentage)
def get_overall_percentage(cohort_id: str, user: str, request: Request):
  """Get overall grade for a student per course

  Args:
    cohort_id : cohort_id for which overall grade is required
    user : email id or user id for whose overall grade is required

  Raises:
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    A number indicative of the overall grade and category average
    by the student,
    {'status': 'Failed'} if any exception is raise
  """
  try:
    headers = {"Authorization": request.headers.get("Authorization")}
    overall_grade_response = []
    user_id = get_user_id(user=user.strip(), headers=headers)
    cohort = Cohort.find_by_id(cohort_id)
    result = Section.fetch_all_by_cohort(cohort_key=cohort.key)
    for section in result:
      record = CourseEnrollmentMapping.\
          find_active_enrolled_student_record(section.key,user_id)
      if record is not None:
        course_work_list = classroom_crud.get_coursework_list(
          section.classroom_id)
        submitted_course_work = classroom_crud.get_submitted_course_work_list(
        section.key.split("/")[1], user_id,headers)
        overall_grade = 0
        category_grade=[]
        for course_work_obj in course_work_list:
          # check if gradeCategory exists in the coursework object
          # check if assigned grade exists for the coursework in submitted \
          # coursework
          if ("gradeCategory" in course_work_obj and \
              "assignedGrade" in \
              next(item for item in submitted_course_work if \
              item["courseWorkId"] == \
              course_work_obj["id"])):
            category_id=course_work_obj["gradeCategory"]["id"]
            category_weight=course_work_obj["gradeCategory"]["weight"]/10000
            total_max_points = 0
            total_assigned_points = 0
            coursework_count=0
            category_data={"category_name":\
                            course_work_obj["gradeCategory"]["name"],\
                            "category_id":\
                            course_work_obj["gradeCategory"]["id"],\
                            "category_weight":category_weight,
                            "category_percent":0}
            for i in course_work_list:
              if ("gradeCategory" in i and \
              i["gradeCategory"]["id"] == category_id and \
              "assignedGrade" in \
              next(item for item in submitted_course_work if \
              item["courseWorkId"] == \
              i["id"])):
                total_max_points = total_max_points+i["maxPoints"]
                total_assigned_points = total_assigned_points+\
                next(item for item in submitted_course_work if \
                    item["courseWorkId"] == i["id"])["assignedGrade"]
                coursework_count = coursework_count+1
            category_data["category_percent"] = \
            round((total_assigned_points/total_max_points)*100,2)
            if not any(d["category_id"] == category_id for \
            d in category_grade):
              category_grade.append(category_data)
            # calculate coursework weight with respect to the category weight
            assignment_weight = \
            (course_work_obj["maxPoints"]/total_max_points)*\
            (category_weight/100)
            assigned_grade_by_max_points = \
            next(item for item in submitted_course_work if \
            item["courseWorkId"] == \
            course_work_obj["id"])["assignedGrade"]/\
            course_work_obj["maxPoints"]
            # calculate coursework's contribution towards overall grade
            assignment_grade=assigned_grade_by_max_points*assignment_weight
            overall_grade = overall_grade+assignment_grade
        data={"section_id":section.key.split("/")[1],\
          "overall_grade":round(overall_grade*100,2),\
              "category_grade":category_grade}
        overall_grade_response.append(data)
    return {"data":overall_grade_response}

  except ResourceNotFoundException as err:
    Logger.error(err)
    raise ResourceNotFound(str(err)) from err
  except ValidationError as ve:
    raise BadRequest(str(ve)) from ve
  except Exception as e:
    Logger.error(e)
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    raise InternalServerError(str(e)) from e
