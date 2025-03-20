from fastapi import FastAPI, HTTPException, Form
from typing import Optional
import sqlite3
from fastapi.responses import HTMLResponse, RedirectResponse

# Initialize FastAPI app
app = FastAPI(title="Player Profile API", description="Simplified UI for managing player profiles", version="1.0")

# Database setup
def init_db():
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        age INTEGER,
                        position TEXT,
                        force INTEGER,
                        agility INTEGER,
                        vision INTEGER,
                        private_url TEXT UNIQUE
                    )''')
    conn.commit()
    conn.close()

init_db()

def generate_simple_id(name: str) -> str:
    return "-".join(name.lower().split())[:15]  # Generate a simple ID based on the player's name

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Player Profile API</title>
        </head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1>🏆 Player Profile Manager 🏆</h1>
            <p><a href="/create-profile-form" style="font-size: 20px; text-decoration: none; color: blue;">➕ Create a Player Profile</a></p>
            <p><a href="/profiles" style="font-size: 20px; text-decoration: none; color: green;">📜 View All Profiles</a></p>
        </body>
    </html>
    """

@app.get("/create-profile-form", response_class=HTMLResponse)
def create_profile_form():
    return """
    <html>
        <head><title>Create Player Profile</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1>Create a Player Profile</h1>
            <form action="/create-profile/" method="post">
                <label>Name:</label><br><input type="text" name="name" required><br><br>
                <label>Age:</label><br><input type="number" name="age" required><br><br>
                <label>Position:</label><br><input type="text" name="position" required><br><br>
                <label>Force:</label><br><input type="number" name="force" required><br><br>
                <label>Agility:</label><br><input type="number" name="agility" required><br><br>
                <label>Vision:</label><br><input type="number" name="vision" required><br><br>
                <input type="submit" value="Create Profile">
            </form>
        </body>
    </html>
    """

@app.post("/create-profile/")
def create_profile(name: str = Form(...), age: int = Form(...), position: str = Form(...), force: int = Form(...), agility: int = Form(...), vision: int = Form(...)):
    player_id = generate_simple_id(name)
    private_url = player_id  
    
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    cursor.execute("SELECT private_url FROM players WHERE private_url = ?", (private_url,))
    existing_player = cursor.fetchone()
    
    if existing_player:
        conn.close()
        raise HTTPException(status_code=400, detail="A profile with this name already exists. Please use a different name.")
    
    cursor.execute("INSERT INTO players (id, name, age, position, force, agility, vision, private_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (player_id, name, age, position, force, agility, vision, private_url))
    conn.commit()
    conn.close()
    
    return {"player_id": player_id, "profile_url": f"http://127.0.0.1:8000/profile/{private_url}"}

@app.get("/profiles", response_class=HTMLResponse)
def get_all_profiles():
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, private_url FROM players")
    players = cursor.fetchall()
    conn.close()
    
    html = "<h1>All Player Profiles</h1><ul>"
    for player in players:
        html += f"<li><a href='http://127.0.0.1:8000/profile/{player[1]}'>{player[0]}</a></li>"
    html += "</ul><p><a href='/'>🏠 Back to Home</a></p>"
    return HTMLResponse(content=html)

@app.get("/profile/{private_url}", response_class=HTMLResponse)
def get_profile(private_url: str):
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, age, position, force, agility, vision FROM players WHERE private_url = ?", (private_url,))
    player = cursor.fetchone()
    conn.close()
    
    if player:
        name, age, position, force, agility, vision = player
        return f"""
        <html>
        <head><title>{name}'s Profile</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h1>{name}'s Profile</h1>
            <p><strong>Profile URL:</strong> <a href='http://127.0.0.1:8000/profile/{private_url}'>http://127.0.0.1:8000/profile/{private_url}</a></p>
            <p>Age: {age}</p>
            <p>Position: {position}</p>
            <p>Force: {force}</p>
            <p>Agility: {agility}</p>
            <p>Vision: {vision}</p>
            <p><a href='/profiles'>🏠 Back to Profiles</a></p>
        </body>
        </html>
        """
    raise HTTPException(status_code=404, detail="Profile not found")
