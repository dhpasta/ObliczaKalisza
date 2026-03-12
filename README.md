# 🗺️ City quest support application
Application created to support organization of city quest. Event is organized at Polish Independece Day by Scouting Assosiation I belong to.

Application written in Python with Flask framework and MySQL database.

Project estabilished to make organizators work easier, lower costs of event and offer participants an interactive entertainment.

Application has been used to support 5 editions of event "Oblicza Kalisza". Around 200 people has participated in each. View event [webpage](https://www.facebook.com/ObliczaKalisza).


## ❓ What is a "city quest"?
According to our idea, city quest is a form of game in which participants compete with each other by seeking and solving tasks hidden in some area of the city.
People of all age gathered in patrols are pursuing main goal of the quest collecting points and items. There are prices for the most involved!

This is our alternative for celebrating Independence Day, teaching about history of our city integrating residents.

<details>

<summary>Details of the quest...</summary>

- every edition differs in main goal, subject and decorations,
- each **patrol** receives **patrol booklet** containing instructions and set of tasks,
- tasks can be presented in different forms e.g., as a list of riddles, encrypted coordinates or points on map,
- whole event is devided into few **stages**, patrols respectively gatheres informations to use in following stages,
- every city quest has a **main goal**,
- there are two types of tasks:
    - **checkpoints** - QR codes scattered around field of event. Patrols reveals content of task by scanning found code with their mobile phone,
    - **character stations** - hidden location where patrols carry out physical tasks for disguised characters. To check in to station, patrol must meet conditions described in instructions e.g., complete previous stage or acquire secret password,
- city quest ends at a specific time. Patrols must check in at event office. Summary and award ceremony follows,
- patrol that scores the most points wins. Points are awarded for: achieving the main goal, completing 
each stage, completed tasks, received bonuses and time to end the quest.
</details>


## 🎯 App main features
- users use application by scanning QR codes with smartphones. Codes are placed in checkpoints, patrol and organizator booklets and in application itself,
- based on data stored in browser cookie app renders appropriate page,
- visiting event web address users get access to proper home page.

Depending on role in city quest there are available features:

### 👔 Management:
- password protected administration panel,
- granting organizer privileges by displaying proper QR code,
- managing quest items: monitoring state of checkpoints and work of character stations,
- managing patrols: viewing patrols data, adding unregistered patrols to database, monitoring patrols actions,
- maintaing tasks parameters during event, granting bonuses avalible only in event office,
- monitoring classification and generating final results.

### 🦺 Organizers:
- maintaining checkpoints - linking random QR codes with their function and placement,
- monitoring state of placed checkpoints,
- granting points for filled tasks at character stations,
- maintaining work of character station - viewing visits history and monitoring remaining patrols,
- granting patrols bonuses according to instructions.

### 🏃 Participants:
- check in and check out for play,
- preview of scored points and gathered items,
- access to instructions, booklet and tips,
- main page with individual QR code necessary to receive points for completed tasks.

## 📷 Screenshots

<details>

<summary>Show examples of usage:</summary>

<img src="assets/screenshots1.jpg">

**Left:** list of options avalible in administration panel

**Center:** organizer home page contains key instructions, map of districts and summary of checkpoints already installed,

**Right:** character home page shows list of patrols which already visited their station, awarded points and time of visit. Below there is list of remaining patrols in game.

---

<img src="assets/screenshots2.jpg">

Image shows patrol home page (edition 2025).

**First image from the top**: patrol name, type of path and fellowship, points, gathered items, map with fellowships scores.

**Second image**: avalible and collected bonuses, patrol QR code, access to instructions and contact with organizers.
</details>


## 📡 Project deploy
Docker container ready do run. Requires MySQL database running in another container.


## 🔔 Planned features
- create registration form for event in app,
- check patrol location when QR code address is requested,
- implement interactions between patrols,
- develop administration panel abilities to maintain app database,
- unify and reduce amount of funcions in database.py,
- create a test platform for new types of tasks,
- add statistics preview to admin panel e.g., the most and least visited checkpoint.
