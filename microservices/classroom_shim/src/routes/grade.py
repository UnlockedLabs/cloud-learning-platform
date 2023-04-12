''' Grade APIs '''
import traceback
from fastapi import APIRouter
from common.models import LTIAssignment
from common.utils.logging_handler import Logger
from common.utils.http_exceptions import InternalServerError
from common.utils.classroom_crud import (post_grade_of_the_user,
                                         get_submitted_course_work_list)
from config import auth_client
from schemas.grade_schema import PostGradeModel, PostGradeResponseModel
from schemas.error_schema import (InternalServerErrorResponseModel,
                                  NotFoundErrorResponseModel,
                                  ValidationErrorResponseModel)

# pylint: disable=line-too-long, broad-exception-raised

router = APIRouter(
    tags=["Grade"],
    responses={
        500: {
            "model": InternalServerErrorResponseModel
        },
        404: {
            "model": NotFoundErrorResponseModel
        },
        422: {
            "model": ValidationErrorResponseModel
        }
    })


@router.post("/grade", response_model=PostGradeResponseModel)
def update_classroom_grade(input_grade: PostGradeModel):
  """Post/Updates the student grade in the classroom for a given course
   work in a course"""

  try:
    input_grade_dict = {**input_grade.dict()}

    # TODO: Need to check where the comment can be added in the classroom
    if input_grade_dict["comment"]:
      pass

    if input_grade_dict["validate_title"]:
      lti_assignment_list = LTIAssignment.collection.filter(
          "lti_content_item_id", "==",
          input_grade_dict["lti_content_item_id"]).fetch()

      for i in lti_assignment_list:

        if i.lti_assignment_title == input_grade_dict["line_item_title"]:
          lti_assignment = i

    else:
      lti_assignment = LTIAssignment.collection.filter(
          "lti_content_item_id", "==",
          input_grade_dict["lti_content_item_id"]).get()

    lti_assignment_max_points = lti_assignment.max_points
    course_work_id = lti_assignment.course_work_id

    assigned_grade = input_grade_dict["assigned_grade"]

    if input_grade_dict["draft_grade"]:
      draft_grade = input_grade_dict["draft_grade"]
    else:
      draft_grade = assigned_grade

    if assigned_grade:
      assigned_grade = (assigned_grade / input_grade_dict["maximum_grade"]
                       ) * lti_assignment_max_points

    if draft_grade:
      draft_grade = (draft_grade / input_grade_dict["maximum_grade"]
                    ) * lti_assignment_max_points

    user_id = input_grade_dict["user_id"]

    headers = {"Authorization": f"Bearer {auth_client.get_id_token()}"}

    submissions = get_submitted_course_work_list(
        section_id=lti_assignment.section_id,
        user_id=user_id,
        headers=headers,
        course_work_id=course_work_id)

    if submissions:
      submission_id = submissions[0].get("id")
      post_grade_of_the_user(lti_assignment.section_id, course_work_id,
                             submission_id, assigned_grade, draft_grade)
    else:
      raise Exception(
          f"Submission not found for the user id - {user_id} and section id - {lti_assignment.section_id} and course work id - {course_work_id}"
      )

    return {"success": True}

  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e
