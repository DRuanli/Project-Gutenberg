# Word Frequency in Classic Novels

This project analyzes word frequency patterns in classic novels from Project Gutenberg. It includes functionality for scraping texts, preprocessing, analyzing word frequencies, visualizing the results, and generating insights about themes and comparative language usage.

## Features

- **Data Collection**: Automated scraping of classic novels from Project Gutenberg
- **Text Preprocessing**: Cleaning, tokenization, stopword removal, and lemmatization
- **Word Frequency Analysis**: Identification of frequent words, rare words, and comparative usage
- **Visualization**: Word clouds, bar charts, and histograms of word frequency distributions
- **Theme Analysis**: Topic modeling to identify common themes across novels
- **Comparative Analysis**: Tools to compare word usage between different authors or works

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

The project can be run using the main.py script with various command-line arguments:

```
python main.py --download --book-ids 84 1342 --preprocess --analyze --visualize
```

Available options:
- `--download`: Download books from Project Gutenberg
- `--book-ids`: Specify book IDs to download (e.g., 84 1342)
- `--preprocess`: Clean and preprocess the downloaded texts
- `--analyze`: Generate word frequency analyses
- `--visualize`: Create visualizations of the results
- `--themes`: Analyze themes across novels
- `--compare`: Compare word usage between novels
- `--all`: Run the complete pipeline

## Project Structure

- `src/`: Source code modules
  - `scraper/`: Web scraping functionality
  - `preprocessor/`: Text cleaning and tokenization
  - `analyzer/`: Word frequency analysis
  - `visualizer/`: Data visualization
  - `insights/`: Theme and comparative analysis
- `data/`: Data storage
  - `raw/`: Raw downloaded novels
  - `processed/`: Preprocessed text data
  - `results/`: Analysis results
- `output/`: Generated outputs
  - `visualizations/`: Generated charts and word clouds
  - `reports/`: Analysis reports
- `config/`: Configuration settings
- `main.py`: Main execution script

## Example

To analyze the language patterns in "Frankenstein" (book ID 84) and "Pride and Prejudice" (book ID 1342):

```
python main.py --download --book-ids 84 1342 --all
```

This will download the books, preprocess them, analyze word frequencies, create visualizations, and generate insights about themes and comparative language usage.

## License

This project is for educational purposes. Please respect Project Gutenberg's terms of use when scraping content.