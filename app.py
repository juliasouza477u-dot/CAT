import os
import random
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-dev')

database_url = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scores = db.relationship('Score', backref='user', lazy=True)


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)
    reference = db.Column(db.String(200), nullable=True)


QUESTIONS = [
    {
        "question_text": "De acordo com 1 Coríntios 12:4, o que existe em grande diversidade, mas provém do mesmo e único Espírito?",
        "option_a": "Os dons (carismas)",
        "option_b": "Os pecados",
        "option_c": "As igrejas",
        "correct_option": "A",
        "reference": "1 Coríntios 12:4"
    },
    {
        "question_text": "Segundo 1 Coríntios 12:5, há diversidade de ministérios, mas quem é o mesmo a quem todos servem?",
        "option_a": "O mesmo Senhor (Jesus Cristo)",
        "option_b": "O mesmo apóstolo",
        "option_c": "O mesmo anjo",
        "correct_option": "A",
        "reference": "1 Coríntios 12:5"
    },
    {
        "question_text": "No versículo 6, há diversidade de operações, mas quem opera tudo em todos?",
        "option_a": "O mesmo Deus (o Pai)",
        "option_b": "O mesmo homem",
        "option_c": "O mesmo demônio",
        "correct_option": "A",
        "reference": "1 Coríntios 12:6"
    },
    {
        "question_text": "De acordo com 1 Coríntios 12:7, para qual finalidade a manifestação do Espírito é dada a cada um?",
        "option_a": "Para o bem comum (edificar a comunidade)",
        "option_b": "Para se gabar diante dos outros",
        "option_c": "Para dominar a igreja",
        "correct_option": "A",
        "reference": "1 Coríntios 12:7"
    },
    {
        "question_text": "No versículo 8, qual é o primeiro dom específico mencionado que é dado pelo Espírito?",
        "option_a": "A palavra de sabedoria",
        "option_b": "A palavra de ciência",
        "option_c": "A fé",
        "correct_option": "A",
        "reference": "1 Coríntios 12:8"
    },
    {
        "question_text": "Ainda no versículo 8, qual dom aparece logo ao lado da palavra de sabedoria?",
        "option_a": "A palavra de ciência (ou conhecimento)",
        "option_b": "O dom de curas",
        "option_c": "O dom de milagres",
        "correct_option": "A",
        "reference": "1 Coríntios 12:8"
    },
    {
        "question_text": "Segundo o versículo 9, qual virtude/dom é concedido a outro pelo mesmo Espírito?",
        "option_a": "A fé",
        "option_b": "A riqueza",
        "option_c": "A sabedoria humana",
        "correct_option": "A",
        "reference": "1 Coríntios 12:9"
    },
    {
        "question_text": "No versículo 9, qual dom relacionado à restauração da saúde é concedido?",
        "option_a": "O dom de curas",
        "option_b": "O dom de profecia",
        "option_c": "O dom de línguas",
        "correct_option": "A",
        "reference": "1 Coríntios 12:9"
    },
    {
        "question_text": "No versículo 10, qual dom está associado à realização de sinais extraordinários?",
        "option_a": "O dom de operar milagres",
        "option_b": "O dom de ensinar",
        "option_c": "O dom de administrar",
        "correct_option": "A",
        "reference": "1 Coríntios 12:10"
    },
    {
        "question_text": "Ainda no versículo 10, qual dom consiste em proclamar a palavra inspirada por Deus?",
        "option_a": "O dom de profecia",
        "option_b": "O dom de discernimento",
        "option_c": "O dom de fé",
        "correct_option": "A",
        "reference": "1 Coríntios 12:10"
    },
    {
        "question_text": "Qual dom citado no versículo 10 dá a capacidade de reconhecer se uma inspiração vem de Deus ou não?",
        "option_a": "O dom de discernimento dos espíritos",
        "option_b": "O dom de sabedoria",
        "option_c": "O dom de curas",
        "correct_option": "A",
        "reference": "1 Coríntios 12:10"
    },
    {
        "question_text": "Ainda no versículo 10, qual é o dom ligado à oração e louvor em linguagem inspirada?",
        "option_a": "A diversidade (variedade) de línguas",
        "option_b": "O dom de ajuda",
        "option_c": "O dom de governo",
        "correct_option": "A",
        "reference": "1 Coríntios 12:10"
    },
    {
        "question_text": "Para completar o dom das línguas, qual dom o versículo 10 menciona em seguida?",
        "option_a": "A interpretação das línguas",
        "option_b": "O dom de profecia",
        "option_c": "O dom de fé",
        "correct_option": "A",
        "reference": "1 Coríntios 12:10"
    },
    {
        "question_text": "Conforme o versículo 11, quem realiza e distribui todas essas manifestações?",
        "option_a": "Um só e o mesmo Espírito Santo",
        "option_b": "O apóstolo Paulo",
        "option_c": "O próprio crente",
        "correct_option": "A",
        "reference": "1 Coríntios 12:11"
    },
    {
        "question_text": "Como o Espírito distribui os dons a cada pessoa, segundo o final do versículo 11?",
        "option_a": "A cada um em particular, como Ele quer",
        "option_b": "A todos de forma igual",
        "option_c": "Somente aos pastores",
        "correct_option": "A",
        "reference": "1 Coríntios 12:11"
    },
    {
        "question_text": "Segundo Lucas 1:39, qual foi a atitude de Maria logo após saber da gravidez de Isabel?",
        "option_a": "Pôs-se a caminho e foi apressadamente à região montanhosa",
        "option_b": "Ficou em casa esperando",
        "option_c": "Foi para o deserto",
        "correct_option": "A",
        "reference": "Lucas 1:39"
    },
    {
        "question_text": "De acordo com Lucas 1:40, em cuja casa Maria entrou e a quem ela saudou?",
        "option_a": "Entrou na casa de Zacarias e saudou Isabel",
        "option_b": "Entrou na casa de Herodes e saudou a rainha",
        "option_c": "Entrou na casa de Pilatos e saudou o soldado",
        "correct_option": "A",
        "reference": "Lucas 1:40"
    },
    {
        "question_text": "O que aconteceu com a criança no ventre de Isabel ao ouvir a saudação de Maria? (v. 41)",
        "option_a": "A criança estremeceu (pulou de alegria) em seu ventre",
        "option_b": "A criança chorou",
        "option_c": "A criança dormiu",
        "correct_option": "A",
        "reference": "Lucas 1:41"
    },
    {
        "question_text": "O que aconteceu com Isabel quando Maria a saudou? (v. 41)",
        "option_a": "Isabel ficou cheia do Espírito Santo",
        "option_b": "Isabel ficou com medo",
        "option_c": "Isabel ficou doente",
        "correct_option": "A",
        "reference": "Lucas 1:41"
    },
    {
        "question_text": "Com qual proclamação Isabel acolheu Maria em alta voz? (v. 42)",
        "option_a": "\"Bendita és tu entre as mulheres e bendito é o fruto do teu ventre!\"",
        "option_b": "\"Quem és tu?\"",
        "option_c": "\"Vá em paz\"",
        "correct_option": "A",
        "reference": "Lucas 1:42"
    },
    {
        "question_text": "Segundo Lucas 1:45, por que Maria é chamada de bem-aventurada?",
        "option_a": "Porque acreditou que se cumpririam as coisas ditas da parte do Senhor",
        "option_b": "Porque era rica",
        "option_c": "Porque era rainha",
        "correct_option": "A",
        "reference": "Lucas 1:45"
    },
    {
        "question_text": "Quem é a Mãe de Jesus?",
        "option_a": "Maria",
        "option_b": "Isabel",
        "option_c": "Marta",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Quantos apóstolos Jesus escolheu?",
        "option_a": "12",
        "option_b": "10",
        "option_c": "7",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Qual é o primeiro livro da Bíblia?",
        "option_a": "Gênesis",
        "option_b": "Êxodo",
        "option_c": "Salmos",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Em qual cidade Jesus nasceu?",
        "option_a": "Belém",
        "option_b": "Jerusalém",
        "option_c": "Nazaré",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Quem foi o primeiro Papa?",
        "option_a": "São Pedro",
        "option_b": "São Paulo",
        "option_c": "São João",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Qual sacramento lava o pecado original?",
        "option_a": "Batismo",
        "option_b": "Eucaristia",
        "option_c": "Confissão",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Qual é a oração que Jesus ensinou?",
        "option_a": "Pai-Nosso",
        "option_b": "Ave Maria",
        "option_c": "Credo",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Quem traiu Jesus?",
        "option_a": "Judas Iscariotes",
        "option_b": "Pedro",
        "option_c": "Pilatos",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Qual é o último livro da Bíblia?",
        "option_a": "Apocalipse",
        "option_b": "João",
        "option_c": "Atos",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Quem anunciou a Maria que ela seria Mãe de Deus?",
        "option_a": "Arcanjo Gabriel",
        "option_b": "Arcanjo Miguel",
        "option_c": "Arcanjo Rafael",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Quantos mandamentos existem?",
        "option_a": "Dez",
        "option_b": "Cinco",
        "option_c": "Sete",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "O que significa \"Amém\"?",
        "option_a": "Assim seja",
        "option_b": "Obrigado",
        "option_c": "Por favor",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Qual festa celebra a descida do Espírito Santo?",
        "option_a": "Pentecostes",
        "option_b": "Natal",
        "option_c": "Páscoa",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Quem foi o primeiro mártir cristão?",
        "option_a": "Santo Estêvão",
        "option_b": "São Paulo",
        "option_c": "São Pedro",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "O que é a Igreja?",
        "option_a": "Comunidade de fieis",
        "option_b": "Um prédio",
        "option_c": "Um objeto",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Quantos dias durou a Quaresma?",
        "option_a": "40",
        "option_b": "30",
        "option_c": "50",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Quem escreveu a maioria das cartas do Novo Testamento?",
        "option_a": "São Paulo",
        "option_b": "São João",
        "option_c": "São Pedro",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Qual é o dom de proclamar a palavra inspirada por Deus?",
        "option_a": "Profecia",
        "option_b": "Curar",
        "option_c": "Línguas",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "O que significa Eucaristia?",
        "option_a": "Ação de graças / Corpo e Sangue de Cristo",
        "option_b": "Lava pés",
        "option_c": "Oração",
        "correct_option": "A",
        "reference": "Catecismo"
    },
    {
        "question_text": "Quem distribui os dons espirituais conforme a Sua vontade?",
        "option_a": "O Espírito Santo",
        "option_b": "O anjo",
        "option_c": "O homem",
        "correct_option": "A",
        "reference": "Catecismo"
    },
]


def seed_database():
    with app.app_context():
        db.create_all()
        if Question.query.count() == 0:
            for q in QUESTIONS:
                db.session.add(Question(**q))
            db.session.commit()
            print(f"Banco seedado com {len(QUESTIONS)} perguntas.")


with app.app_context():
    seed_database()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')


@app.route('/api/question')
def api_question():
    q = Question.query.order_by(db.func.random()).first()
    if not q:
        return jsonify({"error": "Sem perguntas"}), 404
    return jsonify({
        "id": q.id,
        "question": q.question_text,
        "options": {
            "A": q.option_a,
            "B": q.option_b,
            "C": q.option_c,
        },
        "reference": q.reference
    })


@app.route('/api/check-answer', methods=['POST'])
def api_check_answer():
    data = request.get_json(force=True) or {}
    question_id = data.get('question_id')
    answer = data.get('answer')

    q = Question.query.get(question_id)
    if not q:
        return jsonify({"correct": False, "error": "Pergunta não encontrada"}), 404

    correct = (answer == q.correct_option)
    return jsonify({
        "correct": correct,
        "correct_option": q.correct_option,
        "reference": q.reference
    })


@app.route('/api/score', methods=['POST'])
def api_save_score():
    data = request.get_json(force=True) or {}
    username = (data.get('username') or 'Anônimo').strip()[:80]
    score = int(data.get('score') or 0)

    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        db.session.add(user)
        db.session.flush()

    new_score = Score(user_id=user.id, score=score)
    db.session.add(new_score)
    db.session.commit()

    return jsonify({"status": "ok", "saved_score": score})


@app.route('/api/leaderboard')
def api_leaderboard():
    rows = (
        db.session.query(User.username, db.func.max(Score.score).label('best'))
        .join(Score, Score.user_id == User.id)
        .group_by(User.id)
        .order_by(db.desc('best'))
        .limit(10)
        .all()
    )
    return jsonify([{"username": r[0], "best": r[1]} for r in rows])


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)