import math
import random
from scipy import stats


X_MAX = 1000
Y_MAX = 1000
COMM_SIZE = 100
PAUSE_RANGE = []
SPEED_RANGE = [5, 15]
LOCAL_TO_ROAM = 0.2
ROAM_TO_LOCAL = 0.5
CON_LOCAL_TO_ROAM = 0.2
CON_ROAM_TO_LOCAL = 0.8
PAUSE_AVG = 10
CON_PERIOD = 100    # concentration period time
NORMAL_PERIOD = 100 # normal period time
TIME_STEP = 10
AVG_LENGTH_ROAM = 520
AVG_LENGTH_LOCAL = 80


def get_distance(x_1, y_1, x_2, y_2):
    return math.sqrt((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2)


class User(object):

    def __init__(self, user_name, user_edge_length):
        self.user_edge_length = user_edge_length
        self.roaming_epoch_length = 0
        self.local_epoch_length = 0
        self.p_l_n = 0    # roaming to local
        self.p_l_c = 0    # roaming to local
        self.p_r_n = 0    # local to roaming, which is bigger in concentrate movement period
        self.p_r_c = 0    # local to roaming, which is bigger in concentrate movement period
        self.pause_time_range = []
        self.speed_range = []
        self.total_time = 0
        self.cmp = 0    # concentrate movement period
        self.nmp = 0    # normal movement period
        self.file_name = user_name + '.csv'

    def log(self, content):
        with open(self.file_name, 'a+') as f_in:
            f_in.write(content + '\n')

    def fix_point(self, x, y, x_range, y_range):  # LOCAL or ROAM
        x_length = x_range[1] - x_range[0]
        y_length = y_range[1] - y_range[0]
        if x < x_range[0]:
            x += x_length
        elif x > x_range[1]:
            x -= x_length
        if y < y_range[0]:
            y += y_length
        elif y > y_range[1]:
            y -= y_length
        return x, y

    def simulate(self):
        """
        start from a roaming epoch，concentrate movement period
        :return:
        """
        start_time = 0
        curr_x = random.random() * X_MAX
        curr_y = random.random() * Y_MAX
        status = 0  # 0: local, 1: roaming
        period = 0  # 0: normal, 1: concentration
        # normal movement period
        comm_x_normal = [random.random() * (X_MAX - COMM_SIZE), 0]
        comm_x_normal[1] = comm_x_normal[0] + COMM_SIZE
        comm_y_normal = [random.random() * (X_MAX - COMM_SIZE), 0]
        comm_y_normal[1] = comm_y_normal[0] + COMM_SIZE
        # concentrate movement period
        comm_x_con = [random.random() * (X_MAX - COMM_SIZE), 0]
        comm_x_con[1] = comm_x_con[0] + COMM_SIZE
        comm_y_con = [random.random() * (X_MAX - COMM_SIZE), 0]
        comm_y_con[1] = comm_y_con[0] + COMM_SIZE

        period_time = 0

        reach = False
        for _ in range(1000):
            direction = random.random() * 2 * math.pi
            v = (SPEED_RANGE[1] - SPEED_RANGE[0]) * random.random() + SPEED_RANGE[0]
            v_x = v * math.cos(direction)
            v_y = v * math.sin(direction)
            length = stats.expon.rvs(scale=AVG_LENGTH_LOCAL, size=1)[0]
            target_x = curr_x + length * math.cos(direction)
            target_y = curr_y + length * math.sin(direction)
            if status == 0:
                if period == 0:
                    target_x, target_y = self.fix_point(target_x, target_y, comm_x_normal, comm_y_normal)
                else:
                    target_x, target_y = self.fix_point(target_x, target_y, comm_x_con, comm_y_con)
            else:
                target_x, target_y = self.fix_point(target_x, target_y, [0, X_MAX], [0, Y_MAX])
            # every epoch
            while not reach:
                period_time += TIME_STEP
                start_time += TIME_STEP
                x_inc = v_x * TIME_STEP
                y_inc = v_y * TIME_STEP
                curr_x += curr_x + x_inc
                curr_y += curr_y + y_inc
                if status == 0:
                    if period == 0:
                        curr_x, curr_y = self.fix_point(curr_x, curr_y, comm_x_normal, comm_y_normal)
                    else:
                        curr_x, curr_y = self.fix_point(curr_x, curr_y, comm_x_con, comm_y_con)
                else:
                    curr_x, curr_y = self.fix_point(curr_x, curr_y, [0, X_MAX], [0, Y_MAX])
                if get_distance(curr_x, curr_y, target_x, target_y) < 5:
                    reach = True
            # stay or start a new epoch
            if status == 0:
                pass
            else:
                pass

            # if or not start a new period
            if period == 0 and period_time > NORMAL_PERIOD:
                period = 1
            elif period == 1 and period_time > CON_PERIOD:
                period = 0


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
