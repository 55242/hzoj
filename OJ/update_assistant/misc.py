from OJ.models import JudgeState
from OJ import db

db.create_all()

all_judge = JudgeState.query.all()
for item in all_judge:
    item.update_userac_info()
