# Candy Game

This is a simple Candy Crush clone implemented in Python using the Pygame library.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/candy-crush-clone.git
    cd candy-crush-clone
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

Run the game using the following command:
```sh
python main.py
```

## Configuration

You can configure the game settings by editing the `config.ini` file.

### Example Configuration

```ini
[general]
frames_per_second = 60
texture_pack = CandyTexturePack

[graphics]
grid_width = 15
grid_height = 10
cell_size = 64
grid_margin = 64

[game-objectives]
red_cells = 30
green_cells = 30
blue_cells = 30
yellow_cells = 30
purple_cells = 30
pink_cells = 30
```

### Available Settings

- `frames_per_second`: Sets the frame rate of the game. Higher values result in smoother animations but may require more processing power. Default is `60`.

- `texture_pack`: Specifies the texture pack to be used for the game graphics. Default is `CandyTexturePack`.

- `grid_width`: Defines the number of columns in the game grid. Default is `15`.

- `grid_height`: Defines the number of rows in the game grid. Default is `10`.

- `cell_size`: Sets the size of each cell in the grid in pixels. Default is `64`.

- `grid_margin`: Specifies the margin around the grid in pixels. Default is `64`.

- `[game-objectives]`: Specifies for each type of cell the amount that must be obtained in order to win the game