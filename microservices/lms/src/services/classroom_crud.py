""" Hepler functions for classroom crud API """
from asyncio.log import logger
import datetime
from re import I
from fastapi import APIRouter, HTTPException
from common.utils.logging_handler import Logger
from fastapi.encoders import jsonable_encoder
from google.api_core.exceptions import PermissionDenied
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import traceback
import json
from google.protobuf.json_format import MessageToDict
from config import CLASSROOM_ADMIN_EMAIL,PROJECT_ID
from google_auth_oauthlib.flow import Flow
import google_crc32c


# disabling for linting to pass
# pylint: disable = broad-except



SUCCESS_RESPONSE = {"status": "Success"}
FAILED_RESPONSE = {"status": "Failed"}


def create_course(name,section,owner_id):
    SCOPES = ["https://www.googleapis.com/auth/classroom.courses",
    "https://www.googleapis.com/auth/classroom.courses.readonly"]

    # a_creds = service_account.Credentials.from_service_account_file(
    # "utils/service.json", scopes=SCOPES)
    # GKE_POD_SA_KEY=json.loads(GKE_POD_SA_KEY)
    a_creds = service_account.Credentials.from_service_account_info(GKE_POD_SA_KEY,scopes=SCOPES)
    creds = a_creds.with_subject(CLASSROOM_ADMIN_EMAIL)
    service = build("classroom", "v1", credentials=creds)
    new_course = {}
    new_course["name"]=name
    new_course["section"]=section
    # new_course["description"]=course["description"]
    # new_course["room"]=course["room"]
    new_course["ownerId"]=owner_id
    # new_course["descriptionHeading"]=course["description_heading"]

    course = service.courses().create(body=new_course).execute()
    course_name = course.get("name")
    course_id = course.get("id")
    return course

def get_secret_from_secret_manager():
    print("Called Function")
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    secret_id="gke-pod-sa-key"
    version_id="1"
    secret_name = f"projects/core-learning-services-dev/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": secret_name})
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        print("Data corruption detected.")
        return response
    payload = response.payload.data.decode("UTF-8")
    print("Plaintext: {}".format(payload))
    return payload



def get_course_by_id(course_id):
    SCOPES = ["https://www.googleapis.com/auth/classroom.courses",
    "https://www.googleapis.com/auth/classroom.courses.readonly"]
    a_creds = service_account.Credentials.from_service_account_file(
    "utils/service.json", scopes=SCOPES)
    creds = a_creds.with_subject(CLASSROOM_ADMIN_EMAIL)
    try:
        service = build("classroom", "v1", credentials=creds)
        course = service.courses().get(id=course_id).execute()
        return course

    except HttpError as error:
        logger.error(error)
        return None

def get_course_list():    
    SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.rosters']
    # a_creds = service_account.Credentials.from_service_account_file(
    # "utils/service.json", scopes=SCOPES)
    # creds = a_creds.with_subject(CLASSROOM_ADMIN_EMAIL)
    # service = build("classroom", "v1", credentials=creds)
    # results = service.courses().list().execute()
    # courses = results.get('courses', [])
    # info = (os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON_STRING'])
    # info = json.dumps(CLASSROOM_KEY)
    # print("SA _KEY",info)
    response = get_secret_from_secret_manager()
    CLASSROOM_KEY = json.loads(response)
    print("type of response",type(response))
    print(type(CLASSROOM_KEY))
    a_creds = service_account.Credentials.from_service_account_info(CLASSROOM_KEY,scopes=SCOPES)
   
    creds = a_creds.with_subject(CLASSROOM_ADMIN_EMAIL)

    print("cred  -------",creds)
    service = build("classroom", "v1", credentials=creds)
    results = service.courses().list().execute()
    courses = results.get('courses', [])
    return courses

def get_topics(course_id):
    SCOPES = ['https://www.googleapis.com/auth/classroom.topics',
  'https://www.googleapis.com/auth/classroom.topics.readonly']
    a_creds = service_account.Credentials.from_service_account_file(
    "utils/service.json", scopes=SCOPES)
    creds = a_creds.with_subject(CLASSROOM_ADMIN_EMAIL)
    service = build("classroom", "v1", credentials=creds)
    topics = []
    page_token = None
    while True:
        response = service.courses().topics().list(
        pageToken=page_token,
        courseId=course_id).execute()
        topics = topics.extend(response.get('topic', []))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break
    if response:
        topics = response["topic"] 
        return topics



def create_topics(course_id , topics):
 
    SCOPES = ['https://www.googleapis.com/auth/classroom.topics',
  'https://www.googleapis.com/auth/classroom.topics.readonly']
    a_creds = service_account.Credentials.from_service_account_file(
    "utils/service.json", scopes=SCOPES)
    creds = a_creds.with_subject(CLASSROOM_ADMIN_EMAIL)
    service = build("classroom", "v1", credentials=creds)
    for topic in topics:
        topic_name = topic["name"]
        topic = {
        "name": topic_name}
        response = service.courses().topics().create(
        courseId=course_id,
        body=topic).execute()
    return "success"

def get_coursework(course_id):
    SCOPES = ['https://www.googleapis.com/auth/classroom.coursework.students',
    'https://www.googleapis.com/auth/classroom.coursework.students.readonly']
    a_creds = service_account.Credentials.from_service_account_file(
    "utils/service.json", scopes=SCOPES)
    creds = a_creds.with_subject(CLASSROOM_ADMIN_EMAIL)
    service = build("classroom", "v1", credentials=creds)
    coursework_list = service.courses().courseWork().list(courseId=course_id).execute()
    if coursework_list:
        coursework_list = coursework_list['courseWork']
    return coursework_list

def create_coursework(course_id, coursework_list):
    SCOPES = ['https://www.googleapis.com/auth/classroom.coursework.students',
    'https://www.googleapis.com/auth/classroom.coursework.students.readonly']
    a_creds = service_account.Credentials.from_service_account_file(
    "utils/service.json", scopes=SCOPES)
    creds = a_creds.with_subject(CLASSROOM_ADMIN_EMAIL)
    service = build("classroom", "v1", credentials=creds)
    for coursework_item  in coursework_list:
        # coursework_item['courseId'] = new_course_id
        # coursework_item.pop("id")
        coursework = service.courses().courseWork().create(courseId=course_id, body=coursework_item).execute()
    
def delete_course_by_id(course_id):
    SCOPES = ["https://www.googleapis.com/auth/classroom.courses",
    "https://www.googleapis.com/auth/classroom.courses.readonly"]
    a_creds = service_account.Credentials.from_service_account_file(
    "utils/service.json", scopes=SCOPES)
    creds = a_creds.with_subject(CLASSROOM_ADMIN_EMAIL)
    service = build("classroom", "v1", credentials=creds)
    course = service.courses().delete(id=course_id).execute()
    course_name = course.get("name")
    return course

