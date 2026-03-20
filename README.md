# PengPengAgent
An LLM-based AI agent capable of playing the "Boomsday Project" puzzles in Hearthstone.

# User Guide

1. **Configure the Log Path**: 
   Open `hsplayer/log_path.py` and update the file path to point to your local Hearthstone log file location.
   *(Default location is usually `%LOCALAPPDATA%\Blizzard\Hearthstone\Logs\Power.log` on Windows)*

2. **Launch the Application**:
   Run the following command in your terminal to start the service:
   ```bash
   streamlit run app.py