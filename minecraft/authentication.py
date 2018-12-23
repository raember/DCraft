import requests
import json
import re
import datetime
from .exceptions import YggdrasilError

#: The base url for Ygdrassil requests
AUTH_SERVER = "https://authserver.mojang.com"
SESSION_SERVER = "https://sessionserver.mojang.com/session/minecraft"
# Need this content type, or authserver will complain
CONTENT_TYPE = "application/json"
HEADERS = {"content-type": CONTENT_TYPE}


class Profile(object):
    """
    Container class for a MineCraft Selected profile.
    See: `<http://wiki.vg/Authentication>`_
    """

    def __init__(self, id_=None, name=None):
        self.id_ = id_
        self.name = name

    def to_dict(self):
        """
        Returns ``self`` in dictionary-form, which can be serialized by json.
        """
        if self:
            return {"id": self.id_,
                    "name": self.name}
        else:
            raise AttributeError("Profile is not yet populated.")

    def __bool__(self):
        bool_state = self.id_ is not None and self.name is not None
        return bool_state

    # Python 2 support
    def __nonzero__(self):
        return self.__bool__()


class AuthenticationToken(object):
    """
    Represents an authentication token.

    See http://wiki.vg/Authentication.
    """
    AGENT_NAME = "Minecraft"
    AGENT_VERSION = 1

    def __init__(self, username=None, access_token=None, client_token=None):
        """
        Constructs an `AuthenticationToken` based on `access_token` and
        `client_token`.

        Parameters:
            access_token - An `str` object containing the `access_token`.
            client_token - An `str` object containing the `client_token`.

        Returns:
            A `AuthenticationToken` with `access_token` and `client_token` set.
        """
        self.username = username
        self.access_token = access_token
        self.client_token = client_token
        self.profile = Profile()

    @property
    def authenticated(self):
        """
        Attribute which is ``True`` when the token is authenticated and
        ``False`` when it isn't.
        """
        if not self.username:
            return False

        if not self.access_token:
            return False

        if not self.client_token:
            return False

        if not self.profile:
            return False

        return True

    def authenticate(self, username, password):
        """
        Authenticates the user against https://authserver.mojang.com using
        `username` and `password` parameters.

        Parameters:
            username - An `str` object with the username (unmigrated accounts)
                or email address for a Mojang account.
            password - An `str` object with the password.

        Returns:
            Returns `True` if successful.
            Otherwise it will raise an exception.

        Raises:
            minecraft.exceptions.YggdrasilError
        """
        payload = {
            "agent": {
                "name": self.AGENT_NAME,
                "version": self.AGENT_VERSION
            },
            "username": username,
            "password": password
        }

        res = _make_request(AUTH_SERVER, "authenticate", payload)

        _raise_from_response(res)

        json_resp = res.json()

        self.username = username
        self.access_token = json_resp["accessToken"]
        self.client_token = json_resp["clientToken"]
        self.profile.id_ = json_resp["selectedProfile"]["id"]
        self.profile.name = json_resp["selectedProfile"]["name"]

        return True

    def refresh(self):
        """
        Refreshes the `AuthenticationToken`. Used to keep a user logged in
        between sessions and is preferred over storing a user's password in a
        file.

        Returns:
            Returns `True` if `AuthenticationToken` was successfully refreshed.
            Otherwise it raises an exception.

        Raises:
            minecraft.exceptions.YggdrasilError
            ValueError - if `AuthenticationToken.access_token` or
                `AuthenticationToken.client_token` isn't set.
        """
        if self.access_token is None:
            raise ValueError("'access_token' not set!'")

        if self.client_token is None:
            raise ValueError("'client_token' is not set!")

        res = _make_request(AUTH_SERVER,
                            "refresh", {"accessToken": self.access_token,
                                        "clientToken": self.client_token})

        _raise_from_response(res)

        json_resp = res.json()

        self.access_token = json_resp["accessToken"]
        self.client_token = json_resp["clientToken"]
        self.profile.id_ = json_resp["selectedProfile"]["id"]
        self.profile.name = json_resp["selectedProfile"]["name"]

        return True

    def validate(self):
        """
        Validates the AuthenticationToken.

        `AuthenticationToken.access_token` must be set!

        Returns:
            Returns `True` if `AuthenticationToken` is valid.
            Otherwise it will raise an exception.

        Raises:
            minecraft.exceptions.YggdrasilError
            ValueError - if `AuthenticationToken.access_token` is not set.
        """
        if self.access_token is None:
            raise ValueError("'access_token' not set!")

        res = _make_request(AUTH_SERVER, "validate",
                            {"accessToken": self.access_token})

        # Validate returns 204 to indicate success
        # http://wiki.vg/Authentication#Response_3
        if res.status_code == 204:
            return True

    @staticmethod
    def sign_out(username, password):
        """
        Invalidates `access_token`s using an account's
        `username` and `password`.

        Parameters:
            username - ``str`` containing the username
            password - ``str`` containing the password

        Returns:
            Returns `True` if sign out was successful.
            Otherwise it will raise an exception.

        Raises:
            minecraft.exceptions.YggdrasilError
        """
        res = _make_request(AUTH_SERVER, "signout",
                            {"username": username, "password": password})

        if _raise_from_response(res) is None:
            return True

    def invalidate(self):
        """
        Invalidates `access_token`s using the token pair stored in
        the `AuthenticationToken`.

        Returns:
            ``True`` if tokens were successfully invalidated.

        Raises:
            :class:`minecraft.exceptions.YggdrasilError`
        """
        res = _make_request(AUTH_SERVER, "invalidate",
                            {"accessToken": self.access_token,
                             "clientToken": self.client_token})

        if res.status_code != 204:
            _raise_from_response(res)
        return True

    def join(self, server_id):
        """
        Informs the Mojang session-server that we're joining the
        MineCraft server with id ``server_id``.

        Parameters:
            server_id - ``str`` with the server id

        Returns:
            ``True`` if no errors occured

        Raises:
            :class:`minecraft.exceptions.YggdrasilError`

        """
        if not self.authenticated:
            err = "AuthenticationToken hasn't been authenticated yet!"
            raise YggdrasilError(err)

        res = _make_request(SESSION_SERVER, "join",
                            {"accessToken": self.access_token,
                             "selectedProfile": self.profile.to_dict(),
                             "serverId": server_id})

        if res.status_code != 204:
            _raise_from_response(res)
        return True


def _make_request(server, endpoint, data):
    """
    Fires a POST with json-packed data to the given endpoint and returns
    response.

    Parameters:
        endpoint - An `str` object with the endpoint, e.g. "authenticate"
        data - A `dict` containing the payload data.

    Returns:
        A `requests.Request` object.
    """
    res = requests.post(server + "/" + endpoint, data=json.dumps(data),
                        headers=HEADERS)
    return res


def _raise_from_response(res):
    """
    Raises an appropriate `YggdrasilError` based on the `status_code` and
    `json` of a `requests.Request` object.
    """
    if res.status_code == requests.codes['ok']:
        return None

    exception = YggdrasilError()
    exception.status_code = res.status_code

    try:
        json_resp = res.json()
        if not ("error" in json_resp and "errorMessage" in json_resp):
            raise ValueError
    except ValueError:
        message = "[{status_code}] Malformed error message: '{response_text}'"
        message = message.format(status_code=str(res.status_code),
                                 response_text=res.text)
        exception.args = (message,)
    else:
        message = "[{status_code}] {error}: '{error_message}'"
        message = message.format(status_code=str(res.status_code),
                                 error=json_resp["error"],
                                 error_message=json_resp["errorMessage"])
        exception.args = (message,)
        exception.yggdrasil_error = json_resp["error"]
        exception.yggdrasil_message = json_resp["errorMessage"]
        exception.yggdrasil_cause = json_resp.get("cause")

    raise exception


MCLEAKS_AUTH_SERVER = 'https://auth.mcleaks.net/v1'
MCLEAKS_SESSION_SERVER = 'https://auth.mcleaks.net/v1'


class MCLeaksAuthenticationToken(AuthenticationToken):
    session = ''
    server = ''

    def __init__(self, username=None, access_token=None, client_token=None, server=None):
        """
        Constructs an `AuthenticationToken` based on `access_token` and
        `client_token`.

        Parameters:
            access_token - An `str` object containing the `access_token`.
            client_token - An `str` object containing the `client_token`.

        Returns:
            A `AuthenticationToken` with `access_token` and `client_token` set.
        """
        super().__init__(username, access_token, client_token)
        self.server = server

    @property
    def authenticated(self):
        """
        Attribute which is ``True`` when the token is authenticated and
        ``False`` when it isn't.
        """
        if not self.username:
            return False

        if not self.profile:
            return False

        return True

    def authenticate(self, token, _):
        """
        Authenticates the user against https://auth.mcleaks.net/v1 using
        the `token` parameter.

        :param token: The alt-token received from mcleaks.
        :type token: str
        :return: Returns `True` if successful. Otherwise it will raise an exception.
        :rtype: bool
        :raise YggdrasilError:
        """
        if re.compile(r"^[a-zA-Z0-9]{16}$").match(token) is None:
            raise YggdrasilError("Token doesn't seem to be a typical MCLeaks token.")
        payload = {
            "token": token
        }

        res = _make_request(MCLEAKS_AUTH_SERVER, "redeem", payload)

        _raise_from_response(res)

        json_resp = res.json()

        # print(json_resp)
        if not json_resp['success']:
            # ALT-TOKEN has expired or is not valid!
            raise YggdrasilError(json_resp['errorMessage'])
        self.username = json_resp['result']['mcname']
        self.session = json_resp['result']['session']
        self.profile.id_ = ""
        self.profile.name = json_resp['result']['mcname']
        return True

    def join(self, server_id):
        """
        Informs the Mojang session-server that we're joining the MineCraft server with id `server_id`.

        :param server_id: Server hash
        :type server_id: str
        :return: `True` if no errors occured
        :rtype: bool
        :raise YggdrasilError:
        """
        if not self.authenticated:
            err = "AuthenticationToken hasn't been authenticated yet!"
            raise YggdrasilError(err)

        payload = {
            "session": self.session,
            "mcname": self.username,
            "serverhash": server_id,
            "server": self.server
        }
        res = _make_request(MCLEAKS_SESSION_SERVER, "joinserver", payload)

        if res.status_code != 204:
            _raise_from_response(res)
        print(res.json())
        return True

    def check_token_status(self, token):
        """
        Checks the alt token status
        :param token: Alt token from MCLeaks
        :type token: str
        :return:
        """
        MCLEAKS_TOKEN_STATUS = "https://mcleaks.net/tokenstatusajax"
        res = requests.get("{}?t={}".format(MCLEAKS_TOKEN_STATUS, token), headers=HEADERS)
        jsn = res.json()
        if jsn['status'] == 'redeemed':
            print("Token has already been redeemed.")
        elif jsn['status'] == 'valid':
            print("Token is still valid.")
            rem = jsn['remaining']
            if rem.endswith('minutes') or rem.endswith('minute'):
                minutes = re.compile(r"^\d+").match(rem).group(0)
                timespn = datetime.timedelta(minutes=int(minutes))
            elif rem.endswith('seconds') or rem.endswith('second'):
                seconds = re.compile(r"^\d+").match(rem).group(0)
                timespn = datetime.timedelta(seconds=int(seconds))
            else:
                print(jsn)
                raise Exception("Unhandled remaining time.")
            print("{} left.".format(timespn))
        elif jsn['status'] == 'invalid':
            print("Token is invalid.")
            return False
        else:
            print(jsn)
            raise Exception("Unhandled response status.")
