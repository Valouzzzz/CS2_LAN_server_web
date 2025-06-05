# 🎯 CS2 Match Logger & Elo Tracker

A lightweight web tool to track **kills**, **match statistics**, and **Elo rankings** in private CS2 matches. It also includes pages to easily configure commands and create 1v1 tournament brackets.

---

## 🚀 How to Start the Server

1. Start a training match in CS2 (offline or local server).
2. Run the Flask server with the following command:

```bash
python server.py
```

3. In the CS2 console, enter the following command (replace your_ip with your actual local IP address):


```bash
logaddress_add_http "http://your_ip:80/logs"
```

4. Open a web browser and go to:


```bash
http://your_ip
```


---

## 🖥️ Main Features

✅ Real-time kill feed display (auto-refresh every 10 seconds)

📊 Live match statistics table (kills, deaths, K/D ratio, etc.)

🏆 Elo ranking system based on player performance

🔄 Automatic log data collection using CS2’s logaddress_add_http API

---

## 🌐 Additional Pages (in the templates/ folder)

📋 commande.html

Easily generate custom commands to tweak your match settings.

🏆 tournois.html

- Create a 1v1 tournament bracket:

- Choose the number of players

- Enter player names

- The match tree is generated automatically

---

## 🔧 Requirements

Python 3.x

Flask (pip install flask)

---

## 🔮 Planned Features

- 🤖 **Discord Integration**  
  Automatic match updates, killfeed highlights, and Elo ranking posts directly in your Discord server.

- 🗳️ **Map Voting System**  
  Let players vote for the next map through the web interface or Discord integration.

- 📈 **Enhanced Elo System & Tournament Bracket**  
  - More accurate Elo calculations with support for K-factor tuning, win streak bonuses, and placement matches.  
  - Smarter tournament bracket logic: automatic seeding, match history, and final results display.