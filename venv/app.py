from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import os
from dotenv import load_dotenv
from collections import defaultdict
from datetime import date
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key')

# درست کردن مسیر دیتابیس
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "tasks.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ====================== Models ======================
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, default=date.today)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ایجاد پوشه instance و دیتابیس
if not os.path.exists('instance'):
    os.makedirs('instance')

with app.app_context():
    db.create_all()

# ====================== Routes ======================
@app.route('/')
def index():
    today = date.today()
    tasks = Task.query.filter_by(date=today).order_by(Task.created_at.desc()).all()
    return render_template('index.html', tasks=tasks, today=today)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    desc = request.form.get('description', '').strip()
    if title:
        task = Task(title=title.strip(), description=desc if desc else None)
        db.session.add(task)
        db.session.commit()
        flash('✅ تسک با موفقیت اضافه شد!', 'success')
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.is_completed = not task.is_completed
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('🗑️ تسک حذف شد.', 'danger')
    return redirect(url_for('index'))



@app.route('/history')
def history():
    all_tasks = Task.query.order_by(Task.date.desc(), Task.created_at.desc()).all()
    
    # گروه‌بندی تسک‌ها بر اساس روز
    grouped = defaultdict(list)
    for task in all_tasks:
        grouped[task.date].append(task)
    
    # آماده‌سازی داده برای نمودار - همه روزهایی که تسک دارند
    dates = []
    completed = []
    not_completed = []
    
    # مرتب‌سازی روزهای موجود از جدید به قدیمی
    for day in sorted(grouped.keys(), reverse=True):
        day_tasks = grouped[day]
        dates.append(day.strftime('%Y-%m-%d'))
        completed.append(len([t for t in day_tasks if t.is_completed]))
        not_completed.append(len([t for t in day_tasks if not t.is_completed]))
    
    return render_template('history.html', 
                         grouped_tasks=grouped,
                         dates=dates,
                         completed=completed,
                         not_completed=not_completed)

if __name__ == '__main__':
    app.run(debug=True)