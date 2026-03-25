import sqlite3
import random
import asyncio
import uvicorn
from datetime import date, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


# ==========================================
# 1. 数据库初始化与依赖注入
# ==========================================
def init_db():
    conn = sqlite3.connect('campus_wifi.db')
    c = conn.cursor()

    # 核心用户表：包含所有经济与信誉所需字段
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (
                     student_id
                     TEXT
                     PRIMARY
                     KEY,
                     password
                     TEXT,
                     name
                     TEXT,
                     score
                     INTEGER,
                     reputation
                     INTEGER,
                     role
                     TEXT,
                     last_sign_date
                     TEXT,
                     sign_days
                     INTEGER,
                     shared_gb
                     INTEGER,
                     consumed_gb
                     INTEGER
                 )''')

    # WiFi节点表
    c.execute('''CREATE TABLE IF NOT EXISTS wifi_nodes
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     owner_id
                     TEXT,
                     name
                     TEXT,
                     speed
                     TEXT,
                     reserved
                     TEXT,
                     cost
                     INTEGER
                 )''')

    # 商城表
    c.execute('''CREATE TABLE IF NOT EXISTS store_items
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     name
                     TEXT,
                     cost
                     INTEGER,
                     desc
                     TEXT
                 )''')

    # 插入超级管理员 (带有初始大流量，用于展示排行榜)
    c.execute('INSERT OR IGNORE INTO users VALUES ("root", "root123", "Super Admin", 9999, 100, "root", "", 0, 500, 10)')

    # 初始化默认商品
    c.execute('SELECT count(*) FROM store_items')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO store_items (name, cost, desc) VALUES ("Milktea(One Cup)", 10, "Mixue Icecream&Tea")')
        c.execute('INSERT INTO store_items (name, cost, desc) VALUES ("Printing Voucher(50 Pages)", 20, "Library Free Printing")')

    conn.commit()
    conn.close()


init_db()


def get_db():
    conn = sqlite3.connect('campus_wifi.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ==========================================
# 2. 多智能体演化引擎 (满血完整版)
# ==========================================
class StudentAgent:
    def __init__(self, strategy):
        self.strategy = strategy
        self.score = random.randint(20, 80)
        self.reputation = random.randint(40, 95)


class EvolutionEngine:
    def __init__(self):
        self.is_running = False
        self.agents = []
        self.tick_count = 0
        self.reset_population()

    def reset_population(self):
        """清空并重置种群比例"""
        self.tick_count = 0
        self.agents = [StudentAgent('coop') for _ in range(14)] + \
                      [StudentAgent('defect') for _ in range(8)] + \
                      [StudentAgent('recip') for _ in range(8)]

    def add_random_student(self):
        """随机增加一名新生"""
        self.agents.append(StudentAgent(random.choice(['coop', 'defect', 'recip'])))

    def evolve_step(self):
        if not self.agents: return
        self.tick_count += 1

        coop_count = sum(1 for a in self.agents if a.strategy == 'coop')
        defect_count = sum(1 for a in self.agents if a.strategy == 'defect')

        for a in self.agents:
            # 1. 更新信誉
            if a.strategy == 'coop':
                a.reputation = min(100, a.reputation + random.randint(0, 2))
            elif a.strategy == 'defect':
                a.reputation = max(0, a.reputation - random.randint(1, 4))

            # 2. 复制者动态 (策略模仿)
            if random.random() < 0.12:  # 12%的概率发生策略动摇
                if a.strategy == 'coop' and defect_count > coop_count * 1.2:
                    a.strategy = 'defect'
                elif a.strategy == 'defect' and a.reputation < 30:
                    a.strategy = 'coop'
                elif a.strategy == 'recip' and defect_count > len(self.agents) * 0.5:
                    a.strategy = 'defect'

    def get_stats(self):
        """获取大屏所需的各项指标"""
        coop = sum(1 for a in self.agents if a.strategy == 'coop')
        defect = sum(1 for a in self.agents if a.strategy == 'defect')
        recip = sum(1 for a in self.agents if a.strategy == 'recip')
        total = len(self.agents)
        avg_rep = int(sum(a.reputation for a in self.agents) / total) if total else 0

        rep_low = sum(1 for a in self.agents if a.reputation < 40)
        rep_med = sum(1 for a in self.agents if 40 <= a.reputation < 75)
        rep_high = sum(1 for a in self.agents if a.reputation >= 75)

        return {
            "tick": self.tick_count, "is_running": self.is_running, "total": total,
            "coop": coop, "defect": defect, "recip": recip,
            "rep_low": rep_low, "rep_med": rep_med, "rep_high": rep_high,
            "avg_rep": avg_rep, "coop_freq": f"{int((coop / total) * 100)}%" if total else "0%"
        }


engine = EvolutionEngine()


async def run_evolution():
    while True:
        if engine.is_running:
            engine.evolve_step()
        await asyncio.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(run_evolution())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)


# ==========================================
# 3. 核心业务 API (登录、签到、交易等)
# ==========================================
class AuthReq(BaseModel):
    student_id: str
    password: str
    name: str = ""


@app.post("/api/login")
def login(req: AuthReq, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute('SELECT * FROM users WHERE student_id=? AND password=?', (req.student_id, req.password))
    user = c.fetchone()
    if not user: raise HTTPException(status_code=401, detail="学号或密码错误")
    return {"status": "success", "data": dict(user)}


@app.post("/api/register")
def register(req: AuthReq, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    if c.execute('SELECT student_id FROM users WHERE student_id=?', (req.student_id,)).fetchone():
        raise HTTPException(status_code=400, detail="该学号已注册")
    c.execute('INSERT INTO users VALUES (?, ?, ?, 100, 80, "user", "", 0, 0, 0)',
              (req.student_id, req.password, req.name or f"同学_{req.student_id[-4:]}"))
    db.commit()
    return {"status": "success", "msg": "注册成功，已获赠100积分初始额度！"}


class ActionReq(BaseModel):
    student_id: str
    action_type: str = ""
    amount: int = 0
    target_id: str = ""


@app.post("/api/sign")
def daily_sign(req: ActionReq, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    row = c.execute('SELECT score, last_sign_date, sign_days FROM users WHERE student_id=?',
                    (req.student_id,)).fetchone()
    if not row: raise HTTPException(status_code=404)

    current_score, last_date_str, sign_days = row
    today = date.today()

    if last_date_str == today.isoformat():
        raise HTTPException(status_code=400, detail="今天已签到")

    sign_days = sign_days + 1 if (
                last_date_str and today - date.fromisoformat(last_date_str) == timedelta(days=1)) else 1
    reward = 20 if sign_days >= 7 else (10 if sign_days >= 3 else 5)

    c.execute('UPDATE users SET score=?, last_sign_date=?, sign_days=? WHERE student_id=?',
              (current_score + reward, today.isoformat(), sign_days, req.student_id))
    db.commit()
    return {"status": "success", "new_score": current_score + reward,
            "msg": f"签到成功！连签 {sign_days} 天，得 {reward} 分"}


class WifiReq(BaseModel):
    student_id: str
    name: str
    speed: str
    reserved: str
    cost: int


@app.post("/api/wifi")
def publish_wifi(req: WifiReq, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    if not c.execute('SELECT score FROM users WHERE student_id=?', (req.student_id,)).fetchone():
        raise HTTPException(status_code=400, detail="用户异常，请重新登录")

    c.execute('INSERT INTO wifi_nodes (owner_id, name, speed, reserved, cost) VALUES (?, ?, ?, ?, ?)',
              (req.student_id, req.name, req.speed, req.reserved, req.cost))
    c.execute('UPDATE users SET score = score + 2 WHERE student_id=?', (req.student_id,))
    db.commit()
    return {"status": "success",
            "new_score": c.execute('SELECT score FROM users WHERE student_id=?', (req.student_id,)).fetchone()[0]}


@app.get("/api/wifi")
def get_wifis(db: sqlite3.Connection = Depends(get_db)):
    return [dict(row) for row in db.cursor().execute('SELECT * FROM wifi_nodes').fetchall()]


@app.get("/api/store")
def get_store(db: sqlite3.Connection = Depends(get_db)):
    return [dict(row) for row in db.cursor().execute('SELECT * FROM store_items').fetchall()]


@app.post("/api/transaction")
def process_transaction(req: ActionReq, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    current_score = c.execute('SELECT score FROM users WHERE student_id=?', (req.student_id,)).fetchone()[0]

    if current_score < req.amount:
        raise HTTPException(status_code=400, detail=f"余额不足！需要 {req.amount} 分")

    new_score = current_score
    msg = ""

    if req.action_type == 'connect':
        new_score -= req.amount
        msg = "连接成功，扣除积分并结算流量"
        c.execute('UPDATE users SET consumed_gb = consumed_gb + 1 WHERE student_id=?', (req.student_id,))
        if req.target_id:
            c.execute('UPDATE users SET shared_gb = shared_gb + 1 WHERE student_id=?', (req.target_id,))

    elif req.action_type == 'buy':
        new_score -= req.amount
        msg = "商品兑换成功！"

    elif req.action_type == 'auction':
        second_price = random.randint(8, 15)
        if req.amount >= second_price:
            new_score -= second_price
            msg = f"竞拍成功！按第二高价实扣 {second_price} 分"
        else:
            msg = f"竞拍失败。出价过低，第二高价为 {second_price}"

    c.execute('UPDATE users SET score=? WHERE student_id=?', (new_score, req.student_id))
    db.commit()
    return {"status": "success", "new_score": new_score, "msg": msg}


# ==========================================
# 4. 排行榜算法 (保留了解决平局双重排序机制)
# ==========================================
@app.get("/api/leaderboard")
def get_leaderboard(db: sqlite3.Connection = Depends(get_db)):
    users = db.cursor().execute('SELECT name, shared_gb, consumed_gb, role FROM users').fetchall()
    results = []
    total_shared = 0
    grades = {'S': 0, 'A': 0, 'B': 0, 'C': 0}

    for u in users:
        total_shared += u['shared_gb']
        rep = min(100, max(0, 80 + u['shared_gb'] * 2 - u['consumed_gb']))

        if rep >= 90:
            grade = 'S'; grades['S'] += 1
        elif rep >= 75:
            grade = 'A'; grades['A'] += 1
        elif rep >= 60:
            grade = 'B'; grades['B'] += 1
        else:
            grade = 'C'; grades['C'] += 1

        results.append({"name": u['name'], "shared": u['shared_gb'], "grade": grade, "rep": rep, "role": u['role']})

    results.sort(key=lambda x: (x['shared'], x['rep']), reverse=True)
    return {"top_users": results[:10], "total_shared": total_shared, "grades": grades, "total_users": len(users)}


# ==========================================
# 5. 沙盘中控大屏 API (全功能回归)
# ==========================================
@app.get("/api/simulation")
def get_simulation():
    return engine.get_stats()


@app.post("/api/simulation/toggle")
def toggle_simulation():
    engine.is_running = not engine.is_running
    return {"status": "success"}


@app.post("/api/simulation/add_agent")
def add_agent():
    engine.add_random_student()
    return {"status": "success"}


@app.post("/api/simulation/reset")
def reset_simulation():
    engine.reset_population()
    return {"status": "success"}


# ==========================================
# 6. 管理员后台 API (完整RBAC)
# ==========================================
class AdminActionReq(BaseModel):
    operator_id: str
    target_id: str = ""
    data: dict = {}


def check_admin(oid: str, db: sqlite3.Connection, req_root=False):
    role = db.cursor().execute('SELECT role FROM users WHERE student_id=?', (oid,)).fetchone()[0]
    if req_root and role != 'root': raise HTTPException(status_code=403, detail="需要 Root 权限")
    if role not in ['root', 'admin']: raise HTTPException(status_code=403, detail="权限不足")
    return role


@app.post("/api/admin/users")
def get_users(req: AdminActionReq, db: sqlite3.Connection = Depends(get_db)):
    check_admin(req.operator_id, db)
    return [dict(r) for r in db.cursor().execute('SELECT * FROM users').fetchall()]


@app.post("/api/admin/user/create")
def admin_create_user(req: AdminActionReq, db: sqlite3.Connection = Depends(get_db)):
    op_role = check_admin(req.operator_id, db)
    new_role = req.data.get('role', 'user')
    if new_role in ['root', 'admin'] and op_role != 'root':
        raise HTTPException(status_code=403, detail="普通管理员不能创建超级账号")
    try:
        db.cursor().execute('INSERT INTO users VALUES (?, ?, ?, 100, 100, ?, "", 0, 0, 0)',
                            (req.data['student_id'], req.data['password'], req.data['name'], new_role))
        db.commit()
        return {"status": "success", "msg": "账户创建成功"}
    except:
        raise HTTPException(status_code=400, detail="学号可能已存在")


@app.post("/api/admin/user/delete")
def delete_user(req: AdminActionReq, db: sqlite3.Connection = Depends(get_db)):
    op_role = check_admin(req.operator_id, db)
    if req.target_id == 'root': raise HTTPException(status_code=400, detail="无法删除root")

    target_user = db.cursor().execute('SELECT role FROM users WHERE student_id=?', (req.target_id,)).fetchone()
    if not target_user: raise HTTPException(status_code=404)
    if op_role == 'admin' and target_user[0] in ['root', 'admin']:
        raise HTTPException(status_code=403, detail="管理员不能删除同级或上级")

    db.cursor().execute('DELETE FROM users WHERE student_id=?', (req.target_id,))
    db.commit()
    return {"status": "success"}


@app.post("/api/admin/store/add")
def add_store_item(req: AdminActionReq, db: sqlite3.Connection = Depends(get_db)):
    check_admin(req.operator_id, db)
    db.cursor().execute('INSERT INTO store_items (name, cost, desc) VALUES (?, ?, ?)',
                        (req.data['name'], req.data['cost'], req.data['desc']))
    db.commit()
    return {"status": "success"}


@app.post("/api/admin/store/delete")
def delete_store_item(req: AdminActionReq, db: sqlite3.Connection = Depends(get_db)):
    check_admin(req.operator_id, db)
    db.cursor().execute('DELETE FROM store_items WHERE id=?', (req.target_id,))
    db.commit()
    return {"status": "success"}


@app.post("/api/admin/wifi/delete")
def delete_wifi_node(req: AdminActionReq, db: sqlite3.Connection = Depends(get_db)):
    check_admin(req.operator_id, db)
    db.cursor().execute('DELETE FROM wifi_nodes WHERE id=?', (req.target_id,))
    db.commit()
    return {"status": "success"}


# ==========================================
# 7. 静态服务挂载
# ==========================================
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)