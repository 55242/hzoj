#-*- coding: utf-8 -*-

from OJ.models import User, Problem
from urllib.parse import urlencode
import time, re

'''controller包含了许多工具函数'''

# 一些网页工具
class Tools(object):
    # Tools 类 包含了一些工具函数
    @staticmethod
    def pretty_time(t):
        # 时间
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))

    @staticmethod
    def to_str(s):
        # 将s转化为str类型
        return str(s)

    @staticmethod
    def url_encode(query, doseq=0):
        # 返回询问的url
        return urlencode(query, doseq)

    @staticmethod
    def get_cur_user():
        # 得到当前用户
        return User.get_cur_user()


class Checker(object):
    # Checker 类 包含了一些检查的函数
    @staticmethod
    def is_valid_username(username):
        # 判断用户名是否合法
        if not username:
            return False

        if len(username) < 3 or len(username) > 16:
            return False

        checker = re.compile("[A-Za-z0-9_]")
        if not checker.match(username):
            return False

        return True

    @staticmethod
    def is_valid_email(email):
        # 判断邮箱是否合法
        if not email:
            return False

        if len(email) < 3 or len(email) > 50:
            return False

        checker = re.compile("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$")
        if not checker.match(email):
            return False

        return True

    @staticmethod
    def is_valid_password(password):
        # 判断密码是否合法
        if not password:
            return None

        # Because of the salt is "syzoj2_xxx" and the "syzoj2_xxx" 's md5 is"59cb..."
        # the empty password 's md5 will equal "59cb.."
        syzoj2_xxx_md5 = "59cb65ba6f9ad18de0dcd12d5ae11bd2"
        if password == syzoj2_xxx_md5:
            return False

        return True


class Paginate():
    # Paginate 类 包含了一些用于分页的函数
    query = None
    total_page = 0
    per_page = 10
    cur_page = 1
    edge_display_num = 10
    make_url = None
    other = None

    def __init__(self, query, make_url=None, other=None, cur_page=1, per_page=10, edge_display_num=2):
        if not cur_page:
            cur_page = 1
        self.cur_page = int(cur_page)
        self.per_page = per_page
        self.edge_display_num = edge_display_num
        self.query = query
        self.make_url = make_url
        self.other = other
        total = query.count()
        self.total_page = total / per_page
        if total % per_page:
            self.total_page += 1

    def have_pre(self, cur_page=None):
        # 是否存在前一页
        if not cur_page:
            cur_page = self.cur_page
        return cur_page > 1

    def have_next(self, cur_page=None):
        # 是否存在后一页
        if not cur_page:
            cur_page = self.cur_page
        return cur_page < self.total_page

    def need_omit_left(self):
        # 分页条左半部分是否需要省略号
        return self.cur_page - self.edge_display_num > 1

    def need_omit_right(self):
        # 分页条右半部分是否需要省略号
        return self.cur_page + self.edge_display_num < self.total_page

    def range(self):
        # 分页条中间部分起始页数（包含当前页码）
        start = self.cur_page - self.edge_display_num
        stop = self.cur_page + self.edge_display_num + 1
        if start < 1:
            start = int(1)
        if stop > self.total_page + 1:
            stop = int(self.total_page + 1)
        # start跟stop不用int()就变成了float，不是很懂QAQ ？？
        return range(start, stop)

    def get(self):
        # 返回这一页要显示的所有条目
        return self.query.offset((self.cur_page - 1) * self.per_page).limit(self.per_page)

    def get_html(self):
        # 得到页码对应的url，最终返回整个分页条的html 感觉不太酸爽？？
        pre_disable = ""
        next_disable = ""
        left_omit = ""
        right_omit = ""
        pre_url = ""
        next_url = ""
        pid_list = ""

        if self.have_pre():
            pre_url = self.make_url(self.cur_page - 1, self.other)
        else:
            pre_disable = "am-disabled"
        if self.have_next():
            next_url = self.make_url(self.cur_page + 1, self.other)
        else:
            next_disable = "am-disabled"

        if self.need_omit_left():
            left_omit = '''<li><span>...</span></li>'''
        if self.need_omit_right():
            right_omit = '''<li><span>...</span></li>'''

        for pid in self.range():
            active = ""
            if pid == self.cur_page:
                active = "am-active"
            pid_list += '''<li class="''' + active + '''"><a href="''' + \
                        self.make_url(pid, self.other) + '''">''' + str(pid) + '''</a></li>'''

        html = '''<div class="am-u-sm-12">
        <ul class="am-pagination am-pagination-centered">
            <li class="''' + pre_disable + '''">
                <a href="''' + pre_url + '''"><span class="am-icon-angle-double-left"></span></a>
            </li>
            ''' + left_omit + pid_list + right_omit + '''
            <li class="''' + next_disable + '''">
                <a href="''' + next_url + '''"><span class="am-icon-angle-double-right"></span></a>
            </li>
        </ul>
    </div>'''
        return html


def register(username, password, email):
    # 注册一个新用户，返回状态码 2002不合法用户名 2007不合法密码 2006不合法邮箱 2008用户名存在 1合法并成功注册
    state_code = 0
    if not Checker.is_valid_username(username):
        state_code = 2002
    elif not Checker.is_valid_password(password):
        state_code = 2007
    elif not Checker.is_valid_password(email):
        state_code = 2006
    elif User.query.filter_by(username=username).first():
        state_code = 2008
    else:
        state_code = 1
        user = User(username=username, password=password, email=email)
        user.save()
    return state_code


def create_problem(user, title):
    # 创建一个问题并保存，返回pid
    problem = Problem(user=user, title=title)
    problem.save()
    print(problem)
    return problem.id


def become_admin(user):
    # 使user成为一个admin
    user.is_admin = True
    user.save()


def cancel_admin(user):
    # 取消user的admin
    user.is_admin = False
    user.save()
