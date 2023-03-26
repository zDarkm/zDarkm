from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube

# Configurações do Flask
app = Flask(__name__)

# Credenciais do Twilio
account_sid = 'AC48e73e164d56871e9d2d4b3926abf014'
auth_token = '10426e8d25a91728e6c3e39be0a2b60f'

# Credenciais do Spotify
spotify_client_id = '5a123c9e4dc3466182029bfbca6b97ae'
spotify_client_secret = '2e67eecb2f7d4e59bdcb69692b1800f6'

# Autenticação no Spotify
client_credentials_manager = SpotifyClientCredentials(
    client_id=spotify_client_id,
    client_secret=spotify_client_secret
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# URL da API do YouTube
youtube_api_url = "https://www.googleapis.com/youtube/v3/videos"

# Lista de usuários administradores
admins = ['+5551999995550']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    # Recebe a mensagem do WhatsApp e o número do remetente
    message = request.form['Body']
    sender = request.form['From']

    # Cria uma resposta do Twilio
    response = MessagingResponse()

    # Verifica se o remetente é um dos administradores
    if sender in admins:
        # Verifica o tipo de mensagem recebida
        if message == '/start':
            # Envia uma mensagem de boas-vindas para os administradores
            response.message("Olá! Você está autorizado a usar os comandos administrativos.")

        elif message.startswith('/broadcast '):
            # Envia uma mensagem para todos os usuários registrados no Twilio
            broadcast_message = message[11:]
            client = Client(account_sid, auth_token)
            for user in client.messages.list():
                from_number = user.from_[8:]
                response = MessagingResponse()
                response.message(f"Broadcast: {broadcast_message}")
                send_message(from_number, response)

        else:
            # Envia uma mensagem de erro quando receber um comando desconhecido
            response.message("Comando desconhecido. Use '/start' para iniciar ou '/broadcast mensagem' para enviar uma mensagem para todos os usuários registrados.")

    else:
        # Verifica o tipo de mensagem recebida
        if message.startswith('/spotify '):
            # Busca a música no Spotify
            query = message[9:]
            results = sp.search(q=query, limit=1)

            # Envia a informação da música encontrada para o usuário
            track_name = results['tracks']['items'][0]['name']
            artist_name = results['tracks']['items'][0]['artists'][0]['name']
            preview_url = results['tracks']['items'][0]['preview_url']
            response.message(f"Nome da música: {track_name}\nArtista: {artist_name}\nPreview: {preview_url}")

        elif message.startswith('/youtube '):
            # Faz o download do vídeo do YouTube
            video_url = message[9:]
            yt = YouTube(video_url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            stream.download('Downloads/')

            # Envia o arquivo baixado como resposta
            with open(f'{stream.default_filename}', 'rb') as file:
                response.message(media_url=file)

        else:
            # Envia uma mensagem padrão quando receber uma mensagem desconhecida
            response.message("Olá! Bem-vindo(a) ao meu chatbot. Para buscar uma música no Spotify, digite '/spotify nome_da_música'. Para fazer o download de um vídeo do YouTube, digite '/youtube URL_do_vídeo'.")

    return str(response)

def send_message(to_number, response):
    client = Client(account_sid, auth_token)
    message = client.messages.create(body=response, from_='whatsapp:+14155238886', to=f'whatsapp:{to_number}')
    return message

if __name__ == '__main__':
    app.run()
