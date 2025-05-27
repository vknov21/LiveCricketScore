# 🏏 Cricket Live Score Update

**Cricket Live Score Update** is a lightweight Python desktop application that provides real-time cricket scores in a compact, always-on-top window. It’s designed for professionals who want live match updates without the distraction of watching TV—ideal for multitasking during work hours.

The app fetches data using GraphQL, refreshing every **4 seconds** while keeping data usage to a minimum (~1–2 KB per refresh), making it suitable even for low-bandwidth environments.

---

## 🚀 Getting Started

### 📦 Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### ▶️ Running the App

To start the application, run:

```bash
python3 <your_path>/cricket_iql.py
```

- A window will appear.
- The terminal will prompt you for a **match URL** or **6-digit match code** from [cricket.com](https://www.cricket.com/).
- Upon entering a valid code or URL, the live score window will update automatically every 4 seconds.

---

## ✨ Features

### 🖥️ User Interface

- ✅ **Always-on-top window** (can be toggled via right-click).
- 🔍 **Dynamic transparency**:
  - Opaque on hover or focus.
  - Transparent when focus is lost.
- 🖱️ **Draggable window** to reposition on your screen.
- 🪟 **Double-click** to toggle a title bar with a close button.

### 📊 Live Match Info

- 🏁 **Match status**:
  - Displays result for completed matches.
  - Notifies delays or interruptions (e.g., rain delay, lunch break).
- 🧢 **Teams Overview**:
  - Batting team's short name and live score.
  - Fielding team's short name and current bowler.
- 🏃 **Batsmen Info**:
  - Shows both players on the crease with strike info and runs.
- 🔄 **Over Timeline**:
  - Ball-by-ball breakdown.
  - Ongoing over shows all deliveries so far; last over shows last 3 balls.
- 🟢 **Refresh indicator**:
  - Live refresh is visualized by green text color.
- 🧩 **Customizable Output**:
  - Users can configure what match data is displayed.

---

## 🧰 Framework Extensibility

The app serves as a **foundation for building custom desktop overlays**:

- Easily extend or modify the UI and data.
- Use it to display any real-time stats or information relevant to your workflow.

---

## 🔮 Future Improvements

The project prioritizes minimal data consumption (less than **8 MB** for total two innings of ODI). However, some areas for future enhancement include:

- ❌ **Disable refresh** after match completion.
- 📝 **Enhanced info display** via scrolling:
  - Live commentary
  - Previous innings summaries
  - Dismissed players and their scores
  - Upcoming batsman
  - Umpire names, venue details, and more

---

## 📌 Note

Gzip compression is currently not supported by the website, which previously helped reducing data usage further.

---

## 🛠️ Contributing

Contributions, feature requests, and suggestions are welcome! Feel free to fork the repository and submit pull requests.

---

## 📃 License

This project is open-source and available under the [MIT License](LICENSE).
```