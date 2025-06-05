from flask import Flask, request, redirect, render_template
import datetime
import os
import re

app = Flask(__name__)
LOG_FILE = "logs.txt"
COMMAND_LOG_TAG = "[COMMANDE]"
ELO_FILE = "elo_scores.txt"
K_FACTOR = 32

# Initialisation des fichiers si absents
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== CS2 LOGS START ===\n")

if not os.path.exists(ELO_FILE):
    with open(ELO_FILE, "w", encoding="utf-8") as f:
        f.write("")

def load_elo_scores():
    scores = {}
    if os.path.exists(ELO_FILE):
        with open(ELO_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    player, score = line.strip().split(":")
                    scores[player] = float(score)
                except ValueError:
                    continue
    return scores

def save_elo_scores(scores):
    with open(ELO_FILE, "w", encoding="utf-8") as f:
        for player, score in scores.items():
            f.write(f"{player}:{score}\n")

def update_elo(winner, loser):
    scores = load_elo_scores()
    R_winner = scores.get(winner, 1000)
    R_loser = scores.get(loser, 1000)
    E_winner = 1 / (1 + 10 ** ((R_loser - R_winner) / 400))
    E_loser = 1 - E_winner
    scores[winner] = R_winner + K_FACTOR * (1 - E_winner)
    scores[loser] = R_loser + K_FACTOR * (0 - E_loser)
    save_elo_scores(scores)

@app.route('/logs', methods=['POST'])
def receive_log():
    log_line = request.get_data(as_text=True).strip()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = f"[{timestamp}] {log_line}"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

    kill_match = re.search(
        r'"(?P<killer>[^"]+)" \[.*?\] killed "(?P<victim>[^"]+)" \[.*?\] with "(?P<weapon>[^"]+)"',
        log_line
    )
    if kill_match:
        killer = kill_match.group("killer")
        victim = kill_match.group("victim")
        update_elo(killer, victim)

    return '', 200

@app.route('/clear', methods=['POST'])
def clear_logs():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== CS2 LOGS CLEARED ===\n")
    return redirect('/')

@app.route('/command', methods=['POST'])
def handle_command():
    command = request.form.get("command", "").strip()
    if command:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {COMMAND_LOG_TAG} {command}\n")
    return redirect('/')

@app.route('/')
def show_logs():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-500:]

        kill_pattern = re.compile(
            r'"(?P<killer>[^"]+)" \[.*?\] killed "(?P<victim>[^"]+)" \[.*?\] with "(?P<weapon>[^"]+)"'
        )
        accountid_map = {}
        kill_lines = []

        for line in lines:
            match = kill_pattern.search(line)
            if match:
                killer = match.group("killer")
                victim = match.group("victim")
                weapon = match.group("weapon")
                kill_lines.append(f"{killer} a tué {victim} avec {weapon}")
                for player in [killer, victim]:
                    id_match = re.search(r'\[U:1:(\d+)\]', player)
                    if id_match:
                        accountid = id_match.group(1)
                        accountid_map[accountid] = player

        if not kill_lines:
            kill_lines = ["Aucun kill récent trouvé."]

        fields = []
        players_data = {}
        current_fields = []
        current_data = {}

        fields_pattern = re.compile(r'"fields"\s*:\s*"(.*)"')
        player_pattern = re.compile(r'"player_\d+"\s*:\s*"(.*)"')

        for line in lines:
            f_match = fields_pattern.search(line)
            if f_match:
                current_fields = [f.strip() for f in f_match.group(1).split(",")]
                current_data = {}
            else:
                p_match = player_pattern.search(line)
                if p_match and current_fields:
                    values = [v.strip() for v in p_match.group(1).split(",")]
                    if len(values) == len(current_fields):
                        player_info = dict(zip(current_fields, values))
                        if "accountid" in player_info:
                            aid = player_info["accountid"]
                            if aid in accountid_map:
                                player_info["accountid"] = accountid_map[aid]
                        current_data[len(current_data)] = player_info

        fields = current_fields
        players_data = current_data

        if fields and players_data:
            table_html = "<h2>Stats des joueurs</h2>"
            table_html += '<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; color:#c7c7c7;">'
            table_html += "<tr>" + "".join(f"<th>{field}</th>" for field in fields) + "</tr>"
            for idx in sorted(players_data.keys()):
                row = players_data[idx]
                table_html += "<tr>" + "".join(f"<td>{row[field]}</td>" for field in fields) + "</tr>"
            table_html += "</table>"
        else:
            table_html = "<p>Aucune donnée joueur disponible.</p>"

        try:
            with open(ELO_FILE, "r", encoding="utf-8") as f:
                full_elo_raw = f.read()
            raw_elo_html = f"""
                <h2>Elo :</h2>
                <div class="logs">{full_elo_raw}</div>
            """
        except Exception as e:
            raw_elo_html = f"<p>Erreur lors de la lecture de elo_scores.txt : {e}</p>"

    except Exception as e:
        kill_lines = [f"Erreur lors de la lecture du fichier de logs: {e}"]
        table_html = ""
        raw_elo_html = ""

    kills_html = "<br>".join(kill_lines)

    return f"""
    <html>
        <head>
            <title>Logs CS2 - Kills, Stats et Elo</title>
            <meta http-equiv="refresh" content="10">
            <style>
                body {{
                    background-color: #1e1e1e;
                    color: #c7c7c7;
                    font-family: monospace;
                    padding: 20px;
                }}
                h1 {{
                    color: #00ffc8;
                }}
                table {{
                    width: 100%;
                    margin-top: 20px;
                    background-color: #2e2e2e;
                }}
                th, td {{
                    padding: 6px 8px;
                    text-align: center;
                    border: 1px solid #444;
                }}
                th {{
                    background-color: #444;
                }}
                .logs {{
                    white-space: pre-wrap;
                    background-color: #2e2e2e;
                    padding: 10px;
                    border-radius: 8px;
                    max-height: 40vh;
                    overflow-y: auto;
                }}
                button {{
                    margin-top: 10px;
                    padding: 8px 16px;
                    background-color: #00ffc8;
                    color: black;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }}
            </style>
        </head>
        <body>
            <h1>Logs CS2 (Kills formatés)</h1>
            <div class="logs">{kills_html}</div>
            {table_html}
            {raw_elo_html}

            <form method="POST" action="/clear">
                <button type="submit">🧹 Vider les logs</button>
            </form>

            <a href="/page2"><h3>Command</h3></a>
            <a href="/page3" target="_blank"><h3>Tournois</h3></a>
        </body>
    </html>
    """

@app.route('/page2')
def page2():
    try:
        return render_template('commande.html')
    except Exception as e:
        return f"<pre>Erreur : {e}</pre>", 500

@app.route('/page3')
def page3():
    try:
        scores = load_elo_scores()
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return render_template('tournois.html', classement=sorted_scores)
    except Exception as e:
        return f"<pre>Erreur : {e}</pre>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
