# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
User object in the ORM
"""

from fireo.fields import TextField
from common.models import BaseModel
from common.utils.errors import ResourceNotFoundException

class User(BaseModel):
  """
  User ORM class
  """
  auth_id=TextField(required=True)
  email=TextField(required=True)
  role=TextField()

  class Meta:
    ignore_none_field = False
    collection_name = BaseModel.DATABASE_PREFIX + "users"

  @classmethod
  def find_by_email(cls, email):
    """Find a user using email (string)
    Args:
        email (string): User Email
    Returns:
        User: User Object
    """
    user = User.collection.filter("email", "==", email).filter(
        "deleted_at_timestamp", "==", None).get()
    if user is None:
      raise ResourceNotFoundException(f"User with email {email} is not found")
    return user
