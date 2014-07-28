#!/usr/bin/env python
from managementAPI.sc_management_api import get_auth_token, sc_request

if __name__ == '__main__':

    get_auth_token()
    result = sc_request(
        resource="securityGroup/4bb45a00-547e-4a03-b6c8-a8ad21f76d05")

    f = open("c:\\test-return.xml", "w")
    f.write(result)
