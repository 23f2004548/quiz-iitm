from app import create_app
from app.models import db, Question, QuestionOption, User
from werkzeug.security import generate_password_hash

app = create_app()

def seed_database():
    with app.app_context():
        # Clear existing tables to prevent duplicate seed data
        db.session.query(QuestionOption).delete()
        db.session.query(Question).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        print("Cleared existing tables.")
        
        # 1. Create a dummy test user
        dummy_user = User(
            username="studious_coder",
            email="learner@iitm.ac.in",
            password_hash=generate_password_hash("password123"),
            xp=150,
            level=2,
            streak=4
        )
        db.session.add(dummy_user)
        
        # 2. Add Linux Command Questions
        # COMMAND QUESTION 1
        q1 = Question(
            type="COMMAND",
            difficulty="Easy",
            subject="Linux System Commands",
            topic="Basic Commands",
            prompt="Write a command to create a directory named 'assignment1' in your current working directory.",
            answer="mkdir assignment1",
            explanation="The command 'mkdir' stands for 'make directory'. Appending 'assignment1' creates a directory of that name.",
            week=1,
            tags="commands,mkdir,directory"
        )
        db.session.add(q1)
        
        # COMMAND QUESTION 2
        q2 = Question(
            type="COMMAND",
            difficulty="Medium",
            subject="Linux System Commands",
            topic="Basic Commands",
            prompt="Write a single command to list all files in the current directory, including hidden ones, in a long listing format.",
            answer="ls -la || ls -al || ls -a -l || ls -l -a",
            explanation="The 'ls' command lists files. The '-a' flag includes hidden files (dotfiles), and '-l' displays long details (permissions, size, owner).",
            week=1,
            tags="commands,ls,listing"
        )
        db.session.add(q2)
        
        # COMMAND QUESTION 3
        q3 = Question(
            type="COMMAND",
            difficulty="Medium",
            subject="Linux System Commands",
            topic="Basic Commands",
            prompt="Write a command to count the number of lines in a file named 'syslog.log'.",
            answer="wc -l syslog.log",
            explanation="'wc' stands for word count. The '-l' option counts and prints the number of newline characters (lines) in the specified file.",
            week=1,
            tags="commands,wc,filters"
        )
        db.session.add(q3)

        # MCQ QUESTION 1
        q4 = Question(
            type="MCQ",
            difficulty="Easy",
            subject="Linux System Commands",
            topic="Basic Commands",
            prompt="Which command is used to display the first 10 lines of a text file?",
            answer="head",
            explanation="The 'head' command displays the beginning of a file. By default, it outputs the first 10 lines. You can use 'head -n 5' for the first 5 lines.",
            week=1,
            tags="commands,head,file"
        )
        db.session.add(q4)
        db.session.flush() # Flush to get q4.id
        
        opts4 = [
            QuestionOption(question_id=q4.id, option_text="cat"),
            QuestionOption(question_id=q4.id, option_text="tail"),
            QuestionOption(question_id=q4.id, option_text="head", is_correct=True),
            QuestionOption(question_id=q4.id, option_text="less")
        ]
        db.session.add_all(opts4)
        
        # MCQ QUESTION 2 (Git)
        q5 = Question(
            type="MCQ",
            difficulty="Medium",
            subject="Git & GitHub",
            topic="Branching & Merging",
            prompt="Which Git command is used to show a list of all local and remote branches in your repository?",
            answer="git branch -a",
            explanation="'git branch' lists local branches. The '-a' (all) flag expands the list to include remote-tracking branches fetched from github/gitlab.",
            week=2,
            tags="git,branching"
        )
        db.session.add(q5)
        db.session.flush()
        
        opts5 = [
            QuestionOption(question_id=q5.id, option_text="git branch"),
            QuestionOption(question_id=q5.id, option_text="git branch -r"),
            QuestionOption(question_id=q5.id, option_text="git branch -a", is_correct=True),
            QuestionOption(question_id=q5.id, option_text="git remote show")
        ]
        db.session.add_all(opts5)
        
        # NAT QUESTION 1 (Python)
        q6 = Question(
            type="NAT",
            difficulty="Medium",
            subject="Python",
            topic="Data Structures",
            prompt="What is the output of the following Python code snippet?\n\n```python\nnums = [1, 2, 3, 4, 5, 2, 3]\nunique_nums = set(nums)\nprint(len(unique_nums))\n```",
            answer="5",
            explanation="A Python 'set' contains only unique values. Converting the list `[1, 2, 3, 4, 5, 2, 3]` to a set results in `{1, 2, 3, 4, 5}`. The length of this set is 5.",
            week=3,
            tags="python,set"
        )
        db.session.add(q6)
        
        # NAT QUESTION 2 (SQL)
        q7 = Question(
            type="NAT",
            difficulty="Hard",
            subject="SQL",
            topic="Aggregations",
            prompt="Consider a table `orders` with a column `amount` containing values: 100, 200, NULL, 300, 400. What value does `SELECT AVG(amount) FROM orders` evaluate to?",
            answer="250",
            explanation="SQL aggregate functions like `AVG` ignore NULL values entirely. The average is computed on the non-NULL rows: (100 + 200 + 300 + 400) / 4 = 1000 / 4 = 250.",
            week=4,
            tags="sql,aggregation"
        )
        db.session.add(q7)
        
        # MCQ QUESTION 3 (IITM BS Computational Thinking)
        q8 = Question(
            type="MCQ",
            difficulty="Hard",
            subject="IITM BS Degree Subjects",
            topic="Computational Thinking",
            prompt="In a flowchart, what symbol is standard for showing a decision or condition checking?",
            answer="Diamond",
            explanation="In standard flowchart symbols, rectangles denote processing steps, diamonds denote decisions/conditionals, and ovals denote start/end terminals.",
            week=5,
            tags="computational-thinking,flowchart"
        )
        db.session.add(q8)
        db.session.flush()
        
        opts8 = [
            QuestionOption(question_id=q8.id, option_text="Rectangle"),
            QuestionOption(question_id=q8.id, option_text="Parallelogram"),
            QuestionOption(question_id=q8.id, option_text="Diamond", is_correct=True),
            QuestionOption(question_id=q8.id, option_text="Oval")
        ]
        db.session.add_all(opts8)

        # MCQ QUESTION 4 (NPTEL ML)
        q9 = Question(
            type="MCQ",
            difficulty="Expert",
            subject="Machine Learning",
            topic="Regularization",
            prompt="Which loss function regularization method forces some feature coefficients to become exactly zero, yielding sparse models?",
            answer="L1 Regularization (Lasso)",
            explanation="L1 regularization (Lasso) adds an absolute penalty on coefficient values. Due to its geometry, it forces coefficients to exactly zero, performing feature selection.",
            week=6,
            tags="machine-learning,regularization"
        )
        db.session.add(q9)
        db.session.flush()
        
        opts9 = [
            QuestionOption(question_id=q9.id, option_text="L2 Regularization (Ridge)"),
            QuestionOption(question_id=q9.id, option_text="L1 Regularization (Lasso)", is_correct=True),
            QuestionOption(question_id=q9.id, option_text="Elastic Net"),
            QuestionOption(question_id=q9.id, option_text="Dropout")
        ]
        db.session.add_all(opts9)
        
        # Ingest JSON question files
        import json
        import os
        from app.utils.ingester import validate_and_ingest_questions
        
        json_files = [
            (os.path.join("questions", "linux", "week1.json"), "Linux System Commands", "Week 1 Overview", 1),
            (os.path.join("questions", "linux", "week2.json"), "Linux System Commands", "Week 2 Overview", 2),
            (os.path.join("questions", "linux", "week3.json"), "Linux System Commands", "Week 3 Overview", 3),
            (os.path.join("questions", "linux", "week4.json"), "Linux System Commands", "Week 4 Overview", 4),
            (os.path.join("questions", "linux", "week5.json"), "Linux System Commands", "Week 5 Overview", 5)
        ]
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for filename, subject, default_topic, week in json_files:
            file_path = os.path.join(base_dir, filename)
            if os.path.exists(file_path):
                print(f"Loading questions from {filename}...")
                with open(file_path, "r", encoding="utf-8") as f:
                    q_list = json.load(f)
                imported, skipped = validate_and_ingest_questions(
                    q_list, 
                    default_subject=subject, 
                    default_topic=default_topic,
                    default_week=week
                )
                print(f"  - Imported {imported}, skipped {skipped}")
            else:
                print(f"Warning: JSON file {filename} not found.")

        db.session.commit()
        print("Database seeded successfully with all question banks.")

if __name__ == '__main__':
    seed_database()
