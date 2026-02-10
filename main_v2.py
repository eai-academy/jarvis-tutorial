"""
JARVIS - Full-Duplex com PyAudio + Pygame
Usa pygame para tocar áudio (interruptível a qualquer momento)
"""

import speech_recognition as sr
from openai import OpenAI
import pyttsx3
import os
import threading
import pyaudio
import pygame
import numpy as np
import time
import tempfile


from dotenv import load_dotenv

load_dotenv()

VELOCIDADE_FALA = 200
OPENAI_MODEL=os.getenv("OPENAI_MODEL", "gpt-4o-mini")
PAUSA_SILENCIO=1.2


LIMIAR_INTERRUPCAO = 1500  # Nível de áudio para detectar interrupção
TAXA_AMOSTRAGEM = 16000
TAMANHO_CHUNK = 1024

# Inicializa pygame mixer
pygame.mixer.init()


class JarvisFullDuplex:
    """JARVIS com verdadeiro full-duplex usando PyAudio + Pygame"""
    
    def __init__(self, chave_api):
        self.cliente = OpenAI(api_key=chave_api)
        self.reconhecedor = sr.Recognizer()
        

        # PyAudio para monitoramento em tempo real
        self.pyaudio = pyaudio.PyAudio()
        
        # Controle de estado
        self.falando = False
        self.interromper = threading.Event()
        self.executando = True
        
        # Buffer para gravar áudio durante a fala do JARVIS
        self.buffer_audio = []
        self.trava_audio = threading.Lock()
        self.comando_interrompido = None  # Guarda o comando que interrompeu
        
        # Configura reconhecimento
        self.reconhecedor.energy_threshold = 200
        self.reconhecedor.dynamic_energy_threshold = True
        self.reconhecedor.pause_threshold = PAUSA_SILENCIO
        
        print("🎤 JARVIS Full-Duplex inicializado!")
        print("=" * 50)

    
    def monitorar_audio(self):
        """Thread que monitora e GRAVA áudio em tempo real"""
        print("👂 Monitor de áudio iniciado")
        
        fluxo = self.pyaudio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=TAXA_AMOSTRAGEM,
            input=True,
            frames_per_buffer=TAMANHO_CHUNK
        )
        
        # Contador para evitar falsos positivos
        contagem_alta = 0
        CONTAGEM_MINIMA = 3
        
        # Gravação contínua
        gravando_interrupcao = False
        frames_interrupcao = []
        frames_silencio = 0
        FRAMES_SILENCIO_MAX = 30  # ~1.0s de silêncio para parar de gravar
        
        try:
            while self.executando:
                dados = fluxo.read(TAMANHO_CHUNK, exception_on_overflow=False)
                dados_audio = np.frombuffer(dados, dtype=np.int16)
                nivel = np.abs(dados_audio).mean()
                
                # Se JARVIS está falando
                if self.falando:
                    # Guarda todo áudio no buffer (para capturar interrupção)
                    with self.trava_audio:
                        self.buffer_audio.append(dados)
                        # Limita buffer a 5 segundos
                        max_frames = int(5 * TAXA_AMOSTRAGEM / TAMANHO_CHUNK)
                        if len(self.buffer_audio) > max_frames:
                            self.buffer_audio.pop(0)
                    
                    # Detecta interrupção
                    if nivel > LIMIAR_INTERRUPCAO:
                        contagem_alta += 1
                        if contagem_alta >= CONTAGEM_MINIMA and not self.interromper.is_set():
                            print(f"🛑 INTERRUPÇÃO! Nível: {nivel:.0f}")
                            self.interromper.set()
                            pygame.mixer.music.stop()
                            # Começa a gravar a frase de interrupção
                            gravando_interrupcao = True
                            frames_interrupcao = list(self.buffer_audio)  # Copia buffer
                    else:
                        contagem_alta = 0
                
                # Gravando a frase de interrupção após parar o JARVIS
                if gravando_interrupcao:
                    frames_interrupcao.append(dados)
                    
                    if nivel < LIMIAR_INTERRUPCAO / 2:
                        frames_silencio += 1
                    else:
                        frames_silencio = 0
                    
                    # Parou de falar? Processa!
                    if frames_silencio >= FRAMES_SILENCIO_MAX:
                        gravando_interrupcao = False
                        frames_silencio = 0
                        
                        # Converte para AudioData e reconhece
                        bytes_audio = b''.join(frames_interrupcao)
                        audio_sr = sr.AudioData(bytes_audio, TAXA_AMOSTRAGEM, 2)
                        
                        try:
                            texto = self.reconhecedor.recognize_google(audio_sr, language='pt-BR')
                            print(f"👤 Interrupção capturada: {texto}")
                            self.comando_interrompido = texto
                        except:
                            print("❓ Não entendi a interrupção")
                            self.comando_interrompido = None
                        
                        frames_interrupcao = []
                
                time.sleep(0.03)
                
        finally:
            fluxo.stop_stream()
            fluxo.close()
    
    def ouvir(self):
        """Captura comando de voz completo"""
        print("\n🎧 Fale seu comando...")
        
        mic = sr.Microphone()
        with mic as source:
            self.reconhecedor.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = self.reconhecedor.listen(source, timeout=10, phrase_time_limit=20)
                texto = self.reconhecedor.recognize_google(audio, language='pt-BR')
                print(f"👤 Você: {texto}")
                return texto
                
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                # Verifica se há interrupção capturada antes de dizer "não entendi"
                if not self.comando_interrompido:
                    print("❓ Não entendi...")
                return None
            except Exception as e:
                if not self.comando_interrompido:
                    print(f"❌ Erro: {e}")
                return None
    
    def pensar(self, comando):
        """Processa comando com OpenAI"""
        print("🤖 Processando...")
        
        try:
            resposta = self.cliente.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Você é JARVIS, assistente inteligente. Responda em português de forma concisa."},
                    {"role": "user", "content": comando}
                ],
                temperature=0.7
            )
            return resposta.choices[0].message.content
        except Exception as e:
            print(f"❌ Erro OpenAI: {e}")
            return "Desculpe, tive um problema técnico."
    
    def falar(self, texto):
        """Fala texto usando pygame (interruptível a qualquer momento)"""
        print(f"🔊 JARVIS: {texto}\n")
        
        self.falando = True
        self.interromper.clear()
        self.comando_interrompido = None
        
        # Limpa buffer de áudio
        with self.trava_audio:
            self.buffer_audio = []
        
        # Arquivo temporário para o áudio
        arquivo_audio = os.path.join(tempfile.gettempdir(), "jarvis_fala.wav")
        
        try:
            # 1. Gera áudio usando pyttsx3
            motor = pyttsx3.init('sapi5')
            
            vozes = motor.getProperty('voices')
            for voz in vozes:
                if 'brazil' in voz.name.lower() or 'portuguese' in voz.name.lower():
                    motor.setProperty('voice', voz.id)
                    break
            
            motor.setProperty('rate', VELOCIDADE_FALA)
            motor.setProperty('volume', 1.0)
            
            # Salva em arquivo ao invés de falar direto
            motor.save_to_file(texto, arquivo_audio)
            motor.runAndWait()
            motor.stop()
            del motor
            
            # Pequena pausa para garantir arquivo completo
            time.sleep(0.2)
            
            # 2. Toca com pygame (interruptível!)
            pygame.mixer.music.load(arquivo_audio)
            pygame.mixer.music.play()
            
            # 3. Aguarda terminar OU ser interrompido
            while pygame.mixer.music.get_busy():
                if self.interromper.is_set():
                    pygame.mixer.music.stop()
                    print("🛑 Fala interrompida!")
                    break
                time.sleep(0.05)
            
        except Exception as e:
            print(f"❌ Erro na fala: {e}")
        
        finally:
            self.falando = False
            # Limpa arquivo temporário
            try:
                if os.path.exists(arquivo_audio):
                    pygame.mixer.music.unload()
                    os.remove(arquivo_audio)
            except:
                pass
        
        # Se foi interrompido, aguarda o monitor processar o áudio
        if self.interromper.is_set():
            print("⏳ Processando comando de interrupção...")
            time.sleep(1.0)  # Aguarda monitor terminar de gravar e reconhecer
        
        return self.interromper.is_set()
    
    def executar(self):
        """Loop principal"""
        print("=" * 50)
        print("🤖 JARVIS - FULL-DUPLEX REAL")
        print("=" * 50)
        print("✨ Eu escuto ENQUANTO falo!")
        print("✨ Me interrompa falando a qualquer momento")
        print("✨ Diga 'sair' para encerrar")
        print("=" * 50)
        
        # Inicia monitor de áudio em thread separada (execução/processo separado)
        monitor = threading.Thread(target=self.monitorar_audio, daemon=True)
        monitor.start()
        
        time.sleep(1)  # Aguarda monitor iniciar
        
        while self.executando:
            # Verifica se há comando de interrupção já capturado
            if self.comando_interrompido:
                comando = self.comando_interrompido
                self.comando_interrompido = None
                print(f"🔄 Usando comando da interrupção: {comando}")
            else:
                # Escuta comando normalmente
                comando = self.ouvir()
            
            if not comando:
                continue
            
            # Verifica saída
            if any(p in comando.lower() for p in ['sair', 'desligar', 'tchau', 'encerrar']):
                self.falar("Até logo!")
                self.executando = False
                break
            
            # Processa e responde
            resposta = self.pensar(comando)
            foi_interrompido = self.falar(resposta)
            
            # Se foi interrompido, o comando já está em self.comando_interrompido
            # O loop vai pegar automaticamente na próxima iteração
        
        # Cleanup
        self.pyaudio.terminate()
        pygame.mixer.quit()
        print("\n👋 JARVIS encerrado!")


def main():
    chave_api = os.getenv("OPENAI_API_KEY")
    
    if not chave_api:
        print("⚠️ Configure OPENAI_API_KEY")
        chave_api = input("Cole sua chave: ").strip()
        if not chave_api:
            return
    
    try:
        jarvis = JarvisFullDuplex(chave_api)
        jarvis.executar()
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    main()
