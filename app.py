from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション用に必ず設定

def generate_question(operation, difficulty):
    if operation == 'multiply' and difficulty == 'medium':
        num1 = random.randint(1, 9)
        num2 = random.randint(10, 99)
    else:
        if difficulty == 'easy':
            low, high = 1, 10
        elif difficulty == 'medium':
            low, high = 10, 50
        else:
            low, high = 50, 100
        num1 = random.randint(low, high)
        num2 = random.randint(low, high)

    if operation == 'add':
        symbol = '+'
        correct_answer = num1 + num2
    elif operation == 'subtract':
        symbol = '-'
        if num1 < num2:
            num1, num2 = num2, num1
        correct_answer = num1 - num2
    elif operation == 'multiply':
        symbol = '×'
        correct_answer = num1 * num2
    else:  # divide
        symbol = '÷'
        correct_answer = num1
        num1 = num1 * num2

    return num1, symbol, num2, correct_answer

@app.route('/')
def index():
    return render_template(
        'index.html',
        operation=session.get('operation', ''),
        difficulty=session.get('difficulty', ''),
        question_count=session.get('question_count', '')
    )

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    session['operation'] = request.form['operation']
    session['difficulty'] = request.form['difficulty']
    session['question_count'] = int(request.form['question_count'])
    session['current_question'] = 1
    session['score'] = 0
    return redirect(url_for('quiz'))

@app.route('/quiz')
def quiz():
    if 'current_question' not in session:
        return redirect(url_for('index'))

    operation = session['operation']
    difficulty = session['difficulty']
    num1, symbol, num2, correct_answer = generate_question(operation, difficulty)

    return render_template(
        'quiz.html',
        num1=num1,
        symbol=symbol,
        num2=num2,
        correct_answer=correct_answer,
        current=session['current_question'],
        total=session['question_count'],
        result=None  # 初回なので結果はなし
    )

@app.route('/check_answer', methods=['POST'])
def check_answer():
    if 'current_question' not in session:
        return redirect(url_for('index'))

    try:
        user_answer = int(request.form['user_answer'].translate(str.maketrans('０１２３４５６７８９', '0123456789')))
        correct_answer = int(request.form['correct_answer'])
    except ValueError:
        return "<h2>数値を入力してください！</h2>"

    if user_answer == correct_answer:
        session['score'] += 1
        result = "正解！🎉"
    else:
        result = f"不正解。正解は {correct_answer} でした。"

    if session['current_question'] == session['question_count']:
        score = session['score']
        total = session['question_count']
        session.clear()
        return render_template('final_result.html', result=result, score=score, total=total)

    session['current_question'] += 1
    operation = session['operation']
    difficulty = session['difficulty']
    num1, symbol, num2, next_correct_answer = generate_question(operation, difficulty)

    return render_template(
        'quiz.html',
        num1=num1,
        symbol=symbol,
        num2=num2,
        correct_answer=next_correct_answer,
        current=session['current_question'],
        total=session['question_count'],
        result=result  # 前回の結果を表示
    )

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
