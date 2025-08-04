from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__, template_folder='templates')
app.secret_key = 'segredo'  # Chave usada pelo flash

# ✅ Conexão com o banco (local)
def get_conn():
    return psycopg2.connect(
        dbname='estacionamento',
        user='postgres',
        password='1221',
        host='localhost',
        port='5432'
    )

# ✅ Página principal (consulta de placas)
@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    if request.method == 'POST':
        placa = request.form['placa'].upper().replace('-', '').strip()
        print(f"Placa consultada: {placa}")
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                'SELECT nome, telefone, placa, modelo, cor FROM veiculos WHERE REPLACE(placa, \'-\', \'\') = %s',
                (placa,)
            )
            resultado = cur.fetchone()
            conn.close()
            print(f"Resultado: {resultado}")
            if not resultado:
                flash('Placa não encontrada.')
        except Exception as e:
            flash(f"Erro: {e}")
    return render_template('index.html', resultado=resultado)

# ✅ Página de cadastro de veículos
@app.route('/cadastros', methods=['GET', 'POST']) 
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        placa = request.form['placa'].upper().strip()
        telefone = request.form['telefone']
        modelo = request.form['modelo']
        cor = request.form['cor']

        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO veiculos (nome, placa, telefone, modelo, cor) VALUES (%s, %s, %s, %s, %s)',
                (nome, placa, telefone, modelo, cor)
            )
            conn.commit()
            conn.close()
            flash('Veículo cadastrado com sucesso.')
            return redirect(url_for('index'))

        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash('Essa placa já está cadastrada.')
        except Exception as e:  
            flash(f'Erro: {e}')
    return render_template('cadastro.html')

# ✅ Inicia o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
