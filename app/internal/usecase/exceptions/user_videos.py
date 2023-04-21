class UserVideoError(Exception):
    pass


class UserVideoAlreadyLikedError(UserVideoError):
    pass


class UserVideoNotLikedError(UserVideoError):
    pass
