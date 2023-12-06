from flet import *
import base64
import cv2
import os
from fer import FER
import time
import random as rand
cap = cv2.VideoCapture(0)
    
class Camera(UserControl):
    def __init__(self):
        super().__init__()
        global captura   
        captura = False
        
        global angry, happy, sad, surprised, neutral
        angry = False
        happy = False
        sad = False
        surprised = False
        neutral = False
        
    def did_mount(self):
        self.update_timer()
        
    def screenshot(self):
        global captura
        captura = True
    
    def angry_true(self):
        global angry
        angry = True
        
    def happy_true(self):
        global happy
        happy = True
        
    def sad_true(self):
        global sad
        sad = True
    
    def neutral_true(self):
        global neutral
        neutral = True
        
    def surprised_true(self):
        global surprised
        surprised = True
        
    def update_timer(self):
        #Fer
        emotions = ["angry", "happy", "sad", "surprised","neutral"]
        emotions_overlays = [cv2.imread(f'images/{emotion}_overlay.png', -1) for emotion in emotions] 
        detector = FER()
        
        #Timer
        display_time = 20  # segundos
        display_timer_start = 0
        
        try:
            while True:
                _, frame = cap.read()
                
                #FER 
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                #Detection de mas de una cara 
                faces = detector.detect_emotions(frame)

                for face in faces:
                    x, y, w, h = face["box"]

                    emotion_text = face["emotions"]
                    max_emotion = max(emotion_text, key=emotion_text.get)

                    if max_emotion in emotions:
                        emotion_index = emotions.index(max_emotion)
                        overlay = emotions_overlays[emotion_index]

                        overlay = cv2.resize(overlay, (w // 2, h // 2))

                        overlay_x = x + w // 4
                        overlay_y = y - int(h * 0.3)

                        overlay_x = max(overlay_x, 0)
                        overlay_y = max(overlay_y, 0)
     
                        overlay_h, overlay_w, _ = overlay.shape
                        if overlay_x + overlay_w > frame.shape[1]:
                            overlay_w = frame.shape[1] - overlay_x
                            overlay = overlay[:, :overlay_w]

                        for c in range(0, 3):
                            frame[overlay_y:overlay_y + overlay_h, overlay_x:overlay_x + overlay_w, c] = frame[overlay_y:overlay_y + overlay_h, overlay_x:overlay_x + overlay_w, c] * (1 - overlay[:, :, 3] / 255.0) + overlay[:, :, c] * (overlay[:, :, 3] / 255.0)

                        
                        """ for emotion, prob in emotion_text.items():
                            print(f"{emotion}: {prob}") """

                        #Detector de emociones
                        global angry, happy, sad, surprised, neutral
                        if max_emotion == "angry":
                            Camera.angry_true(self)
                        else:
                            angry = False
                            
                        if max_emotion == "happy":
                            Camera.happy_true(self)
                        else:
                            happy = False
                            
                        if max_emotion == "sad":
                            Camera.sad_true(self)
                        else:
                            sad = False
                            
                        if max_emotion == "surprised":
                            Camera.surprised_true(self)
                        else:
                            surprised = False
                            
                        if max_emotion == "neutral":
                            Camera.neutral_true(self)
                        else: 
                            neutral = False
     
                        display_timer_start = time.time()
            
                if time.time() - display_timer_start >= display_time:
                    display_timer_start = 0
                
                # Screenshots Module
                folder_path = "screenshots"
                img_list = os.listdir(folder_path)
                index = 0  
                if img_list:
                    for i in img_list:
                        index+=1
                
                global captura 
                if captura == True:
                    img_name = f"img_{index}.jpg"
                    cv2.imwrite(f"screenshots/{img_name}",frame)
                    captura = False
                
                # Frame Encoding para flet
                _,im_arr = cv2.imencode(".png",frame)
                im_b64 = base64.b64encode(im_arr)
                self.img.src_base64 = im_b64.decode("utf-8")
                self.update()
                
        except Exception as e:
            print(e)
                
    def build(self):
        self.img = Image(
            border_radius=border_radius.all(20)
        )
        return Column([
            self.img,
        ])

def main (page: Page):  
    page.title = "FeelSnap"
    page.theme_mode = ThemeMode.LIGHT
    page.padding = 10
    
    camera = Camera()
    
    def screenshot(e):
        camera.screenshot()
        
        dlg = AlertDialog(title=Text("Foto Guardada!"))
        page.dialog = dlg
        dlg.open = True
        
        page.update()      
    
    #Routes
    def route_change(e):
        page.views.clear()
        page.views.append(
            View(
                "/",
                [
                    #Widgets
                    Container(content=Image(
                        src=f"images/logo.png",
                        width=450,
                        height=450,
                        fit= ImageFit.CONTAIN),
                        padding=25,
                        alignment= alignment.top_center
                        ),
                    
                    Container(content= ElevatedButton(
                        content=Text("Iniciar", font_family="montserrat"),
                        width=130,
                        height=50,
                        bgcolor='blue',
                        color='white',
                        on_click= open_menu),
                        alignment= alignment.center
                        ),
                ],
            )
        )
        if page.route == "/menu":
            page.views.append(
                View(
                    "/menu",
                    [
                        AppBar(title=Text("Menú",size=40, font_family="montserrat"), bgcolor=colors.SURFACE_VARIANT),
                        Row(controls=[
                            TextButton(content=
                                    Container(content=
                                                Column(
                                                    [
                                                        Image(src="images/camera.png",fit=ImageFit.CONTAIN,width=300,height=300),
                                                        Container(content=Text("Cámara", size=40,text_align=TextAlign.CENTER,width=300,font_family="montserrat",color=colors.BLACK)),
                                                    ],
                                                    spacing=5
                                                ),
                                                alignment=alignment.center
                                            ),
                                    on_click=open_camera
                                    ),
                           TextButton(content=
                                    Container(content=
                                                Column(
                                                    [
                                                        Image(src="images/picture.png",width=300,height=300),
                                                        Container(content=Text("Galería", size=40,text_align=TextAlign.CENTER,width=300,font_family="montserrat",color=colors.BLACK)),  
                                                    ],
                                                    spacing=5
                                                )
                                            ),
                                    on_click=open_gallery 
                                    ),
                            TextButton(content=
                                    Container(content=
                                                Column(
                                                    [
                                                        Image(src="images/information.png",width=300,height=300),
                                                        Container(content=Text("Información", size=40,text_align=TextAlign.CENTER,width=300,font_family="montserrat",color=colors.BLACK)),
                                                    ],
                                                    spacing=5
                                                )
                                            ),
                                    on_click=open_information 
                                    )
                        ],
                        alignment=MainAxisAlignment.SPACE_AROUND,
                        spacing=10
                        ),

                    ]

                )
            )
        if page.route == "/menu/cam":
            global t
            t = Text("",size=14, font_family="montserrat",text_align=TextAlign.NONE, color=colors.WHITE)

            page.views.append(
            View(
                "/menu/cam",
                [
                    AppBar(title= Text("FeelSnap",size=40, font_family="montserrat"), bgcolor= colors.SURFACE_VARIANT),
                    Column(controls=[
                                        Row(controls=[
                                                        Column([
                                                                Container(content= Camera()),
                                                                Container(content= ElevatedButton(content=Text("CAPTURA EL MOMENTO! 📷", font_family="montserrat", size=16), width=600,height=40,bgcolor='#3188fb', color='white', on_click= screenshot),
                                                                        alignment=alignment.center
                                                                        )   
                                                                ],
                                                            spacing=40
                                                            ),
                                                        
                                                        Column([
                                                                Container(Stack(
                                                                    [
                                                                        Container(content=Text("Hola soy FeelSnap, quieres un consejo?", size=26,text_align=TextAlign.CENTER, font_family="montserrat", color=colors.WHITE),bgcolor="#3188fb", width=300, height=80, border_radius=15,left=38),
                                                                        Container(content=t, bgcolor="#3188fb", width=350, height=370, border_radius=15,left=15,top=100, border=border.all(15,"#3188fb")),
                                                                    ]
                                                                    ),
                                                                bgcolor='#f0f0f0', border_radius=30, width=400, height=500, padding=10),
                                                                
                                                                Container(content=ElevatedButton(content=Text("Quiero un consejo", font_family="montserrat"), bgcolor="#3188fb", color='white',on_click=consejo, width=250)),
                                                                ],
                                                            ),
                                                        ],
                                            spacing=120,
                                            alignment=MainAxisAlignment.CENTER
                                            ),
                                    ]
                        ),
                ]
            )
        )
        page.update()
        
        if page.route == "/menu/gallery":
            
            images = GridView(
                expand=1,
                runs_count=5,
                max_extent=300,
                child_aspect_ratio=1.0,
                spacing=5,
                run_spacing=5,
            )
            
            for i in range(0, 100):
                images.controls.append(
                    Image(
                    src=f"screenshots\img_{i}.jpg",
                    fit=ImageFit.CONTAIN,
                    repeat=ImageRepeat.NO_REPEAT,
                    border_radius=border_radius.all(5),
                    )
                )
                
            page.views.append(
                View(
                    "/menu/gallery",
                    [
                       AppBar(title= Text("Galería de fotos", size=40, font_family="montserrat"), bgcolor= colors.SURFACE_VARIANT),
                       images 
                    ]
                )
            )
        page.update()
        
        if page.route == "/menu/informacion":
            
            cl = Column(
            spacing=10,
            height=570,
            width=float("inf"),
            scroll=ScrollMode.ALWAYS,
            )
            
            cl.controls.append(Text("¡Alguna vez te has preguntado qué emociones expresan las caras de las personas en tus fotos? Nuestra aplicación te permite descubrirlo en un instante.💥💥\n",font_family="montserrat",size=22))
            cl.controls.append(Text("Simplemente colócate frente a la cámara y, en cuestión de segundos, te mostraremos la emoción que estás experimentando en ese momento. Nuestra aplicación reconoce 5 emociones:\n   😄 Felicidad 😄\n   😡 Enojo 😡\n   😟 Tristeza 😟\n   😱 Asombro 😱\n   😐 Neutro 😐\n",font_family="montserrat",size=22))
            cl.controls.append(Text("Cámara📷:\nCaptura esos momentos especiales con solo presionar el botón 'Captura el momento!'.\n",font_family="montserrat",size=22))
            cl.controls.append(Text("Consejos📣:\nSi deseas recibir un consejo relacionado con la emoción que estás sintiendo en ese momento, simplemente pulsa el botón 'Quiero un consejo'. Te proporcionaremos una descripción con un consejo útil. ¡Es muy sencillo!\n",font_family="montserrat",size=22))
            cl.controls.append(Text("Galería👓:\nAdemás, puedes capturar y guardar esos momentos en nuestra Galería. Así podrás revisarlos más tarde para comprender mejor tus reacciones en diferentes situaciones o para observar cómo se sienten y lucen tus amigos.\n",font_family="montserrat",size=22))
            cl.controls.append(Text("Ya sea que desees entender mejor tus propias emociones o las de tus amigos en las fotos de tus últimas aventuras, nuestra aplicación está aquí para ayudarte.¡No esperes más para explorar el mundo de las emociones a través de las imágenes! ¡Descarga la aplicación y comienza a descubrirlo hoy mismo!🚀🚀🚀\n",font_family="montserrat",size=22))
            

            page.views.append(
                View(
                    "/menu/informacion",
                    [
                       AppBar(title= Text("Información", size=40, font_family="montserrat"), bgcolor= colors.SURFACE_VARIANT),
                       Container(cl, bgcolor=colors.SURFACE_VARIANT,border=border.all(15,colors.SURFACE_VARIANT), border_radius=15),
                    ]
                )
            )
        page.update()

    def consejo(e):
        global csj
        global texto
        
        if angry:
            n = rand.randint(1,2)
            if n == 1:
                t.value = "Parece que estás sintiendo 😡 ENOJO 😡\n\nEl enojo es una emoción natural y común, pero debes saber cómo gestionarlo de manera saludable.\n\n💡 Respira profundamente: Practica la respiración profunda para calmarte. Inhala lenta y profundamente a través de la nariz y exhala suavemente por la boca. Esto puede ayudarte a reducir la intensidad del enojo.\n\n💡 Toma un descanso: Si te sientes abrumado por el enojo, da un paso atrás y toma un descanso."
                t.update()
                
            elif n == 2:
                t.value = "Parece que estás sintiendo 😡 ENOJO 😡\n\n💡 Reconoce y acepta tu enojo: Reconoce que estás enojado y acepta tus sentimientos. No te juzgues a ti mismo por sentir enojo.\n\n💡 Encuentra formas saludables de liberar la energía: Hacer ejercicio, como correr o nadar, puede ayudar a liberar la energía acumulada debido al enojo. La actividad física también libera endorfinas, lo que puede mejorar tu estado de ánimo."
                t.update()
                
        elif happy:
            n = rand.randint(1,2)
            if n == 1:
                t.value = "Me alegra verte tan 😄 FELIZ 😄\n\n💡 Disfruta de cada momento de felicidad: Cuando estás feliz, es importante aprovechar y disfrutar de esa emoción positiva.\n\n💡 Celebra tus logros: Cuando alcanzas un logro personal que te llena de felicidad, es importante reconocer tu esfuerzo y celebrar tus éxitos. Esto fortalece tu autoestima y te motiva a seguir trabajando en tus metas."
                t.update()
                
            elif n == 2:
                t.value = "Me alegra verte tan 😄 FELIZ 😄\n\n💡 Crea recuerdos: Los momentos felices son preciosos y efímeros. Aprovecha la oportunidad de crear recuerdos que puedas atesorar en el futuro. Puedes tomar fotos para capturar esos momentos, llevar un diario de tus experiencias o simplemente disfrutar del presente plenamente para que queden grabados en tu memoria.\n\n💡 Haz actos de bondad: Compartir tu felicidad a través de actos de bondad es una manera maravillosa de esparcir la alegría."
                t.update()
            
        elif sad:
            n = rand.randint(1,2)
            if n == 1:
                t.value = "Puedo notar que estas 😟 TRISTE 😟\n\nEs importante cuidarte y buscar formas de afrontar y superar esta emoción.\n\n💡 Habla con alguien de confianza: Compartir tus sentimientos con un amigo, familiar o consejero puede ser reconfortante. A veces, simplemente hablar sobre lo que te aflige puede aliviar la carga emocional.\n\n💡 Realiza actividades que te gusten: Aunque puedas sentirte sin energía, intenta hacer actividades que normalmente disfrutas."
                t.update()
                
            elif n == 2:
                 t.value = "Puedo notar que estas 😟 TRISTE 😟\n\n Aquí tienes un consejo para lidiar con la tristeza de manera saludable:\n\n💡 Algunas actividades que te recomiendo: Puede ser leer un libro, ver una película, practicar un hobby o dar un paseo en la naturaleza.\n\n💡 Encuentra significado en la tristeza: A veces, la tristeza puede llevar a la reflexión y el crecimiento personal. Pregúntate si hay lecciones que puedas aprender de esta emoción."
                 t.update()
                
        
        elif surprised:
            n = rand.randint(1,2)
            if n == 1:
                t.value ="Te sientes 😱 SORPRENDIDO 😱\n\nLa emoción del asombro es una sensación de sorpresa, maravilla o admiración profunda ante algo inesperado, extraordinario o impresionante.\n\n 💡Reflexiona: Piensa en por qué esta experiencia te asombra. ¿Qué es lo que encuentras tan especial o impresionante? Reflexionar sobre esto puede aumentar tu aprecio por el momento."
                t.update()
                
            elif n == 2:
                 t.value = "Te sientes 😱 SORPRENDIDO 😱\n\n💡 No te apresures: No te apresures a pasar al siguiente momento. Permítete disfrutar plenamente de la experiencia sin pensar en lo que viene después.\n\n💡 Guarda un recuerdo: Toma una foto o anota tus pensamientos en un diario para que puedas revivir ese momento de asombro en el futuro."
                 t.update()
            
                
        elif neutral:
            n = rand.randint(1,2)
            if n == 1:
                t.value = "Estas bastante 😐 NEUTRAL 😐\n\nTe encuentras en un estado de ánimo equilibrado y sin una respuesta emocional particular. te doy algunos consejos:\n\n💡 Autoconciencia: Reconoce y acepta tus momentos de neutralidad emocional. Es normal experimentar estados emocionales diversos a lo largo del día.\n\n💡 Aceptación: No te sientas presionado para cambiar tu estado emocional en cada momento."
                t.update()
            elif n == 2:
                t.value = "Estas bastante 😐 NEUTRAL 😐\n\nTe encuentras en un estado de ánimo equilibrado y sin una respuesta emocional particular. te doy algunos consejos:\n\n💡 Autoconciencia: Reconoce y acepta tus momentos de neutralidad emocional.\n\n💡 Autocuidado: Aprovecha los momentos de neutralidad para cuidar de ti mismo. Haz ejercicio, medita, come saludablemente y descansa adecuadamente para mantener un equilibrio emocional."
                t.update()
            
           
        else:
            t.value = "Lo siento no reconozco tu emocion, 🧙‍♂️ intentalo de nuevo..."
            t.update()
     
    # Confirm cidalog       
    def yes_click(e):
        page.window_destroy()

    def no_click(e):
        confirm_dialog.open = False
        page.update()
    
    confirm_dialog = AlertDialog(
        modal=True,
        title=Text("Confirmación"),
        content=Text("Quieres salir de la app?"),
        actions=[
            ElevatedButton("Si", on_click=yes_click),
            OutlinedButton("No", on_click=no_click),
        ],
        actions_alignment=MainAxisAlignment.END,
    )
    
    def window_event(e):
        if e.data == "close":
            page.dialog = confirm_dialog
            confirm_dialog.open = True
            page.update()
    
    page.window_prevent_close = True
    page.on_window_event = window_event
    
    # Routes  
    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
        
    def open_menu(e):
        page.go("/menu")
    
    def open_camera(e):
        page.go("/menu/cam")
        
    def open_gallery(e):
        page.go("/menu/gallery")
    
    def open_information(e):
        page.go("/menu/informacion")
        
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)
  
app(target=main)
cap.release
cv2.destroyAllWindows()             