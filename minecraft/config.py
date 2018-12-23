from Configuration import Configuration


class AppConfig(Configuration):
    class Keys():
        SERVER = 'server'
        SERVER_ADDRESS = 'address'
        SERVER_PORT = 'port'
        PLAYERS = 'players'

    skel = {
        Keys.PLAYERS: [],
        Keys.SERVER: {
            Keys.SERVER_ADDRESS: '8.8.8.8',
            Keys.SERVER_PORT: 25565
        }
    }


class PlayerConfig(Configuration):
    class Keys():
        USERNAME = 'username'
        PASSWORD = 'password'
        ACCESSTOKEN = 'access_token'
        CLIENTTOKEN = 'client_token'
        ALTTOKEN = 'alt_token'
        PROFILE = 'profile'

    filename = 'profile.json'
    skel = {
        Keys.USERNAME: '',
        Keys.PASSWORD: '',
        Keys.ACCESSTOKEN: '',
        Keys.CLIENTTOKEN: '',
        Keys.ALTTOKEN: '',
        Keys.PROFILE: {}
    }
