"""
Jarvis - Versão 1.0
Mais simples impossível
"""

import speech_recognition as sr
import pyttsx3
from openai import OpenAI
import os 

from dotenv import load_dotenv
load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

VELOCIDADE_FALA = 200
PAUSA_SILENCIO = 1.2


class Jarvis:
    def __init__(self, chave):
        
        self.cliente = OpenAI(api_key=chave)
        self.reconhecedor = sr.Recognizer()
        self.microfone = sr.Microphone()

        self.reconhecedor.pause_threshold = PAUSA_SILENCIO

        print("Calibrar microfone... Por favor, aguarde.")
        with self.microfone as fonte:
            self.reconhecedor.adjust_for_ambient_noise(fonte, duration=2)
            print (f"Microfone calibrado com sucesso! Nível de ruído ambiente: {self.reconhecedor.energy_threshold}")

        print("✅ Finalizado a configuração do microfone.")
        

    def ouvir(self): 
        with self.microfone as fonte:
            print("\n🎙️ Ouvindo...")
            try:
            
                audio = self.reconhecedor.listen(fonte, timeout=10, phrase_time_limit=10)

                texto = self.reconhecedor.recognize_google(audio, language="pt-BR")
                print(f"Você disse: {texto}")
                return texto
            except sr.UnknownValueError:
                print("🤖 JARVIS não conseguiu entender o áudio.")
                return None
            except sr.RequestError as e:
                print(f"Erro ao se comunicar com o serviço de reconhecimento de fala: {e}")
                return None
        

    def pensar(self, texto):
        
        try: 
            reposta = self.cliente.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um assistente pessoal chamado JARVIS. Responda de forma clara e objetiva."},
                    {"role": "user", "content": texto}
                ]
            )
            texto_resposta = reposta.choices[0].message.content.strip()
            print(f"JARVIS: {texto_resposta}")
            return texto_resposta
        except Exception as e:
            print(f"Erro na OpenAI: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua solicitação."
    


    def falar(self, texto): 
        
        motor = None 
        try: 
            motor = pyttsx3.init()
            vozes = motor.getProperty('voices')
            for voz in vozes:
                if "brazil" in voz.name.lower() or "portuguese" in voz.name.lower():
                    motor.setProperty('voice', voz.id)
                    break
                
            motor.setProperty('rate', VELOCIDADE_FALA)

            motor.say(texto)
            motor.runAndWait()
            motor.stop()

        except Exception as e:
            print(f"Erro ao falar: {str(e)}")
        finally:
            if motor:
                try:
                    del motor 
                except:
                    pass      

    def executar(self): 
        print("="*60)
        print("\n🤖 JARVIS .. Inicializando..")
        print("="*60)
        print("\n🤖 Comandos: 'sair' ")
        print("="*60)

        while True: 
            texto = self.ouvir()

            if not texto: 
                continue
            
            if texto.lower() == "sair":
                print("\n🤖 JARVIS .. Desligando..")
                break

            resposta = self.pensar(texto)
            self.falar(resposta)
            print("="*60)

def main(): 
    chave = os.getenv("OPENAI_API_KEY")

    if not chave:
        print("A chave da API do OpenAI não foi encontrada. Por favor, defina a variável de ambiente OPENAI_API_KEY.")
        return
    
    try:
        jarvis = Jarvis(chave)
        jarvis.executar()

    except KeyboardInterrupt:
        print("\nJarvis Desligando!")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")


if __name__ == "__main__":
    main()