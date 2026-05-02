# Day Tracker

A simple yet elegant web application to track your daily tasks and monitor your consistency over time.

## Features

- ✅ Add and manage daily tasks
- 📝 Optional text fields for additional task details
- 📊 Track task completion progress
- 📈 View statistics and progress reports
- 🗑️ Delete tasks when no longer needed
- 📅 Navigate between dates
- 🎨 Beautiful, responsive UI

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS with gradients and animations

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/amaanshaik20/Consistency-Tracker.git
   cd Consistency-Tracker
   ```

2. Install dependencies:
   ```bash
   pip install flask
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Usage

- **Home**: Main dashboard with quick links
- **Add Tasks**: Create new tasks with optional text fields
- **Check Tasks**: Mark tasks as complete for specific dates
- **Stats**: View your progress and completion statistics

## Project Structure

```
Day Tracker/
├── app.py                 # Main Flask application
├── static/
│   └── style.css         # Application styling
├── templates/
│   ├── home.html         # Home page
│   ├── add_task.html     # Add task page
│   ├── check_tasks.html  # Task completion page
│   └── stats.html        # Statistics page
└── README.md             # This file
```

## Features in Detail

### Task Management
- Create tasks with custom names
- Enable optional text fields for detailed information
- Delete tasks when they're no longer needed
- View all existing tasks

### Progress Tracking
- Check off completed tasks for each day
- Track completion dates
- View completion history
- See statistics across different time periods

### Responsive Design
- Works on desktop, tablet, and mobile devices
- Beautiful gradient UI with smooth animations
- Intuitive navigation

## License

This project is open source and available for personal use.
