"""Student API services"""
import re
import traceback
from common.utils import classroom_crud
from common.utils.logging_handler import Logger
from common.models import CourseEnrollmentMapping
from common.utils.errors import (ResourceNotFoundException)

def get_section_with_minimum_student(sections):
  """Get section with minimum count of students
  Args:
  sections :list of section objects with same cohort
  Returns: sectioons object with minimum count of studnet

  """
  min_sections_count_mapping = None
  min_student = 0
  for i in sections:
    if min_sections_count_mapping is None:
      min_sections_count_mapping = i
      min_student =  i.enrolled_students_count
    else :
      if i.enrolled_students_count < min_student:
        min_student =i.enrolled_students_count
        min_sections_count_mapping = i
  return min_sections_count_mapping

def get_user_id(user,headers):
  regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
  if re.fullmatch(regex, user):
    if classroom_crud.get_user_details_by_email(
        user_email=user.lower(), headers=headers)["data"] != []:
      return classroom_crud.get_user_details_by_email(
          user_email=user.lower(), headers=headers)["data"][0]["user_id"]
    else:
      raise ResourceNotFoundException(f"user {user} not found")
  return user

def check_student_can_enroll_in_cohort(email,headers,sections):
  """
    Args:
    sections :list of section objects with from same cohort
    email : student email
    headers : Authentication headers
    Returns: boolean value
    True : Student can be enroll

  """
  try:
    student_details = classroom_crud.get_user_details_by_email(user_email=email,
                                                               headers=headers)
  except ResourceNotFoundException as rte:
    err = traceback.format_exc().replace("\n", " ")
    Logger.error(err)
    Logger.error(rte)
    Logger.info("Student is not present in database")
    return True
  if student_details["data"] != []:
    user_id = student_details["data"][0]["user_id"]
    for section in sections:
      result = CourseEnrollmentMapping.find_course_enrollment_record(
                            section_key=section.key,
                            user_id=user_id)
      if result is not None:
        Logger.error(f"Student {email} is present in section_id {section.id}")
        return False
  return True
