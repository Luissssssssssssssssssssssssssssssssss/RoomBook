from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3
import os
import traceback

app = Flask(__name__)
app.secret_key = "chave_secreta"

# ================== BANCO ==================
def conectar():
    return sqlite3.connect("database.db")

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            senha TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reunioes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sala TEXT,
            data TEXT,
            horario TEXT,
            organizador TEXT
        )
    """)

    cursor.execute("SELECT * FROM usuarios WHERE usuario='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO usuarios (usuario, senha) VALUES (?,?)",
            ("admin", "admin")
        )

    conn.commit()
    conn.close()

criar_tabelas()

# ================== LOGIN ==================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE usuario=? AND senha=?",
            (usuario, senha)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["usuario"] = usuario
            return redirect(url_for("dashboard"))

        return render_template("index.html", erro="Usuário ou senha inválidos")

    return render_template("index.html")

# ================== CADASTRO ==================
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        try:
            usuario = request.form.get("usuario", "").strip()
            senha = request.form.get("senha", "").strip()

            if not usuario or not senha:
                return render_template("cadastro.html", erro="Preencha todos os campos")

            if usuario.lower() == "admin":
                return render_template("cadastro.html", erro="Usuário não permitido")

            conn = conectar()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
                (usuario, senha)
            )
            conn.commit()
            conn.close()

            return redirect(url_for("index"))

        except sqlite3.IntegrityError:
            return render_template("cadastro.html", erro="Usuário já existe")

        except Exception as e:
            # LOG REAL DO ERRO (aparece no terminal)
            print("ERRO NO CADASTRO:")
            traceback.print_exc()
            return render_template("cadastro.html", erro="Erro interno ao criar conta")

    return render_template("cadastro.html")

# ================== DASHBOARD ==================
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("index"))

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT sala, data, horario, organizador FROM reunioes")
    reunioes = cursor.fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        usuario=session["usuario"],
        reunioes=reunioes
    )

# ================== AGENDAR ==================
@app.route("/agendar", methods=["POST"])
def agendar():
    if "usuario" not in session:
        return jsonify({"erro": "não autorizado"}), 403

    sala = request.form.get("sala")
    data = request.form.get("data")
    horario = request.form.get("horario")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM reunioes
        WHERE sala=? AND data=? AND horario=?
    """, (sala, data, horario))

    if cursor.fetchone():
        conn.close()
        return jsonify({"erro": "ocupado"}), 409

    cursor.execute("""
        INSERT INTO reunioes (sala, data, horario, organizador)
        VALUES (?,?,?,?)
    """, (sala, data, horario, session["usuario"]))

    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# ================== CANCELAR (ADMIN) ==================
@app.route("/cancelar", methods=["POST"])
def cancelar():
    if session.get("usuario") != "admin":
        return jsonify({"erro": "proibido"}), 403

    sala = request.form.get("sala")
    data = request.form.get("data")
    horario = request.form.get("horario")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM reunioes
        WHERE sala=? AND data=? AND horario=?
    """, (sala, data, horario))
    conn.commit()
    conn.close()

    return jsonify({"ok": True})

# ================== LOGOUT ==================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ================== ERROS (SEGUROS) ==================
@app.errorhandler(404)
def pagina_nao_encontrada(e):
    if os.path.exists("templates/404.html"):
        return render_template("404.html"), 404
    return "Página não encontrada", 404

@app.errorhandler(500)
def erro_interno(e):
    print("ERRO 500:")
    traceback.print_exc()
    if os.path.exists("templates/500.html"):
        return render_template("500.html"), 500
    return "Erro interno do servidor", 500

# ================== EXECUÇÃO ==================
if __name__ == "__main__":
    # Durante desenvolvimento → deixe True
    app.run(host="172.16.78.173", port=5000, debug=True)
