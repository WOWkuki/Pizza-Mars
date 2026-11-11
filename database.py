"""SQLite database for user accounts, login/signup, and saved progress.

Uses Python's built-in `sqlite3` and `hashlib` modules so every player's
progress, stats, settings, and saved run are stored in a real SQL database
(`accounts.db`). Includes a pre-made `admin` / `admin` account with full progress.
"""

import hashlib
import json
import os
import sqlite3

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, "accounts.db")


def _hash_password(password):
    """Return a SHA-256 hex digest of the password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _build_admin_saved_run():
    """Create a full-gear Floor 5 saved run for the admin testing account."""
    from game import Game
    g = Game(seed=777, full_progress=True)
    while g.floor < 5:
        g.descend()
    g.rooms_cleared = 18
    p = g.player
    p.max_hp = 35
    p.hp = 35
    p.weapon = "cutter"
    p.armor = "apron"
    p.pizzas = 4
    p.credits = 250
    p.kills = 45
    # Mark all non-boss rooms visited & cleared so the floor map is explored
    for pos, rm in g.dungeon.rooms.items():
        rm.visited = True
        if rm.role != "boss":
            rm.monsters.clear()
            rm.locked = False
            rm.cleared = True
    return g.to_dict()


def init_db(db_path=None):
    """Create the SQLite accounts table and ensure the `admin` account exists."""
    conn = sqlite3.connect(db_path or DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                high_score INTEGER NOT NULL DEFAULT 0,
                highest_floor INTEGER NOT NULL DEFAULT 1,
                total_kills INTEGER NOT NULL DEFAULT 0,
                games_won INTEGER NOT NULL DEFAULT 0,
                full_progress INTEGER NOT NULL DEFAULT 0,
                settings_json TEXT NOT NULL DEFAULT '{}',
                saved_run_json TEXT
            )
            """
        )
        cur = conn.execute("SELECT username FROM accounts WHERE username = ?", ("admin",))
        if cur.fetchone() is None:
            admin_run = _build_admin_saved_run()
            conn.execute(
                """
                INSERT INTO accounts (
                    username, password_hash, high_score, highest_floor,
                    total_kills, games_won, full_progress, settings_json, saved_run_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "admin",
                    _hash_password("admin"),
                    9999,
                    5,
                    250,
                    10,
                    1,
                    json.dumps({"resolution_index": 2, "graphics_quality": "High"}),
                    json.dumps(admin_run),
                ),
            )
        conn.commit()
    finally:
        conn.close()


def signup_user(username, password, db_path=None):
    """Register a new account in the database.

    Returns (success: bool, message: str, account_dict: dict | None).
    """
    init_db(db_path)
    username = username.strip()
    if len(username) < 2:
        return False, "Username must be at least 2 characters.", None
    if len(password) < 2:
        return False, "Password must be at least 2 characters.", None

    conn = sqlite3.connect(db_path or DB_PATH)
    try:
        cur = conn.execute(
            "SELECT username FROM accounts WHERE LOWER(username) = LOWER(?)",
            (username,),
        )
        if cur.fetchone() is not None:
            return False, f"Account '{username}' already exists! Try logging in.", None

        default_settings = {"resolution_index": 2, "graphics_quality": "High"}
        conn.execute(
            """
            INSERT INTO accounts (
                username, password_hash, high_score, highest_floor,
                total_kills, games_won, full_progress, settings_json, saved_run_json
            ) VALUES (?, ?, 0, 1, 0, 0, 0, ?, NULL)
            """,
            (username, _hash_password(password), json.dumps(default_settings)),
        )
        conn.commit()
    finally:
        conn.close()

    acc = get_account(username, db_path=db_path)
    return True, f"Account '{username}' created and logged in!", acc


def login_user(username, password, db_path=None):
    """Verify username and password against the database.

    Returns (success: bool, message: str, account_dict: dict | None).
    """
    init_db(db_path)
    username = username.strip()
    if not username or not password:
        return False, "Please enter both username and password.", None

    conn = sqlite3.connect(db_path or DB_PATH)
    try:
        cur = conn.execute(
            "SELECT username, password_hash FROM accounts WHERE LOWER(username) = LOWER(?)",
            (username,),
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if row is None or row[1] != _hash_password(password):
        return False, "Invalid username or password.", None

    real_user = row[0]
    acc = get_account(real_user, db_path=db_path)
    tag = " (Full Progress Admin)" if acc.get("full_progress") else ""
    return True, f"Welcome back, {real_user}{tag}!", acc


def get_account(username, db_path=None):
    """Load an account's full data dictionary from the SQLite database."""
    init_db(db_path)
    conn = sqlite3.connect(db_path or DB_PATH)
    try:
        cur = conn.execute(
            """
            SELECT username, high_score, highest_floor, total_kills,
                   games_won, full_progress, settings_json, saved_run_json
            FROM accounts WHERE username = ?
            """,
            (username,),
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return None
    try:
        settings = json.loads(row[6]) if row[6] else {}
    except ValueError:
        settings = {}
    try:
        saved_run = json.loads(row[7]) if row[7] else None
    except ValueError:
        saved_run = None

    return {
        "username": row[0],
        "high_score": int(row[1]),
        "highest_floor": int(row[2]),
        "total_kills": int(row[3]),
        "games_won": int(row[4]),
        "full_progress": bool(row[5]),
        "settings": settings,
        "saved_run": saved_run,
    }


def update_account_settings(username, settings_dict, db_path=None):
    """Save resolution and graphics quality settings for the logged-in user."""
    if not username:
        return
    init_db(db_path)
    conn = sqlite3.connect(db_path or DB_PATH)
    try:
        conn.execute(
            "UPDATE accounts SET settings_json = ? WHERE username = ?",
            (json.dumps(settings_dict), username),
        )
        conn.commit()
    finally:
        conn.close()


def save_account_run(username, game, db_path=None):
    """Save the current in-progress game run & stats to the user's database row."""
    if not username or game is None:
        return False
    init_db(db_path)
    acc = get_account(username, db_path=db_path)
    if acc is None:
        return False

    new_high_score = max(acc["high_score"], game.score)
    new_highest_floor = max(acc["highest_floor"], game.floor)
    run_json = json.dumps(game.to_dict()) if game.state == "playing" else None

    conn = sqlite3.connect(db_path or DB_PATH)
    try:
        conn.execute(
            """
            UPDATE accounts
            SET high_score = ?, highest_floor = ?, saved_run_json = ?
            WHERE username = ?
            """,
            (new_high_score, new_highest_floor, run_json, username),
        )
        conn.commit()
    finally:
        conn.close()
    return True


def record_account_run_end(username, game, db_path=None):
    """Update lifetime stats when a run finishes (or on admin, keep full progress)."""
    if not username or game is None:
        return
    init_db(db_path)
    acc = get_account(username, db_path=db_path)
    if acc is None:
        return

    new_high = max(acc["high_score"], game.score)
    new_floor = max(acc["highest_floor"], game.floor)
    new_kills = acc["total_kills"] + game.player.kills
    new_wins = acc["games_won"] + (1 if game.state == "won" else 0)
    full_prog = 1 if (acc["full_progress"] or new_wins > 0) else 0

    # For the admin test account, keep the Floor 5 test save ready if they finish a run
    saved_json = json.dumps(_build_admin_saved_run()) if username == "admin" else None

    conn = sqlite3.connect(db_path or DB_PATH)
    try:
        conn.execute(
            """
            UPDATE accounts
            SET high_score = ?, highest_floor = ?, total_kills = ?,
                games_won = ?, full_progress = ?, saved_run_json = ?
            WHERE username = ?
            """,
            (new_high, new_floor, new_kills, new_wins, full_prog, saved_json, username),
        )
        conn.commit()
    finally:
        conn.close()
