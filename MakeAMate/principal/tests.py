from dateutil.relativedelta import relativedelta
from datetime import date, timedelta, datetime
import json
from tempfile import NamedTemporaryFile
from django.test import Client, TestCase
from django.conf import settings
from django.contrib import auth
from django.utils import timezone
from django.contrib.auth.models import User
from .recommendations import rs_score, BONUS_PREMIUM
from .models import Aficiones, Mate, Tag, Usuario, Piso, Foto
from django.contrib.auth.models import User
from PIL import Image
from io import StringIO
from django.core.files import File
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile



# Tests Sistema de Recomendación
class RecommendationTestCase(TestCase):
    def setUp(self):
        self.user1 = User(id=0,username="us1")
        self.user1.set_password('123')
        self.user2 = User(id=1,username="us2")
        self.user2.set_password('123')
        self.user3 = User(id=2,username="us3")
        self.user3.set_password('123')

        premium_fin = timezone.now()+ relativedelta(months=1)
        self.perfil1 = Usuario(usuario=self.user1,fecha_nacimiento=datetime.now(),lugar="Sevilla",
                            nacionalidad="Española", genero='F',estudios="Informática",fecha_premium=premium_fin)
        self.perfil2 = Usuario(usuario=self.user2,fecha_nacimiento=datetime.now(),lugar="Sevilla",
                            nacionalidad="Española", genero='F',estudios="Informática")
        self.perfil3 = Usuario(usuario=self.user3,fecha_nacimiento=datetime.now(),lugar="Sevilla",
                            nacionalidad="Española", genero='F',estudios="Informática")
        
        tag1 = Tag(etiqueta="No fumador")
        tag2 = Tag(etiqueta="Mascotas")

        af1 = Aficiones(opcionAficiones="Futbol")
        af2 = Aficiones(opcionAficiones="Lolango")

        tag1.save()
        tag2.save()
        af1.save()
        af2.save()
        self.user1.save()
        self.user2.save()
        self.user3.save()
        self.perfil1.save()
        self.perfil2.save()
        self.perfil3.save()

        self.perfil1.tags.add(tag1)
        self.perfil1.aficiones.add(af1)  
        self.perfil2.tags.add(tag1)
        self.perfil2.aficiones.add(af1)
        self.perfil3.tags.add(tag2)
        self.perfil3.aficiones.add(af2)

        self.perfil1.save()
        self.perfil2.save()
        self.perfil3.save()

    def test_perfect_score(self):
        score = rs_score(self.perfil1,self.perfil2)

        self.assertEqual(score,1.0)

    def test_perfect_score_premium(self):
        score = rs_score(self.perfil2,self.perfil1)

        self.assertEqual(score,1.0*BONUS_PREMIUM)

    def test_no_score(self):
        score = rs_score(self.perfil3,self.perfil1)

        self.assertEqual(score,0.0)

    def test_recommendation(self):
        self.client.login(username='us1', password='123')

        response=self.client.get('/')

        self.assertEqual(list(response.context['usuarios'])[0], self.perfil2)
        self.assertEqual(response.status_code, 200)

# Tests mates
class MateTestCase(TestCase):
    def setUp(self):

        self.user1 = User(id=0,username="us1")
        self.user1.set_password('123')
        self.user2 = User(id=1,username="us2")
        self.user2.set_password('123')
        self.user3 = User(id=2,username="us3")
        self.user3.set_password('123')
        self.user4 = User(id=3,username="us4")
        self.user4.set_password('123')
        self.user5 = User(id=4,username="us5")
        self.user5.set_password('123')

        piso1 = Piso.objects.create(zona="Calle Marqués Luca de Tena 3", descripcion="Descripción de prueba 2")
        piso2 = Piso.objects.create(zona="Calle Marqués Luca de Tena 3", descripcion="Descripción de prueba 2")


        tfn1 = "+34666777111"
        tfn2 = "+34666777222"
        tfn3 = "+34666777333"
        perfil1 = Usuario(usuario=self.user1,fecha_nacimiento="2000-1-1",lugar="Sevilla",nacionalidad="Española",
                            genero='F',estudios="Informática", telefono = tfn1, sms_validado=True)
        perfil2 = Usuario(usuario=self.user2,fecha_nacimiento="2000-1-1",lugar="Sevilla",nacionalidad="Española",
                            genero='F',estudios="Informática", telefono = tfn2, sms_validado=True)
        perfil3 = Usuario(usuario=self.user3,fecha_nacimiento="2000-1-1",lugar="Sevilla",nacionalidad="Española",
                            genero='F',estudios="Informática", telefono = tfn3, sms_validado=True)
        
    
        mate = Mate(userEntrada=self.user3, userSalida=self.user1, mate=True)
        mate1 = Mate(userEntrada=self.user2, userSalida=self.user1, mate=True)

        self.user1.save()
        self.user2.save()
        self.user3.save()
        self.user4.save()
        self.user5.save()
        piso1.save()
        piso2.save()
        perfil1.save()
        perfil2.save()
        perfil3.save()
        perfil4.save()
        perfil5.save()
        mate1.save()
        mate2.save()

    def test_accept_mate(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 1}
        response = self.client.post('/accept-mate/', data, format='json')
        json_resp = json.loads(response.content)
        mate = Mate.objects.get(userEntrada=self.user1, userSalida=self.user2)

        self.assertTrue(mate.mate)
        self.assertTrue(json_resp['success'])
        self.assertFalse(json_resp['mate_achieved'])


    def test_reject_mate(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 1}
        response = self.client.post('/reject-mate/', data, format='json')
        json_resp = json.loads(response.content)
        mate = Mate.objects.get(userEntrada=self.user1, userSalida=self.user2)

        self.assertFalse(mate.mate)
        self.assertTrue(json_resp['success'])

    def test_mate_achieved(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 2}
        response = self.client.post('/accept-mate/', data, format='json')
        json_resp = json.loads(response.content)
        mate = Mate.objects.get(userEntrada=self.user1, userSalida=self.user3)

        self.assertTrue(mate.mate)
        self.assertTrue(json_resp['success'])
        self.assertTrue(json_resp['mate_achieved'])

    def test_accept_mate_self(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 0}
        response = self.client.post('/accept-mate/', data, format='json')
        json_resp = json.loads(response.content)

        self.assertFalse(json_resp['success'])

    def test_reject_mate_self(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 0}
        response = self.client.post('/reject-mate/', data, format='json')
        json_resp = json.loads(response.content)

        self.assertFalse(json_resp['success'])

    def test_accept_not_same_city(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 4}
        response = self.client.post('/accept-mate/', data, format='json')
        json_resp = json.loads(response.content)

        self.assertFalse(json_resp['success'])

    def test_reject_not_same_city(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 4}
        response = self.client.post('/reject-mate/', data, format='json')
        json_resp = json.loads(response.content)

        self.assertFalse(json_resp['success'])

    def test_accept_rejected_mate(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 3}
        response = self.client.post('/accept-mate/', data, format='json')
        json_resp = json.loads(response.content)

        self.assertFalse(json_resp['success'])
        

    def test_reject_rejected_mate(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 3}
        response = self.client.post('/reject-mate/', data, format='json')
        json_resp = json.loads(response.content)

        self.assertFalse(json_resp['success'])

    def test_accept_already_mated(self):
        self.client.login(username='us4', password='123')

        data = {'id_us': 0}
        response = self.client.post('/accept-mate/', data, format='json')
        json_resp = json.loads(response.content)

        self.assertFalse(json_resp['success'])

    def test_reject_already_mated(self):
        self.client.login(username='us3', password='123')

        data = {'id_us': 0}
        response = self.client.post('/reject-mate/', data, format='json')
        json_resp = json.loads(response.content)

        self.assertFalse(json_resp['success'])

    def test_accept_both_pisos(self):
        self.client.login(username='us4', password='123')

        data = {'id_us': 2}
        response = self.client.post('/accept-mate/', data, format='json')
        json_resp = json.loads(response.content)

        self.assertFalse(json_resp['success'])

    def test_reject_both_pisos(self):
        self.client.login(username='us3', password='123')

        data = {'id_us': 3}
        response = self.client.post('/reject-mate/', data, format='json')
        json_resp = json.loads(response.content)

        self.assertFalse(json_resp['success'])

    def test_accept_mate_inexistent_user(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 100}
        response = self.client.post('/accept-mate/', data, format='json')

        self.assertEquals(response.status_code,404)

    def test_reject_mate_inexistent_user(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 100}
        response = self.client.post('/reject-mate/', data, format='json')

        self.assertEquals(response.status_code,404)

    def test_accept_mate_not_logged(self):
        data = {'id_us': 0}
        response = self.client.post('/accept-mate/', data, format='json')
    
        self.assertEquals(response.status_code,302)
        self.assertRedirects(response,"/login/", target_status_code=200)

    def test_reject_mate_not_logged(self):
        data = {'id_us': 0}
        response = self.client.post('/reject-mate/', data, format='json')
    
        self.assertEquals(response.status_code,302)
        self.assertRedirects(response,"/login/", target_status_code=200)
  
class FiltesTests(TestCase):
    
    def setUp(self):
         super().setUp()
    
    @classmethod
    def setUpTestData(cls):
        userPepe= User(username="Pepe")
        userPepe.set_password("asdfg")
        userPepe.save()

        userMaria=User(username="Maria")
        userMaria.set_password("asdfg")
        userMaria.save()

        userSara=User(username="Sara")
        userSara.set_password("asdfg")
        userSara.save()


        tfn1 = "+34666777111"
        tfn2 = "+34666777222"
        tfn3 = "+34666777333"
        self.userPepa=User(username="Pepa")
        self.userPepa.set_password("asdfg")
        self.userPepa.save()

        self.userJuan=User(username="Juan")
        self.userJuan.set_password("asdfg")
        self.userJuan.save()

        etiquetas= Tag.objects.create(etiqueta="No fumador")
        aficion= Aficiones.objects.create(opcionAficiones="Deportes")
    
        piso_maria = Piso.objects.create(zona="Calle Marqués Luca de Tena 3", descripcion="Descripción de prueba 2")
        piso_sara = Piso.objects.create(zona="Calle Marqués Luca de Tena 5", descripcion="Descripción de prueba 3")


        Pepe= Usuario.objects.create(usuario=userPepe, fecha_nacimiento=date(2000,12,31),lugar="Sevilla", telefono=tfn1, sms_validado=True)
        Maria=Usuario.objects.create(usuario=userMaria, fecha_nacimiento=date(2000,12,30),lugar="Sevilla", piso=piso_maria, telefono=tfn2, sms_validado=True)
        Sara= Usuario.objects.create(usuario=userSara,fecha_nacimiento=date(2000,12,29),lugar="Cádiz", piso=piso_sara, telefono=tfn3, sms_validado=True)

        




    # Nos logeamos como Pepe usuario sin Piso en Sevilla y 
    # comprobamos que solo nos sale 1 usuario, que es el que esta en la misma ciudad
    def test_filter_(self):
        Pepe= Usuario.objects.create(usuario=self.userPepe, fecha_nacimiento=date(2000,12,31),lugar="Sevilla")
        Maria=Usuario.objects.create(usuario=userMaria, fecha_nacimiento=date(2000,12,30),lugar="Sevilla", piso=piso_maria)
        Sara= Usuario.objects.create(usuario=userSara,fecha_nacimiento=date(2000,12,29),lugar="Cádiz", piso=piso_sara)
        Pepa=Usuario.objects.create(usuario=self.userPepa, fecha_nacimiento=date(2000,12,28), lugar="Sevilla")
        Juan=Usuario.objects.create(usuario=self.userJuan, fecha_nacimiento=date(2000,12,27), lugar ="Sevilla")
    
    

   #Nos logeamos como Pepe usuario sin Piso en Sevilla y 
   # comprobamos que solo nos sale 1 usuario, que es el que esta en la misma ciudad
    def test_filter_piso_y_ciudad(self):
        c= Client()
        login= c.login(username='Pepe', password= 'asdfg')
        response=c.get('/')

        self.assertTrue( len(response.context['usuarios']) == 3)
        self.assertEqual(response.status_code, 200)
    

    #Nos logeamos como Pepe usuario sin Piso en Sevilla y 
    #comprobamos que efectivamente no salen 2 usuarios ya que uno de ellos no vive en la misma ciudad
    def test_filter_error(self):
        c= Client()
        c.login(username='Pepe', password= 'asdfg')
        response=c.get('/')
        self.assertFalse( len(response.context['usuarios']) == 4)
        self.assertEqual(response.status_code, 200)

    def test_filter_rejected_mate(self):
        c= Client()
        c.login(username='Pepe', password= 'asdfg')
        response=c.get('/')
        #Comprombamos que antes de rechazar a un usuario nos salen 3 en total
        self.assertTrue( len(response.context['usuarios']) == 3)
        mate=Mate.objects.create(userEntrada=self.userPepe, userSalida=self.userPepa, mate=False)
        response=c.get('/')
        #Comprobamos que tras rechazar a un usuario ese ya no nos aparece como usuario recomendado
        self.assertTrue( len(response.context['usuarios']) == 2)

    def test_filter_accepted_mate(self):
        c= Client()
        c.login(username='Pepe', password= 'asdfg')
        response=c.get('/')
        #Comprombamos que antes de hacer mate con un usuario nos salen 3 en total
        self.assertTrue( len(response.context['usuarios']) == 3)
        mate=Mate.objects.create(userEntrada=self.userPepe, userSalida=self.userJuan, mate=True)
        response=c.get('/')
        #Comprobamos que tras hacer mate con un usuario ese ya no nos aparece como usuario recomendado
        self.assertTrue( len(response.context['usuarios']) == 2)
    


#Test de login
class LoginTest(TestCase):
    def setUp(self):
        user = User(username='usuario')
        user.set_password('qwery')
        tfn = "+34666777444"
        piso = Piso.objects.create(zona="Calle Marqués Luca de Tena 3", descripcion="Descripción de prueba 2")
        perfil = Usuario(usuario=user,piso=piso,fecha_nacimiento="2000-1-1",lugar="Sevilla",nacionalidad="Española",
                genero='F',estudios="Informática", telefono=tfn, sms_validado=True)
        user.save()
        perfil.save()
        super().setUp()


    #Test de inicio de sesión con un usuario existente
    def test_login_positive(self):
        c = Client()
        response = c.post('/login/', {'username': 'usuario', 'pass': 'qwery'})
        user = auth.get_user(c)
        self.assertTrue(user.is_authenticated)
        self.assertRedirects(response, '/', status_code=302, 
        target_status_code=200, fetch_redirect_response=True)


    #Test de inicio de sesión con un usuario inexistente
    def test_login_negative(self):
        c = Client()
        response = c.post('/login/', {'username': 'inexistente', 'pass': 'inexistente'})
        user = auth.get_user(c)
        self.assertFalse(user.is_authenticated)

class NotificacionesTest(TestCase):

    def setUp(self):
        user = User(username='usuario')
        user.set_password('qwery')
        user.save()

        user2 = User(username='usuario2')
        user2.set_password('qwery')
        user2.save()

        user3 = User(username='usuario3')
        user3.set_password('qwery')
        user3.save()

        tfn1 = "+34666777666"
        tfn2 = "+34666777777"
        tfn3 = "+34666777888"
        piso_pepe = Piso.objects.create(zona="Calle Marqués Luca de Tena 1", descripcion="Descripción de prueba 1")   
        piso_maria = Piso.objects.create(zona="Calle Marqués Luca de Tena 3", descripcion="Descripción de prueba 2")
        piso_sara = Piso.objects.create(zona="Calle Marqués Luca de Tena 5", descripcion="Descripción de prueba 3")
        
        fecha_premium=timezone.now() + timedelta(days=120)
        pepe= Usuario.objects.create(usuario=user, piso=piso_pepe, fecha_nacimiento=date(2000,12,31),lugar="Sevilla", telefono=tfn1, sms_validado=True,fecha_premium=fecha_premium)
        maria=Usuario.objects.create(usuario=user2, piso=piso_maria, fecha_nacimiento=date(2000,12,30),lugar="Sevilla", telefono=tfn2, sms_validado=True)
        sara= Usuario.objects.create(usuario=user3, piso=piso_sara,fecha_nacimiento=date(2000,12,29),lugar="Cádiz",telefono=tfn3, sms_validado=True)

        #MATE ENTRE user y user2
        mate12 = Mate.objects.create(mate=True,userEntrada=user, userSalida=user2)
        mate21 = Mate.objects.create(mate=True,userEntrada=user2, userSalida=user)

        #EL user3 LE DA LIKE al user1 y al user 2
        like31 = Mate.objects.create(mate=True,userEntrada=user3, userSalida=user)
        like32= Mate.objects.create(mate=True,userEntrada=user3, userSalida=user2)
        super().setUp()


    #El usuario "user" tiene un mate y como es premium tb tiene un like, la lista será de tamaño 2
    def test_notificaciones_premium(self):
        c = Client()
        response_user = c.post('/login/', {'username': 'usuario', 'pass': 'qwery'})
        response2 = c.get('/')
        lista_mates = response2.context['notificaciones']

        self.assertTrue(len(lista_mates) == 2)
        
    #El usuario "user2" tiene un mate y un like, la lista será de tamaño 1 porque al no ser premium el like
    #no se le notifica
    def test_notificaciones_no_premium(self):
        c = Client()
        response = c.post('/login/', {'username': 'usuario2', 'pass': 'qwery'})
        response2 = c.get('/')
        lista_mates = response2.context['notificaciones']
        self.assertTrue(len(lista_mates) == 1)
    
    #El usuario "user3" no tiene ningún mate ni like, por lo que su lista de mates será de tamaño 0
    def test_notificaciones_false(self):
        c = Client()
        response = c.post('/login/', {'username': 'usuario3', 'pass': 'qwery'})
        response2 = c.get('/')
        lista_mates = response2.context['notificaciones']
        self.assertTrue(len(lista_mates) == 0)


def create_image(storage, filename, size=(100, 100), image_mode='RGB', image_format='PNG'):

        data = BytesIO()
        Image.new(image_mode, size).save(data, image_format)
        data.seek(0)
        if not storage:
            return data
        image_file = ContentFile(data.read())
        return storage.save(filename, image_file)
    

class RegistroTest(TestCase):

    def setUp(self):
        

        Tag.objects.create(etiqueta='etiqueta1')
        Tag.objects.create(etiqueta='etiqueta2')
        Tag.objects.create(etiqueta='etiqueta3')


        Aficiones.objects.create(opcionAficiones='Aficion1')
        Aficiones.objects.create(opcionAficiones='Aficion2')
        Aficiones.objects.create(opcionAficiones='Aficion3')

        avatar = create_image(None, 'avatar.png')
        avatar_file = SimpleUploadedFile('front.png', avatar.getvalue())


        self.data = {
            'username':'usuariotest',
            'password':'passwordtest1',
            'password2': 'passwordtest1',
            'nombre': 'nombreprueba',
            'apellidos':'apellidosprueba',
            'correo':'prueba@gmail.com',
            'piso_encontrado': True,
            'zona_piso':'Ejemplo de zona',
            'telefono_usuario':'+34666777888',
            'foto_usuario': avatar_file,
            'fecha_nacimiento':'01-01-2000',
            'lugar':'Ejemplo de lugar',
            'nacionalidad':'Ejemplo',
            'genero':'M',
            'tags': [t.id for t in Tag.objects.all()],
            'aficiones': [a.id for a in Aficiones.objects.all()],
            'terminos': True
        }

        super().setUp()

    def test_register_positive(self):
        c = Client()
        response = c.post('/register/', self.data)
        existe_usuario = Usuario.objects.filter(telefono=self.data['telefono_usuario']).exists()
        self.assertTrue(response.status_code == 302)
        self.assertTrue(existe_usuario)
        Usuario.objects.all().delete()
        User.objects.all().delete() 

    def test_username_already_exists(self):
        c = Client()
        response = c.post('/register/', self.data)
        self.data['correo'] = "correonuevo@gmail.com"
        self.data['telefono_usuario'] = "+34666777333"
        response2 = c.post('/register/', self.data)
        num_usuarios = Usuario.objects.all().count()
        self.assertTrue(num_usuarios == 1)
        Usuario.objects.all().delete()
        User.objects.all().delete() 

    def test_different_passwords(self):
        c = Client()
        self.data['password'] = "password01"
        self.data['password2'] = "password02"
        response = c.post('/register/', self.data)
        num_usuarios = Usuario.objects.all().count()
        self.assertTrue(num_usuarios == 0)
        error = response.context['form'].errors['password2'][0]
        self.assertTrue(error == "Las contraseñas no coinciden")
        Usuario.objects.all().delete()
        User.objects.all().delete() 

    def test_email_already_exists(self):
        c = Client()
        response = c.post('/register/', self.data)
        self.data['username'] = "NewUsername"
        self.data['telefono_usuario'] = "+34666111222"
        avatar = create_image(None, 'avatar.png')
        avatar_file = SimpleUploadedFile('front.png', avatar.getvalue())
        self.data['foto_usuario'] = avatar_file
        response2 = c.post('/register/', self.data)
        num_usuarios = Usuario.objects.all().count()
        self.assertTrue(num_usuarios == 1)
        error = response2.context['form'].errors['correo'][0]
        self.assertTrue(error == "La dirección de correo electrónico ya está en uso")
        Usuario.objects.all().delete()
        User.objects.all().delete()

    def test_phone_number_already_exists(self):
        c = Client()
        response = c.post('/register/', self.data)
        self.data['username'] = "NewUsername"
        self.data['correo'] = "newEmail@gmail.com"
        avatar = create_image(None, 'avatar.png')
        avatar_file = SimpleUploadedFile('front.png', avatar.getvalue())
        self.data['foto_usuario'] = avatar_file
        response2 = c.post('/register/', self.data)
        num_usuarios = Usuario.objects.all().count()
        self.assertTrue(num_usuarios == 1)
        error = response2.context['form'].errors['telefono_usuario'][0]
        self.assertTrue(error == "El teléfono ya está en uso")    
        Usuario.objects.all().delete()
        User.objects.all().delete()

    def test_select_at_least_three_tags(self):
        c = Client()
        tags = self.data['tags'][0:2]
        self.data['tags'] = tags
        response = c.post('/register/', self.data)
        num_usuarios = Usuario.objects.all().count()
        error = response.context['form'].errors['tags'][0]
        self.assertTrue(num_usuarios == 0)
        self.assertTrue(error == "Por favor, elige al menos tres etiquetas que te definan")

    def test_select_at_least_three_aficiones(self):
        c = Client()
        aficiones = self.data['aficiones'][0:2]
        self.data['aficiones'] = aficiones
        response = c.post('/register/', self.data)
        num_usuarios = Usuario.objects.all().count()
        error = response.context['form'].errors['aficiones'][0]
        self.assertTrue(num_usuarios == 0)
        self.assertTrue(error == "Por favor, elige al menos tres aficiones que te gusten")




