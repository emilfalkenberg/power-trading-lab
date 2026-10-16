# Power Trading Lab

## About the Project
Power Trading lab is a personal learning project where I use my spare time to develop Python and explore how electricity markets work. 

I have previous programming experiance with typescript, primarily from building websites and web applications. Through this project, I want to expand my programming knowledge and gain a better understanding of energy trading, data analysis and trading strategies.

## Project 1 – Market Analyzer
My first Python project, focused on learning the fundamentals of Python programming. 

The project introduced me to Python syntax, functions, loops, lists and dictionaries, while working on basic electricity price calculations and market analysis.

## Project 2 – Power Data Explorer
This project uses real historical electricity prices from the Danish DK1 day-ahead market to analyze price movements and simulate battery trading.

The battery simulation follows a simple rule-based strategy with three possible actions; buy, sell or hold.

The model takes several factors into account:
* Battery capacity and maximum charging/discharging power
* Battery efficiency
* Hourly self-discharge
* Trading costs
* Electricity price thresholds for buying and selling

The project also inclues electricity price statistics, daily analysis, visualizations using Matplotlib and automated test to verify the battery calculations

## Technologies Used
* Python
* Matplotlib
* CSV data processing 
* Git and Github

## How to Run

### 1. Clone the repository

```bash
git clone <https://github.com/emilfalkenberg/power-trading-lab>
cd power-trading-lab
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Run Project 2

```bash
python project_02_power_data_explorer/main.py
```

The program loads historical DK1 electricity prices, performs market analysis, runs a battery trading simulation and displays the results using Matplotlib.

### 4. Run battery tests

```bash
python project_02_power_data_explorer/test_battery.py
```