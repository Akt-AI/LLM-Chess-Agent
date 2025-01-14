# Autonomous Chess Game with Stockfish Engines

This project demonstrates an autonomous chess game between two Stockfish engines, visualized live using OpenCV and saved as an MP4 video. The script generates board positions in real time, removes coordinates/labels from the SVGs, and saves each move for review.

## Features
- Autonomous chess game between two Stockfish engines.
- Real-time visualization of board positions using OpenCV.
- SVG board images saved to an `images` folder.
- Final game saved as an MP4 video.
- Clean board representation without coordinates or labels.

## Prerequisites
Ensure the following are installed on your system:

1. Python 3.7+
2. Required Python libraries:
   ```bash
   pip install python-chess svglib reportlab opencv-python-headless
   ```
3. Stockfish chess engine:
   - Install via your package manager:
     ```bash
     sudo apt install stockfish
     ```
   - Or download from the [official Stockfish website](https://stockfishchess.org/download/).

## Project Structure
- `autonomous_chess.py`: Main script to run the game.
- `images/`: Folder where SVG images of board positions are saved.
- `chess_game.mp4`: Output video of the game.

## Usage
1. Clone the repository or download the script.
2. Ensure the Stockfish engine path is correctly set in the script:
   ```python
   STOCKFISH_PATH = "/usr/games/stockfish"
   ```
3. Run the script:
   ```bash
   python autonomous_chess.py
   ```
4. Watch the live game in an OpenCV window. Press `q` to quit the visualization.

## Output
- Real-time game visualization.
- SVG images of each move saved in the `images/` folder.
- A complete game video saved as `chess_game.mp4`.

## Customization
- **Time per move**: Adjust the time limit for engine moves by modifying:
  ```python
  engine1.play(board, chess.engine.Limit(time=0.5))
  ```
- **SVG appearance**: Customize the board appearance using `chess.svg` options.
- **Video resolution and FPS**: Change video settings in the `VideoWriter` initialization:
  ```python
  video_writer = cv2.VideoWriter('chess_game.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 2, (800, 800))
  ```

## Troubleshooting
- **Stockfish Path Error**:
  Ensure the `STOCKFISH_PATH` points to the correct location of the Stockfish binary.
- **Missing Libraries**:
  Install required libraries using `pip`.
- **OpenCV Display Issues**:
  Use `opencv-python-headless` if running on a headless server.

## License
This project is licensed under the MIT License. Feel free to use and modify it as needed.

## Acknowledgments
- [python-chess](https://python-chess.readthedocs.io/): Python library for working with chess boards.
- [Stockfish](https://stockfishchess.org/): World-class open-source chess engine.
- [OpenCV](https://opencv.org/): For real-time visualization and video processing.
- [svglib](https://pypi.org/project/svglib/): For SVG to image conversion.


