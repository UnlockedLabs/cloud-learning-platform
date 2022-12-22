import behave
import requests
from testing_objects.test_config import API_URL
from e2e.gke_api_tests.secrets_helper import get_student_email_and_token

# -------------------------------Enroll student to Section-------------------------------------
# ----Positive Scenario-----


@behave.given("A user has access privileges and wants to enroll a student into a section")
def step_impl_1(context):
    context.url = f'{API_URL}/sections/{context.sections.uuid}/students'
    context.payload = get_student_email_and_token()


@behave.when("API request is sent to enroll student to a section with correct request payload and valid section uuid")
def step_impl_2(context):
    resp = requests.post(context.url, json=context.payload,headers=context.header)
    context.status = resp.status_code
    context.response = resp.json()


@behave.then("Section will be fetch using the given uuid and student is enrolled using student credentials and a response model object will be return")
def step_impl_3(context):
    assert context.status == 200, "Status 200"
    assert context.response["success"] is True, "Check success"

# -----Negative Scenario-----


@behave.given("A user has access to portal and needs to enroll a student into a section")
def setp_impl_4(context):
    context.url = f'{API_URL}/sections/fake_uuid_data/students'
    context.payload = get_student_email_and_token()


@behave.when("API request is sent to enroll student to a section with correct request payload and invalid section uuid")
def step_impl_5(context):
    resp = requests.post(context.url, json=context.payload,headers=context.header)
    context.status = resp.status_code
    context.response = resp.json()


@behave.then("Student will not be enrolled and API will throw a resource not found error")
def step_impl_6(context):
    assert context.status == 404, "Status 404"
    assert context.response["success"] is False, "Check success"


@behave.given("A user has access to the portal and wants to enroll a student into a section")
def step_impl_7(context):
    context.url = f'{API_URL}/sections/{context.sections.uuid}/students'
    context.payload ={"email":"email@gmail.com","credentials":{"token":"token"}}
    

@behave.when("API request is sent to enroll student to a section with incorrect request payload and valid section uuid")
def step_impl_8(context):
    resp = requests.post(context.url, json=context.payload,headers=context.header)
    context.status = resp.status_code
    context.response = resp.json()


@behave.then("Student will not be enrolled and API will throw a validation error")
def step_impl_9(context):
    assert context.status == 422, "Status 422"
    assert context.response["success"] is False, "Check success"



