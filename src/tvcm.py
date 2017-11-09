class User(object):

    def __init__(self, user_edge_length):
        self.user_edge_length = user_edge_length
        self.roaming_epoch_length = 0
        self.local_epoch_length = 0
        self.p_l = 0    # roaming to local
        self.p_r = 0    # local to roaming
        self.pause_time_range = []
        self.speed_range = []


class TimeVariantCommunityModel(object):

    def __init__(self, area_edge_length):
        """
        Init simulation area
        :param area_edge_length:
        """
        self.area_edge_length = area_edge_length
        self.users = []

    def gen_users(self, user_count):
        self.users = [User(10) for _ in range(user_count)]

    def start_simulation(self):
        pass
