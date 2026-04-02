class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def get_demo_credentials(self):
        return self.user_repository.list_demo_credentials()
