import math
import random
from scipy import stats


X_MAX = 1000
Y_MAX = 1000
COMM_SIZE = 100
SPEED_RANGE = [5, 15]
LOCAL_TO_ROAM = 0.2
ROAM_TO_LOCAL = 0.5
CON_LOCAL_TO_ROAM = 0.2
CON_ROAM_TO_LOCAL = 0.8
PAUSE_AVG_NORMAL = 100
PAUSE_AVG_CON = 50

TIME_STEP = 1
AVG_LENGTH_ROAM = 520
AVG_LENGTH_LOCAL = 80

CON_PERIOD = 2880    # concentration period time
NORMAL_PERIOD = 5760     # normal period time

LOCAL = 0
ROAMING = 1

NORMAL = 0
CONCENTRATION = 1


def get_distance(x_1, y_1, x_2, y_2):
    return math.sqrt((x_1 - x_2) * (x_1 - x_2) + (y_1 - y_2) * (y_1 - y_2))


class User(object):

    def __init__(self, user_name):
        self.file_name = './data/' + user_name + '.csv'
        self.logs = []

    def log(self):
        with open(self.file_name, 'w+') as f_in:
            for content in self.logs:
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
        timestamp = 0
        epoch = LOCAL  # 0: local, 1: roaming
        period = NORMAL  # 0: normal, 1: concentration
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
        local_length = stats.expon.rvs(scale=AVG_LENGTH_LOCAL, size=100000)
        roaming_length = stats.expon.rvs(scale=AVG_LENGTH_ROAM, size=100000)
        normal_pause_time = stats.expon.rvs(scale=PAUSE_AVG_NORMAL, size=100000)
        con_pause_time = stats.expon.rvs(scale=PAUSE_AVG_CON, size=100000)

        for _ in range(1000):
            # each round is an epoch
            reach = False
            # initial start position
            if epoch == LOCAL:
                if period == NORMAL:
                    curr_x = random.random() * (comm_x_normal[1] - comm_x_normal[0]) + comm_x_normal[0]
                    curr_y = random.random() * (comm_y_normal[1] - comm_y_normal[0]) + comm_y_normal[0]
                else:
                    curr_x = random.random() * (comm_x_con[1] - comm_x_con[0]) + comm_x_con[0]
                    curr_y = random.random() * (comm_y_con[1] - comm_y_con[0]) + comm_y_con[0]
            else:
                # roaming epoch
                curr_x = random.random() * X_MAX
                curr_y = random.random() * Y_MAX

            direction = random.random() * 2 * math.pi
            v = (SPEED_RANGE[1] - SPEED_RANGE[0]) * random.random() + SPEED_RANGE[0]
            v_x = v * math.cos(direction)
            v_y = v * math.sin(direction)
            d_inc = v * TIME_STEP
            x_inc = v_x * TIME_STEP
            y_inc = v_y * TIME_STEP
            # get move length
            length = local_length[random.randint(0, len(local_length) - 1)] if epoch == LOCAL else \
                roaming_length[random.randint(0, len(roaming_length) - 1)]
            # every epoch
            while not reach:
                period_time += TIME_STEP
                timestamp += TIME_STEP
                curr_x = curr_x + x_inc
                curr_y = curr_y + y_inc
                if epoch == LOCAL:
                    if period == NORMAL:
                        curr_x, curr_y = self.fix_point(curr_x, curr_y, comm_x_normal, comm_y_normal)
                    else:
                        curr_x, curr_y = self.fix_point(curr_x, curr_y, comm_x_con, comm_y_con)
                else:
                    curr_x, curr_y = self.fix_point(curr_x, curr_y, [0, X_MAX], [0, Y_MAX])
                self.logs.append('{:.0f}\t{:.6f}\t{:.6f}'.format(timestamp, curr_x, curr_y))
                length -= d_inc
                if length < 0:
                    reach = True
            # stay or start a new epoch, gen next epoch
            # get pause time after an epoch ends
            pause_time = normal_pause_time[random.randint(0, len(normal_pause_time) - 1)] if period == NORMAL else \
                con_pause_time[random.randint(0, len(con_pause_time) - 1)]
            timestamp += pause_time
            self.logs.append('{:.0f}\t{:.6f}\t{:.6f}'.format(timestamp, curr_x, curr_y))
            if period == NORMAL:
                if epoch == LOCAL:
                    if random.random() > LOCAL_TO_ROAM:
                        epoch = ROAMING
                else:
                    if random.random() > ROAM_TO_LOCAL:
                        epoch = LOCAL
            else:
                if epoch == LOCAL:
                    if random.random() > CON_LOCAL_TO_ROAM:
                        epoch = ROAMING
                else:
                    if random.random() > CON_ROAM_TO_LOCAL:
                        epoch = LOCAL

            # if or not start a new period
            if period == NORMAL and period_time > NORMAL_PERIOD:
                period = CONCENTRATION
            elif period == CONCENTRATION and period_time > CON_PERIOD:
                period = NORMAL
        self.log()


class TimeVariantCommunityModel(object):

    def __init__(self, user_count):
        """
        Init simulation area
        """
        self.users = []
        self.users = [User(str(_)) for _ in range(user_count)]

    def start_simulation(self):
        for u in self.users:
            u.simulate()
