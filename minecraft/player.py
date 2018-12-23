from minecraft import authentication
from minecraft.authentication import Profile
from minecraft.exceptions import YggdrasilError
from minecraft.config import PlayerConfig


class Player:
    username = ''
    password = ''
    access_token = ''
    client_token = ''
    profile = None

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login(self, client_token='') -> authentication.AuthenticationToken:
        auth_token = authentication.AuthenticationToken()
        auth_token.client_token = client_token
        return self._authenticate_token(auth_token)

    def _authenticate_token(self, auth_token: authentication.AuthenticationToken) -> authentication.AuthenticationToken:
        try:
            if not self.access_token == '' and not self.client_token == '':
                print("Refreshing session")
                auth_token.username = self.username
                auth_token.access_token = self.access_token or ''
                auth_token.client_token = self.client_token or ''
                auth_token.profile = Profile(*self.profile)
                auth_token.refresh()
            else:
                print("Authenticating for new session")
                auth_token.authenticate(self.username, self.password)
        except YggdrasilError as err:
            print(err)
            return None
        self.access_token = auth_token.access_token
        self.client_token = auth_token.client_token
        self.profile = auth_token.profile.to_dict()
        return auth_token

    def serialize(self) -> dict:
        return {
            PlayerConfig.Keys.USERNAME: self.username,
            PlayerConfig.Keys.PASSWORD: self.password,
            PlayerConfig.Keys.ACCESSTOKEN: self.access_token,
            PlayerConfig.Keys.CLIENTTOKEN: self.client_token,
            PlayerConfig.Keys.PROFILE: self.profile
        }

    @staticmethod
    def deserialize(data: dict):
        """
        Create a Player object with the data provided in the dictionary.
        :param data: The data to deserialize from
        :return: Player object with the filled in data
        :rtype: Player
        """
        player = Player(data[PlayerConfig.Keys.USERNAME], data[PlayerConfig.Keys.PASSWORD])
        player.access_token = data[PlayerConfig.Keys.ACCESSTOKEN]
        player.client_token = data[PlayerConfig.Keys.CLIENTTOKEN]
        player.profile = data[PlayerConfig.Keys.PROFILE]
        return player


class McLeaksPlayer(Player):
    alt_token = ''
    server = ''

    def __init__(self, alt_token):
        super().__init__(alt_token, alt_token)
        self.alt_token = alt_token

    def login(self, client_token='') -> authentication.MCLeaksAuthenticationToken:
        auth_token = authentication.MCLeaksAuthenticationToken(server=self.server)
        auth_token.client_token = client_token
        self.username = self.alt_token
        self.password = self.alt_token
        auth_token.server = self.server
        auth_token.check_token_status(self.alt_token)
        return self._authenticate_token(auth_token)

    def set_server(self, server: str):
        self.server = server

    def serialize(self) -> dict:
        return {
            PlayerConfig.Keys.USERNAME: self.username,
            PlayerConfig.Keys.PASSWORD: self.password,
            PlayerConfig.Keys.ACCESSTOKEN: self.access_token,
            PlayerConfig.Keys.CLIENTTOKEN: self.client_token,
            PlayerConfig.Keys.ALTTOKEN: self.alt_token,
            PlayerConfig.Keys.PROFILE: self.profile
        }

    @staticmethod
    def deserialize(data: dict):
        """
        Create a Player object with the data provided in the dictionary.
        :param data: The data to deserialize from
        :return: Player object with the filled in data
        :rtype: McLeaksPlayer
        """
        player = McLeaksPlayer(data[PlayerConfig.Keys.ALTTOKEN])
        player.username = data[PlayerConfig.Keys.USERNAME]
        player.access_token = data[PlayerConfig.Keys.ACCESSTOKEN]
        player.client_token = data[PlayerConfig.Keys.CLIENTTOKEN]
        player.profile = data[PlayerConfig.Keys.PROFILE]
        player.alt_token = data[PlayerConfig.Keys.ALTTOKEN]
        return player
