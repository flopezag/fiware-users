#!/usr/bin/env python
# -*- encoding: utf-8 -*-
##
# Copyright 2017 FIWARE Foundation, e.V.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
##

import requests
import json
import re
from settings import TENANT_NAME, USERNAME, PASSWORD, REGION


def get_admin_token():
    print("Getting Admin token...")

    payload = {'auth': {'tenantName': TENANT_NAME,
                        'passwordCredentials': {'username': USERNAME, 'password': PASSWORD}
                        }
               }

    url = 'http://cloud.lab.fi-ware.org:4730/v2.0/tokens'
    headers = {'content-type': 'application/json'}

    r = requests.post(url=url, headers=headers, data=json.dumps(payload))

    return r.json()['access']['token']['id']


def get_region_endpoint_group(region, token):
    print("Getting region id for region...")

    url = 'http://cloud.lab.fi-ware.org:4730/v3/OS-EP-FILTER/endpoint_groups'

    headers = {'x-auth-token': token}

    r = requests.get(url=url, headers=headers)

    result = r.json()['endpoint_groups']

    region_id = filter(lambda x: x.get('filters', {}).get('region_id') == region, result)[0]['id']

    return region_id


def get_user_list_per_region(region_id, token):
    print("Getting user list per project per region...")

    url = 'http://cloud.lab.fi-ware.org:4730/v3/OS-EP-FILTER/endpoint_groups/'\
          + region_id + '/projects'

    headers = {'x-auth-token': token}

    r = requests.get(url=url, headers=headers)

    result = r.json()['projects']

    projects = filter(lambda x: x.get('is_cloud_project') == True
                               and x.get('enabled') == True, result)

    project_name = map(lambda x: x['name'], projects)

    users = filter(lambda x: re.match(r'(.*) cloud', x, re.M | re.I), project_name)

    users = map(lambda x: re.match(r'(.*) cloud', x, re.M | re.I).group(1), users)

    return users, projects


def count_users(user_list, token):
    print("Getting users count per type...")

    temporal = map(lambda x: type_user(x, token=token), user_list)

    total_users = len(temporal)
    trial_users = len(filter(lambda x: x == 0, temporal))
    community_users = len(filter(lambda x: x == 1, temporal))

    other_users = filter(lambda x: x != 0 and x != 1, temporal)

    return total_users, trial_users, community_users, other_users


def type_user(user, token):
    """
    Return the user type.
    :param user: the user name
    :param token: the authentication token
    :return: 1 -> Community
             0 -> Trial
            -1 -> Error
    """

    url = 'http://cloud.lab.fi-ware.org:4730/v3/users/' + user

    # print url

    headers = {'x-auth-token': token}

    r = requests.get(url=url, headers=headers)

    try:
        r.json()['user']['community_started_at']
        result = 1
    except:
        try:
            r.json()['user']['trial_started_at']
            result = 0
        except:
            # Some estrange project
            result = user

    return result


def get_list_users_from_project(users, projects, token):
    project_ids = [ x.get('id') for x in projects for y in users
                    if x.get('name') == (y + ' cloud') or x.get('name') == (y + ' Cloud')]

    temporal = map(lambda x: get_list_user_with_some_role(x, token=token), project_ids)

    lista1 = reduce(list.__add__, temporal)

    lista1 = filter(lambda x: x == 1, lista1)

    return len(lista1)


def get_list_user_with_some_role(project_id, token):

    url = 'http://cloud.lab.fi-ware.org:4730/v3/role_assignments?scope.project.id=' + project_id

    headers = {'x-auth-token': token}

    r = requests.get(url=url, headers=headers)

    result = r.json()['role_assignments']

    datos = map(lambda x: x.get('user').get('id'), result)

    # Type 0 -> Basic users
    # Type 1 -> Community
    temporal = map(lambda x: type_user(x, token=token), datos)

    return temporal


if __name__ == "__main__":
    token = get_admin_token()

    region_id = get_region_endpoint_group(region=REGION, token=token)

    user_list, project_list = get_user_list_per_region(region_id=region_id, token=token)

    total_users, trial_users, community_users, other_users = \
        count_users(user_list=user_list, token=token)

    new_community_users = get_list_users_from_project(users=other_users, projects=project_list, token=token)

    community_users += new_community_users
    total_users += new_community_users

    print("\n\n\nTotal users: {}\nTrial users: {}\nCommunity users: {}"
          .format(total_users, trial_users, community_users))
