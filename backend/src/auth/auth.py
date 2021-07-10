import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'kahve.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'http://localhost:5000'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''


def get_token_auth_header():
    auth_header = request.headers['Authorization']
    # auth_header = 'eyRTdGUmNjNlBnNXBNalNLMSJ9.eyJpc3MiOiJodHRwczovL2thaHZlLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MGE0NzJiZmEwYjBiYjAwNmFkYTI4MGQiLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0OjUwMDAiLCJpYXQiOjE2MjE0NTQ5ODYsImV4cCI6MTYyMTQ2MjE4NiwiYXpwIjoiWUtnaldvZ1lQaExnZll2dGprMFpKbnBCMDZSTjYwdTIiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDpkcmlua3MtZGV0YWlsIl19.E44L8QIW_Yqk82d5tr5t2hXzaPhJ97nTbqdr4lsAq3kpXxSNtuxgq9nzcFslyQQAFJ9lu0UzbwDj6fdk5NMhtQ3OhcG5F0RWfFf5021jY2hfmuFhlGOMPkj1T2sFVv4bzYt1d-vhNz3jElMx49iz4hWuQS1Q3sKQ042fsWnjNpaUHOfBuDA2apYgEvHRIDtX48gQE5i5P62riagiZQPs6p2h4sLWcHXCn1HpdTdbeHWR8loRJMWqqRQV4fOeNZsTqzUJhqwzsX9mVUC19fiiUK8eBKW3nr8b4vyH9vUPyo2PP6SN-fY9ofA2D0hNCQgW5iMHPh88RC55PqPWF7USQw'
    # auth_header = request.headers.get("Authorization", None)
    # print(auth_header)

    if not auth_header:
        print('not auth')
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth_header.split(' ')
    if parts[0].lower() != 'bearer':
        print('no bearer')
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        print('len=1')
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        print('len>2')
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token
    # return auth_header

    # raise Exception('Not Implemented')


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
    return True


# def check_permissions(permission, payload):
#     raise Exception('Not Implemented')


'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        print('kid not in')
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)

# def verify_decode_jwt(token):
#     raise Exception('Not Implemented')


'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            print(token)
            try:
                payload = verify_decode_jwt(token)
            except:
                print('except')
                abort(401)
            check_permissions(permission, payload)

            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator

