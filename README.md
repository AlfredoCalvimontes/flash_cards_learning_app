# Flash Cards Learning App

A Windows desktop application for practicing and learning concepts through flash cards, featuring smart scheduling, spaced repetition, and category-based organization. Built as an AI pair programming practice project.

## Features

- 📝 Create and manage flash cards with categories
- 🎯 Smart card selection based on difficulty and priority
- ⏰ Flexible scheduling system with multiple frequency modes
- 📊 Track progress and review history
- 📥 Import/Export cards and categories via CSV
- 🔄 Background operation with system tray integration
- 🔒 Automatic data backup and recovery
- 🎨 Modern PySide6-based UI with dark mode support

## Requirements

- Windows 10/11
- Python 3.11 or higher
- 4GB RAM minimum
- 100MB disk space
- Display resolution 1280x720 or higher

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AlfredoCalvimontes/flash_cards_learning_app.git
cd flash_cards_learning_app
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Activate the virtual environment (if not already activated):
```bash
.\venv\Scripts\activate
```

2. Run the application:
```bash
python main.py
```

## Development Setup

1. Install additional development dependencies:
```bash
pip install -r requirements.txt
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
pytest
```

## Project Structure

```
flash_cards_learning_app/
├── core/             # Core business logic
│   └── serialization/  # Data serialization
├── database/        # SQLAlchemy models and DB logic
├── ui/             # PySide6 UI components
├── tests/          # Test suite
├── main.py         # Application entry point
└── requirements.txt # Project dependencies
```

## Usage

### Creating Flash Cards
1. Open the Cards section from the sidebar
2. Click "Add New Card"
3. Fill in the question and answer
4. Select or create a category
5. Set initial difficulty (1-10)
6. Save the card

### Scheduling
- Global schedules affect all cards
- Category schedules override global settings
- Individual card schedules take highest precedence
- Three frequency modes available:
  - Times per week
  - Times per day (min-max)
  - Fixed intervals

### Import/Export
- CSV import with preview
- Support for partial imports
- Error logging for invalid entries
- Export all data with headers
- Backup/Restore functionality

## Testing

- Run all tests:
```bash
pytest
```

- Run with coverage:
```bash
pytest --cov=.
```

- Run specific test file:
```bash
pytest tests/test_specific.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests to ensure they pass
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PySide6](https://wiki.qt.io/Qt_for_Python)
- Database powered by [SQLAlchemy](https://www.sqlalchemy.org/)
- Testing with [pytest](https://docs.pytest.org/)

## Contact

Alfredo Calvimontes - [@YourTwitter](https://twitter.com/YourTwitter)

Project Link: [https://github.com/AlfredoCalvimontes/flash_cards_learning_app](https://github.com/AlfredoCalvimontes/flash_cards_learning_app)
