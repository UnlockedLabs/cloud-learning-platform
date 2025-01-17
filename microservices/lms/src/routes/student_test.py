"""
  Tests for User endpoints
"""
import os
import mock
import pytest

# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import
from common.testing.client_with_emulator import client_with_emulator
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from common.models import (CourseTemplate, Cohort, User,
                           CourseEnrollmentMapping,Section)
from testing.test_config import BASE_URL
from schemas.schema_examples import COURSE_TEMPLATE_EXAMPLE,\
   COHORT_EXAMPLE, TEMP_USER,CREDENTIAL_JSON, STUDENT_RECORDS_MODEL
from config import USER_MANAGEMENT_BASE_URL




os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
SUCCESS_RESPONSE = {"status": "Success"}


@pytest.fixture
def create_fake_data():
  """_summary_

  Args:
      course_template_id (_type_): _description_
      cohort_id (_type_): _description_
      section_id (_type_): _description_

  Returns:
      _type_: _description_
  """
  course_template = CourseTemplate.from_dict(COURSE_TEMPLATE_EXAMPLE)
  course_template.save()
  COHORT_EXAMPLE["course_template"] = course_template
  cohort = Cohort.from_dict(COHORT_EXAMPLE)
  cohort.save()

  test_section_dict = {
      "name": "section_name",
      "section": "section c",
      "description": "description",
      "classroom_id": "cl_id",
      "classroom_code": "cl_code",
      "classroom_url": "https://classroom.google.com",
      "course_template": course_template,
      "cohort": cohort,
      "enrollment_status":"OPEN",
      "status":"ACTIVE",
      "max_students":25
  }

  section = Section.from_dict(test_section_dict)
  section.save()
  temp_user = User.from_dict(TEMP_USER)
  temp_user.user_id = ""
  temp_user.save()
  temp_user.user_id = temp_user.id
  temp_user.update()
  user_id = temp_user.user_id

  course_enrollment_mapping= CourseEnrollmentMapping()
  course_enrollment_mapping.role = "learner"
  course_enrollment_mapping.user = temp_user
  course_enrollment_mapping.section = section
  course_enrollment_mapping.status = "active"
  course_enrollment_mapping.save()


  return {
      "cohort": cohort.id,
      "course_template": course_template.id,
      "section": section.id,
      "user_id":user_id,
      "email":temp_user.email
  }


def test_get_progress_percentage(client_with_emulator):
  url = BASE_URL + "/sections/9xieFlma8bcWYyLPOg0c/" + \
    "get_progress_percentage/clplmstestuser1@gmail.com"
  with mock.patch\
  ("routes.student.get_user_id",return_value="user_id"):
    with mock.patch("routes.student.classroom_crud.get_course_work_list",
                    return_value=[{}, {}]):
      with mock.patch(
          "routes.student.classroom_crud.get_submitted_course_work_list",
          return_value=[{
              "state": "TURNED_IN"
          }, {
              "state": "TURNED_IN"
          }]):
        resp = client_with_emulator.get(url)
  assert resp.status_code == 200

def test_get_student_in_section(client_with_emulator,create_fake_data):
  url = (BASE_URL
         + f"/sections/{create_fake_data['section']}/students/"
         + create_fake_data["email"])

  with mock.patch("routes.student.get_user_id",
        return_value=create_fake_data["user_id"]):
    resp = client_with_emulator.get(url)
  assert resp.status_code == 200

def test_list_student_of_section(client_with_emulator,create_fake_data):
  url = BASE_URL + f"/sections/{create_fake_data['section']}/students"
  resp = client_with_emulator.get(url)
  assert resp.status_code == 200

def test_delete_student_from_section(client_with_emulator,create_fake_data):
  user_id = create_fake_data["user_id"]
  section_id = create_fake_data["section"]
  url = BASE_URL + f"/sections/{section_id}/students/{user_id}"
  with mock.patch("routes.student.classroom_crud.delete_student",
                  return_value=[{}, {}]):
    with mock.patch("routes.student.classroom_crud.get_user_details",
                  return_value={"data":{"email":"clplmstestuser1@gmail.com"}}):
      with mock.patch("routes.student.section_service."
                        + "insert_section_enrollment_to_bq"
                                  ):
        resp = client_with_emulator.delete(url)
  assert resp.status_code == 200

def test_delete_student_sectionid_not_found\
(client_with_emulator,create_fake_data):
  user_id = create_fake_data["user_id"]
  section_id = "test_section_id"
  # url = BASE_URL + f"/student/{user_id}/section/{section_id}"
  url = BASE_URL + f"/sections/{section_id}/students/{user_id}"
  with mock.patch("routes.student.classroom_crud.delete_student",
                  return_value=[{}, {}]):
    with mock.patch("routes.student.classroom_crud.get_user_details",
                  return_value={"data":{"email":"clplmstestuser1@gmail.com"}}):
      resp = client_with_emulator.delete(url)
  assert resp.status_code == 404

def test_enroll_student_negative(client_with_emulator):
  url = BASE_URL + "/cohorts/fake_id_cohort/students"
  input_data = {
      "email": "student@gmail.com",
      "access_token": CREDENTIAL_JSON["token"]
  }
  with mock.patch("routes.section.classroom_crud.enroll_student"):
    with mock.patch("routes.section.Logger"):
      resp = client_with_emulator.post(url, json=input_data)

  assert resp.status_code == 404, "Status 404"
  assert resp.json()["success"] is False, "Check success"

def test_enroll_student(client_with_emulator, create_fake_data):

  url = BASE_URL + f"/cohorts/{create_fake_data['cohort']}/students"
  input_data = {
      "email": "student@gmail.com",
      "access_token": CREDENTIAL_JSON["token"]
  }
  course_user=User.from_dict(TEMP_USER)
  course_user.user_id=""
  course_user.email=input_data["email"]
  course_user.user_id=course_user.save().id
  course_user.update()
  with mock.patch("routes.student.classroom_crud.enroll_student",
  return_value ={"user_id":course_user.user_id}):
    with mock.patch(
      "services.student_service.check_student_can_enroll_in_cohort",
    return_value =True):
      with mock.patch("routes.student.Logger"):
        with mock.patch("routes.student.section_service."
                        + "insert_section_enrollment_to_bq"
                                  ):
          resp = client_with_emulator.post(url, json=input_data)
  assert resp.status_code == 200, "Status 200"
  assert resp.json()["success"] is True
  assert resp.json()["data"]["classroom_url"] == "https://classroom.google.com"
  assert resp.json()["data"]["classroom_id"] == "cl_id"

def test_enroll_student_already_present(client_with_emulator, create_fake_data):

  url = BASE_URL + f"/cohorts/{create_fake_data['cohort']}/students"
  input_data = {
      "email": "student@gmail.com",
      "access_token": CREDENTIAL_JSON["token"]
  }
  with mock.patch("routes.student.classroom_crud.enroll_student",
  return_value ={"user_id":"test_user_id"}):
    with mock.patch(
      "services.student_service.check_student_can_enroll_in_cohort",
    return_value =False):
      with mock.patch("routes.student.Logger"):
        resp = client_with_emulator.post(url, json=input_data)
  assert resp.status_code == 409, "Status 409"
  assert resp.json()["success"] is False

def test_enroll_student_already_present_section\
  (client_with_emulator, create_fake_data):

  url = BASE_URL + f"/sections/{create_fake_data['section']}/students"
  input_data = {
      "email": "student@gmail.com",
      "access_token": CREDENTIAL_JSON["token"]
  }
  with mock.patch("routes.student.classroom_crud.enroll_student",
  return_value ={"user_id":"test_user_id"}):
    with mock.patch(
  "routes.student.student_service.check_student_can_enroll_in_cohort",
    return_value =False):
      with mock.patch("routes.student.Logger"):
        resp = client_with_emulator.post(url, json=input_data)
  assert resp.status_code == 409, "Status 409"
  assert resp.json()["success"] is False

def test_enroll_student_section(client_with_emulator, create_fake_data):

  url = BASE_URL + f"/sections/{create_fake_data['section']}/students"
  input_data = {
      "email": "student@gmail.com",
      "access_token": CREDENTIAL_JSON["token"]
  }
  course_user=User.from_dict(TEMP_USER)
  course_user.user_id=""
  course_user.email=input_data["email"]
  course_user.user_id=course_user.save().id
  course_user.update()
  with mock.patch("routes.student.Logger"):
    with mock.patch("routes.student.classroom_crud.enroll_student",
      return_value ={"user_id":course_user.user_id}):
      with mock.patch(
  "routes.student.student_service.check_student_can_enroll_in_cohort",
        return_value =True):
        with mock.patch(
          "routes.student.section_service"
          + ".insert_section_enrollment_to_bq"
                                  ):
          resp = client_with_emulator.post(url, json=input_data)
  assert resp.status_code == 200, "Status 200"
  assert resp.json()["success"] is True
  assert resp.json()["data"]["classroom_url"] == "https://classroom.google.com"
  assert resp.json()["data"]["classroom_id"] == "cl_id"

def test_enroll_student_section_closed_enrollment(
    client_with_emulator, create_fake_data):

  url = BASE_URL + f"/sections/{create_fake_data['section']}/students"
  input_data = {
      "email": "student@gmail.com",
      "access_token": CREDENTIAL_JSON["token"]
  }
  section = Section.find_by_id(create_fake_data["section"])
  section.enrollment_status = "CLOSED"
  section.update()
  course_user=User.from_dict(TEMP_USER)
  course_user.user_id=""
  course_user.email=input_data["email"]
  course_user.user_id=course_user.save().id
  course_user.update()
  with mock.patch("routes.student.Logger"):
    with mock.patch("routes.student.classroom_crud.enroll_student",
      return_value ={"user_id":course_user.user_id}):
      with mock.patch(
    "routes.student.student_service.check_student_can_enroll_in_cohort",
        return_value =True):
        resp = client_with_emulator.post(url, json=input_data)
  print(resp.json())
  assert resp.status_code == 422, "Status 422"

def test_enroll_student_section_failed_section(
    client_with_emulator, create_fake_data):

  url = BASE_URL + f"/sections/{create_fake_data['section']}/students"
  input_data = {
      "email": "student@gmail.com",
      "access_token": CREDENTIAL_JSON["token"]
  }
  section = Section.find_by_id(create_fake_data["section"])
  section.status = "FAILED_TO_PROVISION"
  section.update()
  course_user=User.from_dict(TEMP_USER)
  course_user.user_id=""
  course_user.email=input_data["email"]
  course_user.user_id=course_user.save().id
  course_user.update()
  with mock.patch("routes.student.Logger"):
    with mock.patch("routes.student.classroom_crud.enroll_student",
      return_value ={"user_id":course_user.user_id}):
      with mock.patch(
    "routes.student.student_service.check_student_can_enroll_in_cohort",
        return_value =True):
        resp = client_with_emulator.post(url, json=input_data)
  print(resp.json())
  assert resp.status_code == 422, "Status 422"


def test_enroll_student_section_enrollment_count(
  client_with_emulator, create_fake_data):

  url = BASE_URL + f"/sections/{create_fake_data['section']}/students"
  input_data = {
      "email": "student@gmail.com",
      "access_token": CREDENTIAL_JSON["token"]
  }
  section = Section.find_by_id(create_fake_data["section"])
  section.enrolled_students_count = section.max_students +1
  section.update()
  course_user=User.from_dict(TEMP_USER)
  course_user.user_id=""
  course_user.email=input_data["email"]
  course_user.user_id=course_user.save().id
  course_user.update()
  with mock.patch("routes.student.Logger"):
    with mock.patch("routes.student.classroom_crud.enroll_student",
      return_value ={"user_id":course_user.user_id}):
      with mock.patch(
  "routes.student.student_service.check_student_can_enroll_in_cohort",
        return_value =True):
        resp = client_with_emulator.post(url, json=input_data)
  print(resp.json())
  assert resp.status_code == 422, "Status 422"


def test_enroll_student_section_negative(client_with_emulator):
  url = BASE_URL + "/sections/fake_section_id/students"
  input_data = {
      "email": "student@gmail.com",
      "access_token": CREDENTIAL_JSON["token"]
  }
  with mock.patch("routes.section.classroom_crud.enroll_student"):
    with mock.patch("routes.section.Logger"):
      resp = client_with_emulator.post(url, json=input_data)

  assert resp.status_code == 404, "Status 404"
  assert resp.json()["success"] is False, "Check success"

def test_get_student_in_cohort_email(client_with_emulator,create_fake_data):
  cohort_id = create_fake_data["cohort"]
  url = BASE_URL + f"/cohorts/{cohort_id}/students/clplmstestuser1@gmail.com"
  with mock.patch\
  ("routes.student.classroom_crud.get_user_details",
   return_value={"data":TEMP_USER}):
    with mock.patch\
  ("routes.student.get_user_id",
   return_value=create_fake_data["user_id"]):
      resp = client_with_emulator.get(url)
  assert resp.status_code == 200
  assert resp.json()["data"]["cohort_id"] == cohort_id

def test_get_student_in_cohort_user_id(client_with_emulator,create_fake_data):
  cohort_id = create_fake_data["cohort"]
  user_id = create_fake_data["user_id"]
  url = BASE_URL + f"/cohorts/{cohort_id}/students/{user_id}"
  with mock.patch\
  ("routes.student.classroom_crud.get_user_details",
   return_value={"data":TEMP_USER}):
    resp = client_with_emulator.get(url)
  assert resp.status_code == 200
  assert resp.json()["data"]["cohort_id"] == cohort_id

def test_get_student_in_invalid_cohort(client_with_emulator,create_fake_data):
  user_id = create_fake_data["user_id"]
  url = BASE_URL + f"/cohorts/invalid_id/students/{user_id}"
  with mock.patch\
  ("routes.student.classroom_crud.get_user_details",
   return_value={"data":TEMP_USER}):
    resp = client_with_emulator.get(url)
  assert resp.status_code == 404

def test_invite_student_to_section_api(client_with_emulator,create_fake_data):
  section_id=create_fake_data["section"]
  url = BASE_URL + f"/sections/{section_id}/invite/clplmstest_user4@gmail.com"
  with mock.patch\
  ("routes.student.student_service.invite_student",
   return_value={"invitation_id":"abcde",
                  "course_enrollment_id":"course_enrollment_id",
                  "user_id":"user_id",
                  "section_id":"section.id",
                  "cohort_id":"section.cohort.key",
            "classroom_id":"section.classroom_id",
            "classroom_url":"section.classroom_url"}):
    with mock.patch(
      "routes.student.student_service.check_student_can_enroll_in_cohort",
                    return_value=True):
      with mock.patch(
        "services.section_service" +
        ".insert_section_enrollment_to_bq"):
        resp = client_with_emulator.post(url)
  assert resp.status_code == 200

def test_invite_student_to_cohort_api(client_with_emulator,create_fake_data):
  section_id=create_fake_data["section"]
  url = BASE_URL + f"/sections/{section_id}/invite/clplmstest_user4@gmail.com"
  with mock.patch\
  ("routes.student.student_service.invite_student",
   return_value={"invitation_id":"abcde",
                  "course_enrollment_id":"course_enrollment_id",
                  "user_id":"user_id",
                  "section_id":"section.id",
                  "cohort_id":"section.cohort.key",
            "classroom_id":"section.classroom_id",
            "classroom_url":"section.classroom_url"}):
    with mock.patch(
      "services.student_service.check_student_can_enroll_in_cohort",
    return_value =True):
      with mock.patch(
        "services.section_service"
        + ".insert_section_enrollment_to_bq"):
        resp = client_with_emulator.post(url)
  assert resp.status_code == 200

def test_invite_student_to_cohort_archived_section(
    client_with_emulator,create_fake_data):
  section_id=create_fake_data["section"]
  section = Section.find_by_id(section_id)
  section.status = "ARCHIVED"
  section.update()
  url = BASE_URL + f"/sections/{section_id}/invite/clplmstest_user4@gmail.com"
  with mock.patch\
  ("routes.student.student_service.invite_student",
   return_value={"invitation_id":"abcde",
                  "course_enrollment_id":"course_enrollment_id",
                  "user_id":"user_id",
                  "section_id":"section.id",
                  "cohort_id":"section.cohort.key",
            "classroom_id":"section.classroom_id",
            "classroom_url":"section.classroom_url"}):
    with mock.patch(
      "services.student_service.check_student_can_enroll_in_cohort",
    return_value =True):
      resp = client_with_emulator.post(url)
  assert resp.status_code == 422


def test_get_list_of_students_exists_in_db_not_in_classroom(
  client_with_emulator):
  url = BASE_URL + "/student/exists_in_db_not_in_classroom"
  data=STUDENT_RECORDS_MODEL.copy()
  data["user_email"]=data.pop("email")
  with mock.patch("routes.student.run_query",
                  return_value=[data]):
    resp = client_with_emulator.get(url)
  assert resp.status_code == 200, "Status 200"
  assert resp.json()["data"][0]["email"] == STUDENT_RECORDS_MODEL[
    "email"], "Return data doesn't match."

def test_get_list_of_students_exists_in_classroom_not_in_db(
  client_with_emulator):
  url = BASE_URL + "/student/exists_in_classroom_not_in_db"
  data=STUDENT_RECORDS_MODEL.copy()
  data["user_emailAddress"]=data.pop("email")
  with mock.patch("routes.student.run_query",
                  return_value=[data]):
    resp = client_with_emulator.get(url)
  assert resp.status_code == 200, "Status 200"
  assert resp.json()["data"][0]["email"] ==STUDENT_RECORDS_MODEL[
    "email"], "Return data doesn't match."
